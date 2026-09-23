# Private GitHub publishing: Desktop or CLI

**Target:** `HHFinAi/climate-investment-ai-agent-in-equity-and-bond-markets`.
**Default:** private. There is no public switch in the publishing script.

The authoring environment could read HHFinAi but had no exposed repository-write action or authenticated GitHub CLI. The ZIP is a complete local source package. A remote repository has not been created here.

## Recommended: GitHub Desktop

Use [START_HERE_GITHUB_DESKTOP.md](START_HERE_GITHUB_DESKTOP.md). Create or select the local repository, copy the project contents into its root, review and commit, and publish privately to HHFinAi. Existing remotes should be cloned and updated with an ordinary commit and push. No command-line publisher is needed.

This manual route does **not** automatically enforce the CLI publisher's manifest allowlist or hashes. Review the changed files before every commit and publication. Preserve `.git/`; include `.github/`, `.gitignore` and `.gitattributes`; keep source PDFs, credentials and private research data out of the commit.

## Alternative: CLI initial creation
Install Git, Python 3.10+ and GitHub CLI. Authenticate HHFinAi on github.com with permission to create a private repository and push its contents/workflow. Configure Git `user.name` and `user.email` locally or globally. These values are used for the initial commit; no credentials are read or printed by the script.

Run `python3 scripts/publish_github.py` from the extracted package for a local preview. Run `python3 scripts/publish_github.py --execute` to perform the external creation explicitly. The script calls only the documented GitHub CLI API/repo commands and ordinary Git; it does not depend on this chat's connector.

The publisher validates release hashes, rejects unsafe paths and symlinks, checks the authenticated username, checks the exact target for existence, reruns package/tests, creates a fresh sibling Git staging folder, commits only allowlisted original files, creates the private repository and pushes main. It never overwrites an existing repository, changes another repository's visibility, force-pushes or uploads the textbook. New files outside the release manifest are not silently published.

## Partial failure
Remote creation and Git push are separate operations. If creation succeeds but push fails, the script leaves the staging directory and prints its exact path. Inspect the private repository and credentials, then retry an ordinary push from that directory. Do not delete/recreate the repository or use force. A second initial-creation attempt intentionally refuses an already existing target.

A successful publisher verifies the remote private flag and that remote main equals the staged commit. A clean CI configuration is included, but GitHub Actions success must be observed on the actual remote run; local tests are not a remote CI result.

## Documentation checked for publishing syntax
GitHub CLI `gh repo create`: https://cli.github.com/manual/gh_repo_create
GitHub CLI `gh api`: https://cli.github.com/manual/gh_api
GitHub Actions workflow syntax: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax
Agent Skills specification: https://agentskills.io/specification

These are technical implementation references, not additional climate-investment source material.
