# Security policy

## Reporting a vulnerability

Do not publish exploit details, credentials, private data, or an unpatched vulnerability in a public issue or pull request.

Use GitHub's private vulnerability reporting or Security Advisories feature for this repository (Security → Advisories → Report a vulnerability). If private reporting is unavailable, contact the repository owner through the GitHub account that owns this repository and request a private reporting channel.

Include the affected repository, branch or commit, affected file and line, reproducible impact, and a safe proof of concept. Do not include live secrets or personal data.

## Handling

Reports will be triaged privately. Do not assume a report is accepted, fixed, or eligible for a reward until the owner confirms it. Do not test against systems or data you do not own or have permission to assess.

## Contributor rules

Never commit passwords, API tokens, private keys, signing keys, database dumps, conversation records, production logs, environment files, or other confidential material. Use runtime secret storage. Rotate any credential that may have been exposed; deleting it from the latest commit does not remove it from Git history.

## Scope

Repository-side scans and CI checks reduce risk but do not prove that every Git ref, fork, release, deployment, log, cache, backup, or external copy is clean.
