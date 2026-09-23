# Start here: publish with GitHub Desktop

**Project:** Climate Investment AI Agent in Equity and Bond Markets  
**Account:** HHFinAi  
**Repository name:** `climate-investment-ai-agent-in-equity-and-bond-markets`  
**Visibility:** Private  
**Engine:** v0.1.0; GitHub Desktop documentation edition, 23 September 2026.

This route uses GitHub Desktop for publishing. You do not need GitHub CLI, Python, API keys or a terminal to upload the prepared files. Python is needed only to run the optional local tests and workflow engine. Publishing stores the project on GitHub; it does not activate an AI agent or connect market data.

## 1. Create the local repository

Extract the Desktop-ready ZIP outside your intended repository directory. Keep the extraction as a clean source copy.

Sign in to GitHub Desktop as **HHFinAi**. Open **File > New Repository** (or **Create a New Repository on your Hard Drive** on the welcome screen). Use these project settings: [1]

| Field | Enter or select |
|---|---|
| Name | `climate-investment-ai-agent-in-equity-and-bond-markets` |
| Description | `Source-grounded, human-reviewed climate investment research workflows for equity and bond markets.` |
| Local path | A parent folder for your repositories, such as `Documents/GitHub`. |
| Initialize this repository with a README | Unchecked: the package already contains `README.md`. |
| Git ignore | None: copy the package's `.gitignore` instead. |
| License | None: this project has not selected an open-source license; keep `NOTICE.md`. |

Click **Create repository**. The repository is initially local. Desktop adds a directory with the repository name beneath the chosen parent. Do not append the name twice. For this new project, use `main` as the branch name. An initial Desktop-generated commit is normal. [1]

**Already created locally?** Select that repository and continue with step 2.  
**Already created on GitHub?** Use the existing-repository route below instead of creating a second remote.

## 2. Copy the project into the repository root

In Desktop, use **Repository > Show in Finder** (macOS) or **Show in Explorer** (Windows) to open the local repository. Alternatively, navigate to its local path yourself.

Open the extracted project folder in a separate window. Copy **everything inside that folder** into the local repository: the files and all subfolders, not the ZIP and not another outer project folder. Enable hidden-file display in your file manager so that `.github/`, `.gitignore` and `.gitattributes` are included.

Keep the `.git/` directory that Desktop created. The package contains no `.git/` directory. For a fresh repository, use the package's `.gitattributes` if Desktop asks about replacing its generated version. When importing into an existing project that contains your own edits, compare conflicting files rather than replacing them blindly.

The root should look like this (additional files are expected):

```text
climate-investment-ai-agent-in-equity-and-bond-markets/
  .git/                         <- local Git history; not supplied
  .github/workflows/validate.yml
  .gitattributes
  .gitignore
  README.md
  START_HERE_GITHUB_DESKTOP.md
  AGENTS.md
  SKILL.md
  WORKFLOW.md
  FILE_MANIFEST.json
  agents/
  climate_agent/
  examples/
  references/
  schemas/
  scripts/
  templates/
  tests/
  workflows/
```

**Root check:** `README.md` and `climate_agent/` must be immediately inside the repository. A second identically named project folder inside it means the import is nested incorrectly.

Keep the source CFA PDF, page images, ZIP archive, credentials, client/portfolio data and generated research runs outside the files you commit. The bundled `.gitignore` excludes several common sensitive paths, but it is not a complete security scanner.

## 3. Review and commit

Return to **Changes** in Desktop. Review the new files and select the intended project changes. The package's `.github/workflows/validate.yml` is a read-only testing workflow; it belongs in this initial commit. Do not select **Discard changes**. [2]

Use this commit summary:

```text
Initial release: climate investment AI agent
```

Optional commit description:

```text
Add source-mapped analyst roles, seven research workflows, a Python
orchestrator, synthetic examples, validation tests and Desktop setup guidance.
```

Click **Commit to main**. A commit saves the changes locally; it is not the publication step. The button displays the active branch, so verify the branch name before committing. [2]

## 4. Publish privately

