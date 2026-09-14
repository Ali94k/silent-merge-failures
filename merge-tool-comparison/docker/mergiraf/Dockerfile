# Mergiraf 0.17.0 — syntax-aware merge driver (Rust binary).
# Version pinned in docs/plans/mergiraf-integration-recon.md.
# Diverges from Schesch upstream's 0.4.0 pin (user override 2026-05-12 —
# Homebrew bottles 0.17.0; M3 option 3i must account for the skew).
#
# Multi-stage: build with rust:1-bookworm, copy binary to debian:bookworm-slim runtime.
# (Builder and runtime both bookworm — guarantees matched GLIBC. Earlier rust:1-slim
# defaulted to trixie/GLIBC 2.39, broke the binary on bookworm/GLIBC 2.36 runtime.)
# Invoked via standalone three-file CLI:
#   mergiraf merge BASE LEFT RIGHT -p PATH
# Exit codes: 0 = clean, 1 = conflict (markers written to stdout), other = crash.

FROM rust:1-bookworm AS builder
ARG MERGIRAF_VERSION=0.17.0
RUN apt-get update \
 && apt-get install -y --no-install-recommends pkg-config libssl-dev ca-certificates \
 && rm -rf /var/lib/apt/lists/*
RUN cargo install --locked mergiraf --version "${MERGIRAF_VERSION}"

FROM debian:bookworm-slim
RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates libssl3 \
 && rm -rf /var/lib/apt/lists/*
COPY --from=builder /usr/local/cargo/bin/mergiraf /usr/local/bin/mergiraf
WORKDIR /workspace
ENTRYPOINT ["mergiraf", "merge"]
