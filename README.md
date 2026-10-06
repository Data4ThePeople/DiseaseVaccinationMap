# DiseaseVaccinationMap

An interactive map of reported infectious disease cases and vaccination coverage
in every U.S. state, 1929 to 2025, built by Data 4 The People.

**See it:** https://data4thepeople.github.io/DiseaseVaccinationMap/

Open a state and year directly by adding `#st=TX&y=2025` to that link.

This is a work in progress. `STATUS.md` says where the project stands and what
is still undecided.

## What is in this repo

| Path | What it is |
|---|---|
| `dist/index.html` | The built tool: one self-contained page, no server needed |
| `viz/template.html` | The page's HTML, CSS and JavaScript, before the data is inlined |
| `scripts/` | Numbered Python scripts that fetch the sources and build the data |
| `data/` | Built tables, the milestone files, and the check reports |
| `DATASETS.md` | Every data source: what it covers, its gaps and its traps |
| `data/COVERAGE.md` | How much of each disease's record is a complete report, by decade |
| `data/TIEOUT.md` | Page numbers recomputed from the raw files |
| `STATUS.md` | Current step, decisions made, decisions open |

Read `DATASETS.md` before trusting any number. The case counts are reported
cases, not infections, and several diseases have runs of years with no state
figures at all.

## Get the project

You need [Git](https://git-scm.com/downloads) and Python 3.9 or newer.

### PyCharm

1. On the Welcome screen choose **Clone Repository** (or **File > New > Project
   from Version Control** if a project is already open).
2. Paste this URL and choose a folder:
   `https://github.com/Data4ThePeople/DiseaseVaccinationMap.git`
3. Click **Clone**, then **Trust Project**.
4. When PyCharm offers to create a virtual environment from `requirements.txt`,
   accept. If it does not offer, go to **Settings > Project > Python
   Interpreter > Add Interpreter > Add Local Interpreter**, choose
   **Virtualenv**, and then run `pip install -r requirements.txt` in PyCharm's
   terminal.

### VS Code

1. Open the Command Palette and run **Git: Clone**.
2. Paste `https://github.com/Data4ThePeople/DiseaseVaccinationMap.git`, pick a
   folder, and open the cloned project.
3. Set up Python with the terminal steps below.

### Any terminal

```bash
git clone https://github.com/Data4ThePeople/DiseaseVaccinationMap.git
cd DiseaseVaccinationMap
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### No Git

On the GitHub page click **Code > Download ZIP**, unzip it, and open the folder
in your editor. You can view and change the files this way, but you cannot pull
updates or send changes back.

## Look at the tool locally

Open `dist/index.html` in a browser. It needs no server and no internet
connection.

## Rebuild the data and the page

The raw downloads are not in the repo (they are large and are re-fetched), so
a fresh clone has the built tables but not the source files behind them. One
script recreates everything, in order:

```bash
python scripts/run_all.py
```

It downloads every source that is missing into `data/raw/`, re-extracts the
CDC annual tables and the other hand-built extracts, rebuilds every table in
`data/`, writes `dist/index.html` and `dist/findings.html`, and finishes with
the coverage check and the tie-out (`data/TIEOUT.md`). A first run downloads
roughly 700 MB and takes a while; later runs skip anything already downloaded.
If a step fails, fix it and run the script again; finished downloads are kept.

Some sources are live (CDC's weekly table, the Johns Hopkins trackers, BEA and
Census revisions), so a fresh run can differ slightly from the committed files
in the most recent years. `git diff --stat data/` shows what moved.

No API key is needed. The Census responses the build uses (2005 to 2024) are
saved in the repo; a key is only needed to fetch a newer year. If you have one
([free sign-up](https://api.census.gov/data/key_signup.html)), set
`CENSUS_API_KEY`.

To rebuild only the page from the committed tables (a small download for the
map shapes, then two quick steps):

```bash
python scripts/run_all.py --quick
```

After a change to `viz/template.html`, `python scripts/09_build_viz.py` alone
is enough.

## Work on it with Claude Code

Claude Code is Anthropic's coding assistant. It reads the files in the project
folder and can run the scripts for you. It needs a paid Claude plan (Pro, Max,
Team or Enterprise) or a Claude Console account; the free plan does not include
it.

### 1. Install it

macOS, Linux or WSL:

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

Windows PowerShell:

```powershell
irm https://claude.ai/install.ps1 | iex
```

Then open a new terminal and check it with `claude --version`. Other ways to
install (Homebrew, WinGet, the desktop app) are in the
[setup guide](https://code.claude.com/docs/en/setup).

### 2. Start it in the project

Open a terminal **in the project folder** and run:

```bash
claude
```

The first time, it opens a browser window to log in.

### 3. Connect it to your editor

- **PyCharm and other JetBrains IDEs:** install the
  [Claude Code plugin](https://plugins.jetbrains.com/plugin/27310-claude-code-beta-)
  from the JetBrains Marketplace and restart the IDE. Then run `claude` in
  PyCharm's built-in terminal, or press `Cmd+Esc` (Mac) or `Ctrl+Esc`
  (Windows, Linux). Claude's edits open in PyCharm's diff viewer, and it can
  see the file and selection you have open. If you started `claude` in a
  separate terminal, type `/ide` to connect it. Details:
  [JetBrains guide](https://code.claude.com/docs/en/jetbrains).
- **VS Code:** see the [VS Code guide](https://code.claude.com/docs/en/vs-code).
- **No editor:** the terminal alone works.

### 4. A good first prompt

```
Read STATUS.md and DATASETS.md, then tell me where this project stands and
what is still open.
```

Those two files, plus the notes beside each data extract
(`data/raw/*/NOTES.md`, `data/MILESTONES_NOTES.md`,
`data/milestones_states/NOTES_batch*.md`), are what Claude needs to pick up
the work. The publishing rules Data 4 The People uses live in the maintainer's
own Claude settings, not in this repo, so a new session will not know them
unless you tell it.

## Sending changes back

This repo belongs to the Data4ThePeople organization. If you have not been
given write access, fork it on GitHub, push your changes to the fork, and open
a pull request. Every push to `main` that changes `dist/` republishes the live
page.

## Sources and credit

Case counts: CDC National Notifiable Diseases Surveillance System (final annual
tables and weekly tables) and Project Tycho, University of Pittsburgh (CC BY
4.0). Vaccination: CDC National Immunization Survey and SchoolVaxView, the U.S.
Immunization Survey and the National Health Interview Survey. County figures:
Johns Hopkins University. State indicators: U.S. Census Bureau and Bureau of
Economic Analysis. Party control: Klarner, State Partisan Balance Data, and
Ballotpedia. Full citations and license notes are in `DATASETS.md`. Two of
these sources have reuse terms that are not yet settled; see the open items in
`STATUS.md`.
