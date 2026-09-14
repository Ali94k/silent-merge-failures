import json
import logging
import sys
from pathlib import Path

import click
import yaml

logger = logging.getLogger("merge_compare")


def _classify_results(
    results: dict, scenarios: list,
) -> tuple[dict[str, dict[str, tuple]], dict[str, str]]:
    """Classify all tool results against developer resolutions.

    Returns (classifications, categories) where:
        classifications: {scenario_id: {tool_name: (Classification, runtime)}}
        categories: {scenario_id: category}
    """
    from src.evaluation.categorizer import cluster_of
    from src.evaluation.comparator import classify_result

    scenario_map = {s.scenario_id: s for s in scenarios}
    classifications: dict[str, dict[str, tuple]] = {}
    categories: dict[str, str] = {}

    for scenario_id, tool_results in results.items():
        scenario = scenario_map.get(scenario_id)
        if not scenario:
            continue

        classifications[scenario_id] = {}
        # Cluster from the R1 RM2 tags (union of ours/theirs file-level),
        # mirroring the runtime dispatcher. Untagged scenario → "NONE".
        refs = scenario.refactorings or {}
        categories[scenario_id] = cluster_of(
            refs.get("ours", []), refs.get("theirs", [])
        )

        for tool_name, result in tool_results.items():
            cls = classify_result(
                result=result,
                developer_resolution=scenario.developer_resolution,
                base_content=scenario.base_content,
                ours_content=scenario.ours_content,
                theirs_content=scenario.theirs_content,
            )
            classifications[scenario_id][tool_name] = (cls, result.runtime_seconds)

    return classifications, categories


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
def cli(verbose: bool):
    """Merge Tool Comparison Framework."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stderr,
    )


@cli.command()
@click.option(
    "--config", default="config/repos.yaml", help="Path to repos config file"
)
@click.option("--output", default="data/scenarios", help="Output directory for scenarios")
@click.option("--max-scenarios", type=int, default=None, help="Max scenarios per repo")
def collect(config: str, output: str, max_scenarios: int | None):
    """Collect merge scenarios from real-world Java repos."""
    from src.data.collector import collect_scenarios

    scenarios = collect_scenarios(
        repos_config_path=config,
        output_dir=output,
        max_scenarios=max_scenarios,
    )
    click.echo(f"Collected {len(scenarios)} scenarios to {output}/")


@cli.command()
@click.option(
    "--tools-config", default="config/tools.yaml", help="Path to tools config file"
)
@click.option("--scenarios-dir", default="data/scenarios", help="Scenarios directory")
@click.option("--results-dir", default="data/results", help="Results output directory")
def run(tools_config: str, scenarios_dir: str, results_dir: str):
    """Run all enabled merge tools on collected scenarios."""
    from src.core.plugin_loader import load_tools_from_config
    from src.core.runner import ComparisonRunner
    from src.data.collector import load_scenarios

    tools = load_tools_from_config(tools_config)
    scenarios = load_scenarios(scenarios_dir)

    if not scenarios:
        click.echo("No scenarios found. Run 'collect' first.", err=True)
        return

    click.echo(f"Running {len(tools)} tools on {len(scenarios)} scenarios...")
    runner = ComparisonRunner(tools=tools, scenarios=scenarios, results_dir=results_dir)
    results = runner.run_all()
    click.echo(f"Done. Results saved to {results_dir}/")


@cli.command()
@click.option("--results-dir", default="data/results", help="Results directory")
@click.option("--scenarios-dir", default="data/scenarios", help="Scenarios directory")
def evaluate(results_dir: str, scenarios_dir: str):
    """Evaluate merge tool results against developer resolutions."""
    from src.core.runner import load_results
    from src.data.collector import load_scenarios
    from src.evaluation.metrics import compute_metrics
    from src.evaluation.report import to_table

    results = load_results(results_dir)
    scenarios = load_scenarios(scenarios_dir)

    if not results:
        click.echo("No results found. Run 'run' first.", err=True)
        return

    classifications, categories = _classify_results(results, scenarios)
    metrics = compute_metrics(classifications, categories)
    click.echo(to_table(metrics))


@cli.command()
@click.option("--results-dir", default="data/results", help="Results directory")
@click.option("--scenarios-dir", default="data/scenarios", help="Scenarios directory")
@click.option(
    "--format", "formats", multiple=True,
    default=["console"],
    help="Output formats: console, csv, json, latex, per-scenario, charts "
         "(charts needs the viz extra: pip install -e .[viz])"
)
@click.option("--output-dir", default="reports", help="Report output directory")
def report(results_dir: str, scenarios_dir: str, formats: tuple[str], output_dir: str):
    """Generate comparison reports in various formats."""
    from src.core.runner import load_results
    from src.data.collector import load_scenarios
    from src.evaluation.metrics import compute_metrics
    from src.evaluation.report import generate_report

    results = load_results(results_dir)
    scenarios = load_scenarios(scenarios_dir)

    if not results:
        click.echo("No results found. Run 'run' first.", err=True)
        return

    classifications, categories = _classify_results(results, scenarios)
    metrics = compute_metrics(classifications, categories)
    outputs = generate_report(metrics, list(formats), output_dir,
                              classifications=classifications)

    if "console" in outputs:
        click.echo(outputs["console"])

    for fmt in formats:
        if fmt != "console":
            click.echo(f"Wrote {fmt} report to {output_dir}/")


@cli.command(name="load-dataset")
@click.option("--dataset-path", default=None, help="Path to dataset dir (overrides config)")
@click.option("--dataset-config", default="config/datasets.yaml", help="Dataset config file")
@click.option("--output", default="data/scenarios", help="Output directory for scenarios")
@click.option("--max-scenarios", type=int, default=None, help="Max scenarios to load")
@click.option("--filter-repos", multiple=True, default=None, help="Only load from these repos (owner/name)")
@click.option("--force", is_flag=True, default=False, help="Re-extract even if cached")
def load_dataset(
    dataset_path: str | None,
    dataset_config: str,
    output: str,
    max_scenarios: int | None,
    filter_repos: tuple[str],
    force: bool,
):
    """Load merge scenarios from the Schesch et al. (ASE 2024) dataset."""
    import json as json_mod

    from src.data.schesch_loader import ScheschDatasetLoader

    # Resolve dataset path and defaults from config
    if dataset_path is None or max_scenarios is None or not filter_repos:
        config_path = Path(dataset_config)
        if config_path.exists():
            cfg = yaml.safe_load(config_path.read_text()).get("datasets", {}).get("schesch2024", {})
            if dataset_path is None:
                dataset_path = cfg.get("path", "data/schesch-dataset")
            if max_scenarios is None:
                max_scenarios = cfg.get("max_scenarios")
            if not filter_repos:
                filter_repos = tuple(cfg.get("filter_repos") or [])

    # Check dataset exists
    if not Path(dataset_path).exists():
        click.echo(
            f"Error: Dataset directory not found at '{dataset_path}'.\n"
            f"Download from:\n"
            f"  Zenodo:  https://zenodo.org/records/13366866\n"
            f"  GitHub:  https://github.com/benedikt-schesch/AST-Merging-Evaluation\n"
            f"Then place it at '{dataset_path}' or use --dataset-path.",
            err=True,
        )
        raise SystemExit(1)

    loader = ScheschDatasetLoader(dataset_path=dataset_path)
    repos = list(filter_repos) if filter_repos else None
    scenarios = loader.load(max_scenarios=max_scenarios, filter_repos=repos)

    output_path = Path(output)
    output_path.mkdir(parents=True, exist_ok=True)

    new_count = 0
    cached_count = 0
    for scenario in scenarios:
        scenario_file = output_path / f"{scenario.scenario_id}.json"
        if scenario_file.exists() and not force:
            cached_count += 1
        else:
            scenario_file.write_text(json_mod.dumps(scenario.to_dict(), indent=2))
            new_count += 1

    total = new_count + cached_count
    click.echo(f"Loaded {new_count} new, {cached_count} cached ({total} total) to {output}/")


@cli.command(name="all")
@click.option("--source", type=click.Choice(["dataset", "collect"]), default="dataset",
              help="Data source: 'dataset' for Schesch, 'collect' for repo mining")
@click.option("--dataset-path", default=None, help="Path to dataset (overrides config)")
@click.option("--dataset-config", default="config/datasets.yaml")
@click.option("--repos-config", default="config/repos.yaml")
@click.option("--tools-config", default="config/tools.yaml")
@click.option("--max-scenarios", type=int, default=None)
@click.pass_context
def run_all(ctx, source: str, dataset_path: str | None, dataset_config: str,
            repos_config: str, tools_config: str, max_scenarios: int | None):
    """Run full pipeline: load data -> run tools -> evaluate -> report."""
    if source == "dataset":
        ctx.invoke(load_dataset, dataset_path=dataset_path,
                   dataset_config=dataset_config, max_scenarios=max_scenarios)
    else:
        ctx.invoke(collect, config=repos_config, max_scenarios=max_scenarios)
    ctx.invoke(run, tools_config=tools_config)
    ctx.invoke(evaluate)
    ctx.invoke(report, formats=("console", "csv", "json", "latex"))


if __name__ == "__main__":
    cli()
