# Thalos Prime — Human-Directed Automated Discovery Specification

## Maximum Definitions (precise)

- **Human Direction Record (HDR):** timestamped, signed record of human-provided objectives, constraints, assumptions, success criteria, and chosen parameters.
- **Execution Graph (EG):** a directed acyclic graph of discrete tasks (nodes) and data dependencies (edges) that the orchestrator executes.
- **Artifact:** any digital output (code, model, simulation result, claim draft) produced by a pipeline step. Each Artifact has a unique Artifact ID and metadata.
- **Provenance Record (PR):** immutable chain linking artifacts to inputs, HDRs, pipeline versions, container images, and signer(s).
- **Knowledge Space:** combined storage of vectorized passages, a knowledge graph of entities/triples, and raw documents.
- **Hypothesis Object:** structured representation containing candidate claim text, supporting evidence references, confidence score, and recommended next action.

## Formal system description (claims-grade language / method steps)

### Independent claim (high level)

A computerized method for human-directed automated discovery, the method comprising:

a. receiving, from a human operator, a Human Direction Record (HDR) that includes at least one objective, constraints, and a set of permitted exploration domains;

b. constructing a Knowledge Space by ingesting and normalizing heterogeneous digital sources, indexing text into vector embeddings, and populating a knowledge graph of entities and relations, wherein each ingested element is stored with provenance metadata;

c. generating, by a hybrid reasoning engine that combines symbolic graph traversal and language-model-based synthesis, one or more Hypothesis Objects relevant to the HDR;

d. ranking said Hypothesis Objects by an evidence score computed from provenance-weighted similarity metrics and deterministic filters defined by the HDR;

e. executing one or more Evaluation Jobs for selected Hypothesis Objects in an isolated simulation sandbox, wherein each Evaluation Job is executed according to an Execution Graph and produces one or more Artifacts; and

f. recording a Provenance Record that links the HDR, Knowledge Space sources, Execution Graph steps, and resultant Artifacts into an immutable chain for subsequent human review and legal attribution.

### Dependent claims (examples)

1. The method of claim 1 where constructing the Knowledge Space further comprises storing vector embeddings in a vector database and triples in a graph database, and storing raw documents in object storage.
2. The method of claim 1 where the hybrid reasoning engine filters candidate hypotheses with deterministic rule predicates prior to language model synthesis.
3. The method of claim 1 where the Evidence Score is a weighted sum of (i) provenance depth, (ii) cross-domain co-occurrence, (iii) simulation consistency, and (iv) human validation signals.
4. The method of claim 1 where each HDR is cryptographically signed and appended to an immutable append-only ledger.

## System architecture (textual diagram)

Components (logical), with arrows showing flows (→):

- Human Operator UI / CLI / API
- ↓ (submit HDR)
- Intent Formalizer → Execution Orchestrator (Core Engine)
- ↙ ↘
- Knowledge Ingest/Normalizer → Knowledge Layer (Vector DB + Graph DB + Raw Storage)
- ↘ ↙
- Hybrid Reasoner (Symbolic + LLM) → Candidate Hypotheses → Ranker → Selection
- ↓
- Simulation Sandbox (isolated compute; non-wetlab simulations only) → Evaluation Artifacts
- ↓
- Provenance Store (append-only ledger + artifact registry) ← Artifact Signer
- ↓
- Reviewer UI / Patent Packager / Exporter

## Data models (concise schemas)

**Document (canonical)**

- id: uuid
- source: url|git|doi|upload
- type: text|pdf|code|dataset
- content_ref: object_storage_path
- embeddings_ref: vector_db_id
- created_at, harvested_at, pipeline_version

**Passage**

- id, document_id, char_start, char_end, text, embeddings_ref

**Entity**

- id, label, type, canonical_uri, aliases

**Triple**

- subject_id, predicate, object_id, source_passage_id, confidence

**Artifact**

- id, type, content_ref, produced_by_pipeline, container_image, code_hash, created_at, signatures

**HDR**

- id, human_id, signed_payload(json), timestamp, hdr_version

**ProvenanceRecord**

- id, artifact_id, inputs[], pipeline_id, pipeline_commit_hash, execution_log_ref, signature

## Execution Graph spec (YAML example)

Provide as `pipeline.yaml`.

```
pipeline_id: example_ingest_reasoner_v1
description: "Ingest README, embed, add to vectorstore, run reasoner, produce hypothesis"
nodes:
  - id: ingest_readme
    type: ingest
    config:
      source: git
      repo: https://github.com/XxxGHOSTX/PythonProject2.git
      path: README.md
  - id: parse_text
    type: parse
    inputs: [ingest_readme]
  - id: embed
    type: embed
    inputs: [parse_text]
    config:
      model: sentence-transformers/multi-qa
  - id: index_vector
    type: vector_upsert
    inputs: [embed]
    config:
      vector_db: local_faiss
  - id: reasoner
    type: hybrid_reasoner
    inputs: [index_vector, parse_text]
    config:
      hdr_ref: hdr_001
      filters: ["no_wetlab", "domain:math,biocomp"]
  - id: ranker
    type: rank
    inputs: [reasoner]
  - id: simulate
    type: simulate
    inputs: [ranker]
    config:
      sandbox_image: sim-math:1.0
  - id: artifact_sign
    type: sign_and_store
    inputs: [simulate]
  - id: finalize
    type: export
    inputs: [artifact_sign]
```

