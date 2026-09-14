# Weave 0.3.2 — entity-level semantic merge driver (Rust binary, Ataraxy-Labs).
# Version pinned per docs/plans/weave-integration.md §2 "Pin hard" constraint.
# Upstream had v0.3.3 latest as of 2026-05-18; 0.3.2 is the version whose CLI /
# exit-code / marker behaviour the plan verified — do not bump without re-recon.
#
# Install is path-based only (`cargo install --path crates/weave-driver`); there
# is no crates.io publish, so the builder stage clones the repo at the v0.3.2 tag.
#
# Multi-stage mirrors docker/mergiraf/Dockerfile: build with rust:1-bookworm,
# copy the binary to a debian:bookworm-slim runtime. Builder and runtime are
# both bookworm to guarantee a matched GLIBC.
#
# Invoked as a git-style three-way driver (positional, mutates OURS in place):
#   weave-driver <base> <ours> <theirs>
# Exit codes: 0 = clean, 1 = conflict (markers written into <ours>), other = crash.
# (Upstream README documents the git merge-driver form `weave-driver %O %A %B`.)

FROM rust:1-bookworm AS builder
ARG WEAVE_VERSION=0.3.2
RUN apt-get update \
 && apt-get install -y --no-install-recommends git pkg-config libssl-dev ca-certificates \
 && rm -rf /var/lib/apt/lists/*
RUN git clone --depth 1 --branch "v${WEAVE_VERSION}" \
      https://github.com/Ataraxy-Labs/weave.git /src
RUN cargo install --locked --path /src/crates/weave-driver

FROM debian:bookworm-slim
RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates libssl3 \
 && rm -rf /var/lib/apt/lists/*
COPY --from=builder /usr/local/cargo/bin/weave-driver /usr/local/bin/weave-driver
WORKDIR /workspace
ENTRYPOINT ["weave-driver"]
