# Execution client test routes

Open `index.html` directly in a browser. It is self-contained and works offline. No service, build step, external font or package installation is required.

Ten scrollable topics cover Engine/RLP routes, shared-genesis reuse, measured timings, WireX, sync, reorg, Amsterdam fixture counts, execute remote, and execute-blobs/Hive. Arrow keys or Page Up/Down move between topics. `N` toggles the current topic’s discussion notes. `F` toggles fullscreen. Click Head A / Head B on the reorg diagram to change the illustrative canonical branch.

The default layouts target a laptop viewport of 1280×720 or larger. Use browser fullscreen for presentation. A print stylesheet is included for landscape output.

## Sources

Primary docs: `docs/running_tests/running.md` in the supplied `wirex-consume` worktree and linked consume/execute docs. Implementation was checked in that worktree.

Reorg: the supplied `reorg-suite` worktree, including its format docs, consumer and dedicated tests. WireX and reorg are explicitly marked as unmerged work.

Sync history: https://github.com/ethereum/execution-spec-tests/pull/2007

Counts: the supplied v21.0.0 `.meta/index.json`. Count entries whose fork is exactly `Amsterdam`, grouped by format. Formats overlap. WireX uses the EngineX input corpus, with eligibility limitations. Reorg is not included in the release index. Execute runs source tests and has no corresponding count in that fixture index.

`fixture-counts.json` records the index timestamp, root hash, counts and grouping statistics. `build.py` rebuilds the HTML and counts using Python’s standard library. It uses the original cached index when available, or the bundled count snapshot otherwise. Pass an index path to refresh the counts:

```sh
python3 build.py
python3 build.py /path/to/.meta/index.json
```

The 26.5× comparison describes planned base client starts for EngineX, not measured runtime. More grouping reduction remains in legacy allocations. Optional discussion notes in the HTML include implementation qualifications and source references.

Measured timing provenance, exact durations, client images and public Hive result IDs are in `timings.json`. The timing slide compares matched v20.0.1 Paris–Osaka runs from July 2026, rather than the Amsterdam v21 corpus.

Published with GitHub Pages at https://danceratopz.github.io/consume-execute-overview/.