## Example HDR payload (JSON)

This is the human-signed payload format that anchors inventorship.

```json
{
  "hdr_id": "hdr_001",
  "human": {
    "name": "Tony",
    "email": "you@example.com",
    "signature_method": "gpg-v2"
  },
  "objective": "Discover mathematical identities useful for efficient biologically-inspired computation abstractions",
  "constraints": ["no actionable wet-lab instructions", "scope: in-silico, simulation-only", "domains: math, synthetic-bio-theory"],
  "success_criteria": ["candidate with confidence>0.85 AND simulation_consistency>0.9"],
  "timestamp": "2026-02-09T00:00:00Z",
  "notes": "Human specified search heuristics: prefer cross-domain co-occurrence and topological graph motifs."
}
```

## API contracts (sketch — OpenAPI style)

Provide endpoints (for the engineer).

- `POST /hdr` — submit HDR (returns hdr_id). Must require cryptographic signature.
- `POST /pipelines` — submit Execution Graph YAML. Returns pipeline_id.
- `POST /run` — run pipeline with hdr_id + pipeline_id. Returns run_id.
- `GET /run/{run_id}/artifacts` — list artifacts and provenance.
- `GET /artifact/{artifact_id}` — download artifact and metadata.
- `GET /knowledge/query` — search vector/graph with HDR constraints.
- `POST /human-validate/{hypothesis_id}` — human validation signal (true/false + commentary).

## Evidence & provenance workflow (immutable capture)

- On each HDR submission, compute human signature and write HDR to append-only ledger (e.g., timestamped IPFS + signed hash + anchor in cloud KMS).
- For each pipeline run: capture pipeline YAML, pipeline container image digest, code commit hash, inputs (document refs + HDR id), full execution log, and resulting artifacts.
- Produce an Artifact Package: `{artifact.zip, provenance.json, signature.asc}` and store in artifact registry with immutable object address.
- Export patent packet generator that compiles high-confidence artifacts + provenance into a human-readable narrative and attachments.

## Scoring & ranking (explicit formula)

EvidenceScore(E) = w1·ProvDepth + w2·CrossDomainCooccurrence + w3·SimulationConsistency + w4·HumanSignal − w5·RedundancyPenalty

Where:

- ProvDepth = log(1 + number_of_supporting_passages)
- CrossDomainCooccurrence = normalized count of distinct domains covering claim
- SimulationConsistency = average similarity across N simulation runs
- HumanSignal = normalized human validation votes (0–1)
- RedundancyPenalty = fraction of matches to existing patents / known art (requires IP lookup)

(Default weights: w1=0.35, w2=0.25, w3=0.2, w4=0.15, w5=0.05 — tunable in HDR)

## Security, governance, and safety (explicit rules)

- Mandatory HDR signature for any discovery run that involves more than trivial queries.
- "No-wetlab" constraint must be enforced by deterministic filters in ingest, reasoner, and export modules; when HDR lacks clearance, all outputs flagged with `restricted:true` and routed to a human-review queue.
- PII scrub pipeline for ingestion; data access controlled by RBAC.
- Audit logs and periodic red-team reviews for model hallucination and unsafe synthesis.
- Ethics board review required before any outputs are used to propose physical experiments or external collaborations.

## Patent drafting bundle (what to include)

- System specification text (this document).
- Example HDR logs and signed artifacts showing human direction + time stamps.
- One or more reproducible demo runs (ingest→reasoner→artifact) with attached provenance.json.
- Architecture diagrams (component list + data flows).
- Sample claim set (included above).
- Appendix: sample pipeline YAML and small dataset used for demo.

## Example claim language (ready to paste into attorney packet)

(See Independent claim above — include both the independent claim and the dependent claims 2–5 as written.)

## Implementation roadmap (detailed milestones)

### Phase A — Freeze invention (0–2 weeks)

- Produce formal spec (this document).
- Collect and sign HDRs that capture your conception moments (export chats, store with signatures).
- Create a single reproducible demo repository with an ingest→reasoner→artifact pipeline and full provenance capture.

### Phase B — MVP (2–8 weeks)

- Build orchestrator (DAG runner) + one ingestion adapter + FAISS vector store.
- Implement HDR submission endpoint and provenance store (append-only).
- Implement simple hybrid reasoner: graph traversal + LLM prompt templates (local or cloud).
- Produce 3 reproducible runs and package artifacts.

### Phase C — Harden & extend (8–20 weeks)

- Add knowledge graph (Neo4j), model registry, simulation sandbox, UI.
- Add artifact signing, immutable ledger anchoring (e.g., timestamp to blockchain or trusted timestamping).
- Run internal red-team; prepare patent package.

