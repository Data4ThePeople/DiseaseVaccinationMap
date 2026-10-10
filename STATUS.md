# Status

Project: DiseaseVaccinationMap
Process: ~/.claude/d4tp-process/PROCESS.md

## Current

Post: none yet
Step: 1
Since: 2026-10-01

## Steps

| Step | What | Confirmed | Notes |
|---|---|---|---|
| 1  | Exploration and analysis | | |
| 2a | Draft with brackets resolved | | |
| 2b | Eric's edit, Claude's look-over | | |
| 2c | Slice markup | | |
| 2d | Hero 1680x1080 + alt text | | |
| 2e | SEO | | |
| 2f | Pushed to Prismic (draft) | | |
| 2g | Mailchimp teaser | | |

## Stale

None.

## Log

- 2026-10-01 Step 1 opened. Topic: infectious disease incidence by state as far
  back as good data goes, drawn with people icons on a state map, with
  vaccination rates, a state drill-down, a milestone timeline, state KPIs and
  party control. Plan approved the same day
  (`~/.claude/plans/proud-stargazing-engelbart.md`).
- 2026-10-01 First full build in `dist/index.html`: national tile map, state
  drill-down with county map, vaccination history from 1959, state indicators,
  party control, 47 national and 23 pilot-state milestones. Source coverage
  check (`data/COVERAGE.md`) and tie-out (`data/TIEOUT.md`, all passed) run.
  Open with Eric: fifth disease, county data license, Ballotpedia terms,
  awkward milestone headlines, remaining 47 states of milestones.
- 2026-10-01 Eric: keep polio as the fifth disease. Milestones for the other
  47 states and DC started, one file per state in `data/milestones_states/`.
- 2026-10-01 Renamed to DiseaseVaccinationMap. GitHub repo renamed
  (`Data4ThePeople/DiseaseVaccinationMap`). The local folder is renamed once
  the milestone research writing into it has finished.
- 2026-10-02 Milestones done for all 47 other states and DC (338 items, one
  file per state in `data/milestones_states/`, notes per batch beside them).
  Two items held off the page for an editor's decision (MT and ID, 1983).
  Repo made public and GitHub Pages turned on at Eric's request:
  https://data4thepeople.github.io/DiseaseVaccinationMap/ . Local folder
  renamed to `DiseaseVaccinationMap`; `PythonProject1` is a link to it and can
  be deleted once PyCharm is reopened from the new folder.
- 2026-10-06 Step 1 analysis: `analysis/FINDINGS.md` and the shareable page
  https://data4thepeople.github.io/DiseaseVaccinationMap/findings.html .
  Mumps 1968-1992, measles 1968-1992 and whooping cough 1956-1992 now come from
  CDC's scanned final annual summaries (strict sum test, image-read cells
  listed). Eric accepted the 1971 mumps readings and New York City-only mumps
  for 1968-1973. Open: 1970 whooping cough (two misprinted cells).
- 2026-10-10 Independent audit of the data work by a fresh agent: pipeline
  reproduces exactly; open findings on the Tycho years, New York gaps, and how
  missing values are drawn. Eric set the story: damage, elimination, decline,
  resurgence, with the rise of vaccine refusal as a research thread
  (`analysis/ANTIVAX_HISTORY.md`). Hepatitis A 1966 to 1992 now comes from the
  scanned CDC annual summaries (all 27 years pass the sum test, 229 image-read
  cells), replacing Tycho; New York filled except 1985 and 1986 (City printed
  NA). Open with Eric: show upstate New York alone for 1985 and 1986 or leave
  no data; measles 1964 to 1967 from the scans.
- 2026-10-10 Eric: New York stays no data for hepatitis A 1985 and 1986.
  Measles 1964 to 1967 now from the scanned summaries (New York filled, page
  sums equal CDC's printed totals). Tie-out passes. Research report on the
  history of vaccine exemptions and refusal saved as
  `analysis/ANTIVAX_HISTORY.md`; many 2015 to 2026 items in it are flagged as
  not yet checked against the source page.
- 2026-10-10 Worked through the audit's high and medium items. Data: measles
  1956 to 1963 from the scanned summaries (134 image-read cells; Hawaii 1963
  printed "3.623", read as 3,623, awaiting Eric's confirmation). Page: a ring
  marks a disease with no count and a dot a count too small to draw; incomplete
  years (under 48 of 52 weekly reports), thin national figures and provisional
  2025 are faded and labeled; New York City-only mumps shows a count with no
  rate; polio labeled as all polio to 1971 and paralytic from 1993; vaccination
  charts get a full axis where values fall below 50%, gaps where nothing was
  measured or the kindergarten method changed, a 95% range band and a line
  saying what each line counts. County: Connecticut 2025 explained, Oklahoma's
  unknown-county cases taken off Oklahoma County. Findings and DATASETS.md
  corrected. Tie-out passes. Not done, needs Eric: polio from the scans (which
  measure, all polio or paralytic), New York City population for a mumps rate.
- 2026-10-10 Eric: accept 3,623 for Hawaii measles 1963; use paralytic polio;
  drop the rings where no state counted the disease that year. Paralytic polio
  1956 to 1992 read from the scanned summaries (all 37 years pass the sum test;
  29 whole columns read from the page image). Tycho all-polio now only before
  1956. Tie-out passes. Committed and pushed. The research notes, `reports/` and
  `analysis/ANTIVAX_HISTORY.*` are kept out of the public repo for now.
