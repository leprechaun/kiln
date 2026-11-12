# Build the platform from scratch

The five-phase KCL-first pipeline (source CRDs → curate provider schemas → design composition schemas → write compose functions → generate manifests) was independently prototyped and validated phase-by-phase before this project began, but no code from that exploration carries forward. We author every schema and `compose*.k` function fresh, treating the prior validation as design input — proof the approach works and a set of house rules to follow — not as a codebase to extend.
