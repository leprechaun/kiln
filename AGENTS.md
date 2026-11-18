## Agent skills

### Issue tracker

Issues and specs live as markdown files under `.scratch/<feature>/` in this repo. See `docs/agents/issue-tracker.md`.

### Triage labels

Default canonical labels (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout: `GLOSSARY.md` + `docs/adr/` at the repo root. See `docs/agents/domain.md`.

### Kiln

Compositions are built with Kiln. Start with the `kiln` skill under `.agents/skills/` (`kiln docs` prints the same text); its Reference table says which file to read for each phase and for any error. The `kcl-primer` and `crossplane-intro` skills cover KCL syntax and Crossplane concepts.
