# Security policy

## Reporting a vulnerability

Please **do not** open a public issue for security problems. Instead, use GitHub's
[private vulnerability reporting](https://github.com/stashlop/Itihaas/security/advisories/new)
for this repository, including steps to reproduce and the impact you observed.
If private reporting is unavailable, contact the maintainer through their
[GitHub profile](https://github.com/stashlop) and ask for a private channel.

## Scope notes

- Payments in Itihaas are simulated; no real payment data is processed.
- Never commit `.env`, databases or uploaded files. If a secret is committed by mistake,
  rotate it immediately — removing it from the latest commit does not remove it from history.
