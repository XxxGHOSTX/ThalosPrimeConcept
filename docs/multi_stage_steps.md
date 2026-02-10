# Thalos Prime: Multi-Stage Execution Steps

Use this checklist to run Thalos Prime workflows in discrete, auditable stages.

## Stage 1 — Frame the Objective
- Author a Human Directive Record (HDR) with objectives, constraints, and success criteria.
- Sign the HDR (use `generate_keypair` + `HumanDirectiveRecord.sign`) to bind provenance.

## Stage 2 — Model the Plan
- Encode the workflow as an Execution Graph or `pipeline.yaml` (tasks, dependencies, parameters).
- Attach task functions (simulation, reasoning, discovery) and validate the graph is acyclic.

## Stage 3 — Configure Discovery
- Select Library of Babel search strategy (exact | fragments | n-gram | inversion).
- Set coherence thresholds, cache sizing, and desired book size/export format.
- Optionally warm the cache with `DiscoveryEngine.get_page` for known addresses.

## Stage 4 — Execute Safely
- Run the graph through the Orchestrator inside the Simulation Sandbox.
- Enforce sandbox limits (timeouts, resource guards); capture stdout/stderr as artifacts.
- Track task start/end times and statuses for reproducibility.

## Stage 5 — Reason and Iterate
- Apply Hybrid Reasoning rules over artifacts and knowledge space embeddings.
- Refine prompts/parameters and re-run affected subgraphs only (dependency-aware).

## Stage 6 — Preserve Provenance
- Capture outputs as `Artifact`s; link them into `ProvenanceRecord`s and chains.
- Export assembled Babel books and HDR-bound results for downstream review.

## Stage 7 — Serve and Integrate
- Expose Discovery API endpoints (`post_search`, `get_page`, `post_assemble`, `get_book`).
- Wrap with your chatbot/UI layer; stream intermediate statuses from the graph for transparency.
