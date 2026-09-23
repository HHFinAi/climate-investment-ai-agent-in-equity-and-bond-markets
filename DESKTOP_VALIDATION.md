# Desktop package validation - 23 September 2026

**Engine version:** 0.1.0. This is a documentation and packaging edition, not an analytical-engine upgrade.

## Executed in the authoring environment

- **116 unit/integration tests passed** on Python 3.13.5 / Linux, with zero failures, errors or skips. Raw output: `tests/desktop-run.txt`.
- `scripts/check_repository.py` passed: 20 role contracts, seven workflow routes and 19 source anchors.
- A fresh synthetic multi-asset CLI run completed with `DEMO_COMPLETE_NOT_APPROVED`.
- Original runtime Python, all 20 role instructions and registry, seven workflow graphs, schemas, example inputs, calculation references and test implementations were compared byte-for-byte with the original v0.1.0 archive and are unchanged.
- Release hashes were regenerated for the documentation edition and independently verified against the completed ZIP after extraction.
- A temporary **local** Git staging simulation checked that all release files are included, that hidden configuration is retained, and that staged content matches the release bytes. It had no remote and made no network calls.
- Source PDFs, rendered images, credentials, local research data, caches and `.git/` are excluded from the release archive.

## Changed delivery files

`README.md`, `PUBLISHING.md` and `CHANGELOG.md` now prioritise GitHub Desktop. `START_HERE_GITHUB_DESKTOP.md`, this validation note and `tests/desktop-run.txt` were added. `FILE_MANIFEST.json` was refreshed. Historical validation files were retained and are explicitly records of their earlier checks, not new remote results.

## Not performed

The GitHub Desktop GUI was not run. No remote repository was created, populated or updated. No remote GitHub Actions job was observed. The local tests were not run on macOS or Windows; UI instructions were checked against official GitHub documentation instead. There is no live LLM/data integration, investment-performance validation, scientific calibration, legal certification or automatic trading.

Publication and checking the actual remote Actions run remain actions for the repository owner. Passing software tests does not establish that an investment conclusion is correct.
