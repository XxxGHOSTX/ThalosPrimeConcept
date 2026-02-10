# Thalos Prime — Discovery Execution Engine

Purpose: Formalize human-directed discovery via HDR-anchored execution graphs, hybrid reasoning, and immutable provenance.

Goals: reproducible discoverability, patentable capture of human inventorship, safe in-silico experimentation.

Quickstart:
1. Submit HDR via `POST /hdr` (signed).
2. Upload `pipeline.yaml` to `/pipelines`.
3. Run `POST /run` with `hdr_id` + `pipeline_id`.
4. Retrieve artifacts: `GET /run/{id}/artifacts`.

Security: All HDR payloads must be cryptographically signed. System enforces "no_wetlab" filter by default.

See `docs/spec.md` for the full specification, claims, and provenance examples. The evidence-first prompt template lives at `reasoner/prompt_templates/evidence_first.tpl`.