### Phase D — Legal & IP (parallel, after Phase A)

- Engage patent attorney, deliver patent bundle, file provisional (if desired).
- Establish contributor agreements and NDAs.

## Repository scaffold (recommended monorepo initial tree)

```
thalos-prime/
├─ core-orchestrator/
│  ├─ src/
│  ├─ Dockerfile
│  ├─ pipeline_schema.yaml
│  └─ README.md
├─ ingest-adapters/
│  ├─ git_adapter/
│  ├─ pdf_adapter/
│  └─ README.md
├─ knowledge/
│  ├─ vector_client/
│  ├─ graph_client/
│  └─ schema/
├─ reasoner/
│  ├─ symbolic_engine/
│  ├─ llm_wrappers/
│  └─ prompt_templates/
├─ simulator/
│  ├─ sandbox_jobs/
│  └─ job_runner/
├─ api/
│  ├─ openapi.yaml
│  └─ auth/
├─ ui/
│  └─ prototype/
├─ ops/
│  ├─ k8s/
│  └─ terraform/
├─ docs/
│  └─ patent_bundle/
└─ ci/
   └─ workflows/
```

## Sample README snippet (to drop into repo)

```
Thalos Prime — Discovery Execution Engine
========================================
Purpose: Formalize human-directed discovery via HDR-anchored execution graphs, hybrid reasoning, and immutable provenance.
Goals: reproducible discoverability, patentable capture of human inventorship, safe in-silico experimentation.

Quickstart:
1. Submit HDR via `POST /hdr` (signed).
2. Upload pipeline.yaml to `/pipelines`.
3. Run `POST /run` with hdr_id + pipeline_id.
4. Retrieve artifacts: `GET /run/{id}/artifacts`.

Security: All HDR payloads must be cryptographically signed. System enforces "no_wetlab" filter by default.
```

## Example prompt template (reasoner — evidence-first)

Prompt skeleton for LLM (store in `reasoner/prompt_templates/evidence_first.tpl`):

```
Human Direction: {{hdr.objective}}.
Constraints: {{hdr.constraints}}.
Supported Evidence Passages (each with doc_id and excerpt): 
{% for p in passages %}
- {{p.doc_id}}: "{{p.excerpt}}"
{% endfor %}
Task: Using ONLY the passages above and the knowledge graph relations provided, synthesize up to 3 candidate hypotheses. For each hypothesis include:
1) concise hypothesis statement (1-2 sentences)
2) list of supporting passages by id
3) minimal computational simulation schema (inputs/outputs only — no wetlab steps)
4) rationale linking evidence to hypothesis
Do not invent unsupported facts. Mark any uncertain claims with [UNCERTAIN].
```

## Sample provenance.json (small example)

```json
{
  "artifact_id": "art_0001",
  "pipeline_id": "example_ingest_reasoner_v1",
  "pipeline_commit": "abc1234",
  "inputs": [{"doc": "repo:PythonProject2/README.md", "hdr": "hdr_001"}],
  "container_images": [{"node": "reasoner", "digest": "sha256:aaa..."}],
  "execution_log": "gs://thalos-artifacts/run_0001/log.txt",
  "signature": "-----BEGIN PGP SIGNATURE----- ...",
  "timestamp": "2026-02-09T12:00:00Z"
}
```

## Example patent pack export structure (what to hand to attorney)

```
patent_bundle/
├─ spec.md (this full spec)
├─ claims.txt (all claim language)
├─ diagrams/ (png/pdf of architecture)
├─ hdrs/ (signed HDR JSON files)
├─ runs/ (run_0001 artifact.zip + provenance.json)
└─ demo_instructions.md
```

## Immediate deliverables (included in this repository)

- Execution Graph YAML example (`pipeline.yaml`).
- HDR JSON example (`docs/hdr_example.json`).
- Prompt template (`reasoner/prompt_templates/evidence_first.tpl`).
- Claim language (within this spec and `docs/patent_bundle/claims.txt`).
- README snippet (incorporated into `README.md`).
- Provenance JSON template (`docs/provenance_sample.json`).

## Safety and legal guardrail reminder (non-negotiable)

This specification intentionally excludes actionable wet-lab step-by-step procedures. Any biological translation must pass an institutional review, biosafety committee, and legal counsel before physical experiments.

Patent filing requires an attorney; the claim language above is a technical draft intended to accelerate legal drafting, not a substitute for counsel.

## Suggested next engineering steps (concrete, immediate)

- Create `thalos-prime` repo with tree above and commit this spec as `/docs/spec.md`. GPG-sign commits for HDR linkage.
- Implement core-orchestrator with a minimal DAG runner (use Prefect or Dagster). Add REST endpoints `/hdr`, `/pipelines`, `/run`.
- Add a FAISS-based local vectorstore and the example pipeline from `pipeline.yaml`. Run end-to-end and capture `provenance.json`.
- Produce three HDR-signed runs demonstrating concept; put them in `docs/patent_bundle/runs/`.
- Contact a patent attorney with the `patent_bundle/` folder.
