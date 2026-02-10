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