Click **Publish repository**. Confirm the repository name above, keep **Keep this code private** selected, and choose **None** in the Organization field when publishing to your personal HHFinAi account. Click **Publish Repository**. Do not run `scripts/publish_github.py` for this route: it is an alternative creation-only CLI publisher and refuses an existing remote. [3]

For a repository that has already been published, use **Push origin** after committing. [4]

## 5. Verify the result

Use **Repository > View on GitHub** to open the published repository. [1]

Confirm the owner is **HHFinAi**, the name is exact and the visibility label is **Private**. Verify the root contains `README.md`, `AGENTS.md`, `climate_agent/`, `agents/`, `workflows/` and `.github/workflows/validate.yml`.

Open **Actions** and inspect the included **Validate climate investment workflow** run. Its configuration tests Python 3.10 and 3.12 on Ubuntu. A green result must come from that remote run; the authoring environment's local test result is not a remote CI result. If Actions are unavailable or no run appears, first check the workflow file, account/repository Actions permissions and any GitHub-provided error; do not treat missing checks as success.

## Existing-repository route

If this name already exists on GitHub, in Desktop choose **File > Clone Repository**, select the HHFinAi repository and a local destination, and clone it. Then copy the project contents into that clone, review conflicts, commit and click **Push origin**. Do not use Publish to create a duplicate and do not force-push or delete the existing repository. [5, 4]

## Optional: run the project after publishing

Publication is complete without running these commands. To exercise the engine, install/use Python **3.10+**, open a terminal in the repository root and run:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/check_repository.py
python3 -m climate_agent demo --workflow multi-asset --out runs/demo-01
```

On Windows, use `python` or `py -3` instead of `python3` when that is how Python is installed. Choose a fresh output directory for every demo. The expected end state is `DEMO_COMPLETE_NOT_APPROVED`; that is deliberate, not a failure.

The GUI publishes files. The engine coordinates research handoffs. An external AI host or analyst supplies actual research and permitted data. Start with `AGENTS.md`, `WORKFLOW.md` and `examples/research-request-template.json` for research operation. Do not regard GitHub Actions or a synthetic demo as a running investment agent.

## Quick troubleshooting

| Symptom | Check |
|---|---|
| Desktop shows no new files | Confirm the selected repository and copy destination; extract the ZIP before copying. |
| GitHub shows only another project folder | Move the inner folder's contents to the repository root, then commit and push the correction. |
| The workflow file is missing | Copy the hidden `.github` directory from the clean extracted package. |
| Publish reports that the name already exists | Follow the existing-repository route; preserve existing history. |
| Authentication or push is rejected | Verify HHFinAi sign-in and permissions in Desktop; do not share credentials or force-push. |
| The original CLI publisher reports a hash error | It is not needed for Desktop. The manifest records delivery bytes; intentional later edits change hashes. |

## What changed in this edition

Desktop onboarding was added and publishing instructions were revised. Runtime Python, analyst roles, workflow graphs, schemas and tests remain byte-identical to v0.1.0. See `DESKTOP_VALIDATION.md` for checks executed on this package. The CFA textbook and page images are not included. No remote creation, publication or GUI operation was performed in the authoring environment.

## Reference notes

The project-specific folder layout and safeguards above come from the supplied repository package. UI guidance uses the following official GitHub documentation, consulted 23 September 2026. These technical references do not update or replace the climate curriculum.

1. [Creating your first repository using GitHub Desktop](https://docs.github.com/en/desktop/overview/creating-your-first-repository-using-github-desktop)
2. [Committing and reviewing changes to your project](https://docs.github.com/en/desktop/making-changes-in-a-branch/committing-and-reviewing-changes-to-your-project-in-github-desktop)
3. [Adding an existing project to GitHub using GitHub Desktop](https://docs.github.com/en/desktop/adding-and-cloning-repositories/adding-an-existing-project-to-github-using-github-desktop)
4. [Pushing changes to GitHub from GitHub Desktop](https://docs.github.com/en/desktop/making-changes-in-a-branch/pushing-changes-to-github-from-github-desktop)
5. [Cloning and forking repositories from GitHub Desktop](https://docs.github.com/en/desktop/adding-and-cloning-repositories/cloning-and-forking-repositories-from-github-desktop)
