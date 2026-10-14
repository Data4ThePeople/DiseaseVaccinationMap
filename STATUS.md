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
- 2026-10-10 Second independent tie-out on commit 8c20ff6 by a fresh agent: it
  re-read 3,709 scan cells by eye (all 37 polio columns, 14 hepatitis A years,
  16 measles years) and found one error, paralytic polio 1986 entered under
  Georgia instead of Florida. Fixed, with the small page and documentation
  items it raised. Rest of the chain rebuilt with 0 differences. Not re-read
  cell by cell: 13 hepatitis A scan years and most older mumps, measles and
  whooping cough columns.
- 2026-10-10 Remaining 13 hepatitis A scan years re-read by a fresh agent from
  the page images (663 state cells): no differences. With the earlier 14 years,
  every hepatitis A scan year 1966 to 1992 has now been read twice
  independently. Tie-out fix pushed (0cac19c).
- 2026-10-10 Older scan columns re-read by four fresh agents from the page
  images: whooping cough 1956 to 1992, mumps and measles 1968 to 1992 (about
  4,400 state cells). No value differed. New York notes made clearer (which
  part printed a dash; summed values labeled as sums); no value changed. The
  second reader also reads the two marked 1970 whooping cough cells as 163 and
  the column adds; still held for Eric's decision.
- 2026-10-12 Eric: accept 163 for New York City and Virginia, whooping cough
  1970. The year is filled from the scanned summary (U.S. 4,249); whooping
  cough now has every year from 1956 from CDC's final tables. Tie-out passes.
- 2026-10-13 Measles and polio 1920 to 1955 and whooping cough 1922 to 1955
  now come from the Public Health Service yearly tables (six scans on CDC
  Stacks), typed from the page images and read twice. 105 of 106 disease-years
  add to their printed totals. The page starts in 1920 (Census population for
  1920 to 1928). Held for Eric: polio 1932 (New York printed "534", totals
  need 334). Tie-out passes. Reviewer asked for a herd immunity graphic; Eric
  agreed to a measles-first version: state tiles colored in three steps by
  kindergarten MMR coverage against 95% (blue to orange), county view, and a
  count of states below 95% by year. Not built yet.
- 2026-10-13 Built the measles coverage view (toggle "Color states by measles
  vaccination": three steps against 95%, bar chart of states below 95% by
  school year, county map recolored blue to orange) and, on the reviewer's
  second request, a "States ranked" panel under the map with a highest/lowest
  button. Open with the reviewer: mumps listed twice in his levels, and a
  source for each level, before adding other diseases.
- 2026-10-13 Eric: accept 334 for New York polio 1932. All 106 early
  disease-years now come from the yearly tables; weekly sums remain only for
  Alaska and Hawaii before statehood. Tie-out passes.
- 2026-10-13 Chart built: kindergarten MMR coverage before and after five
  states changed exemption rules (California, New York, Maine, Connecticut
  ended non-medical exemptions; Mississippi added one by court order).
  `analysis/03_exemption_rules_chart.py`, output in `analysis/charts/`. Rule
  dates checked by search against the bill text, Maine CDC and Mississippi
  health department pages; not yet read on the original pages line by line.
- 2026-10-13 The exemption rules chart is on the findings page, in "The
  reverse sequence", as five small charts with Mississippi added.
- 2026-10-13 Reviewer requests built: each state page has a chart of
  kindergarten MMR coverage by school year from 2009-10 with measles cases
  under each year; the numbers table can be ranked by any column and carries
  kindergarten coverage columns beside the diseases.
- 2026-10-13 Third independent tie-out (fresh agent, 1920 to 1955 data,
  1920s population, coverage counts, rebuild): 1,239 cells re-read by eye with
  0 differences from the readings file; 149 of 150 U.S. totals agree with a
  second printed source (the 1951 supplement misprints measles 1950); rates,
  population and the rebuild match exactly. It confirmed New York polio 1932
  reads "534" on the scan and that only 334 fits the totals. It found CDC marks
  some kindergarten estimates as lower bounds (">="); the page now shows that.
  Not re-read by eye: 85 of the 106 early disease-years (sum-checked only).
- 2026-10-13 Eric: the map coloring by kindergarten MMR coverage is on by
  default (it shades from 2010 on; the checkbox turns it off).
- 2026-10-14 Eric: the findings page table on exemption rules now uses the
  same years as the charts (last school year before each rule, first year
  under it, 2025-26), with Mississippi added and New York shown as MMR
  coverage; New York's exemption share moved to the note under the table.
- 2026-10-14 Fourth independent tie-out (fresh agent) of the newer page
  features: every value it recomputed from CDC's file matched (816 tiles, 15
  years of state counts, 64 rankings, 87 table sorts, 14 state charts, the
  findings charts and table), and it read the five rule dates on the original
  legislature, court and health department pages. It found that CDC's
  lower-bound mark is spelled "≥" before 2020-21, which the build missed (72
  MMR state-years); fixed, with the text that said the mark began in 2020-21.
  Also fixed: state charts now run to 2025-26, Connecticut's rule wording
  (in effect April 28, 2021; 2022-23 is the first kindergarten class fully
  under it), and the phone layout (rail charts hidden or overflowing, tile
  labels colliding, rates rounded against their color). The meaning of the
  mark is confirmed in CDC's MMWR table notes.
- 2026-10-14 Disneyland timing checked against the original sources (CDC
  MMWR 64(06); SB 277 as introduced): exposures December 17-20, 2014; bill
  introduced February 19, 2015; signed June 30, 2015. "Months after the
  Disneyland outbreak" holds. All five rule claims are now checked at source.
- 2026-10-14 Mike Kinch suggested red, yellow and green for coverage, since the
  oranges looked like mumps. Eric chose grays instead (red, green and yellow are
  disease colors on the tiles, and red/green is hard for many readers to tell
  apart): lighter means higher coverage on the map tiles, legend, bar chart,
  state chart dots, ranking and county map. "No figure" is white with a gray
  outline so it can't be read as 95% or more. Tie-out passes.
- 2026-10-14 Phone check of the gray scale. Fixed: disease dots overlapped the
  coverage rate on small tiles (small tiles with coverage on are now a little
  taller, so the dots get their own line, or sit in the bottom right corner);
  the four vaccine charts on a state page were drawn at half width and
  stretched on phones; the "states below 95%" line in the legend was cut off
  at the right edge. No sideways scroll at 390, 500 or 700px. Tie-out passes.
