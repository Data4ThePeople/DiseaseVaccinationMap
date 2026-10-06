# Datasets

One section per dataset, written before any analysis, updated whenever we learn
something new. The point is to know the traps before they show up in a chart.

Status key used below: **read** means the documentation and the file itself
were both inspected; **file only** means the file was inspected and the method
documentation still has to be read; **not yet pulled** means the section is a
placeholder and nothing from that source may be charted until it is filled in.

---

## Project Tycho 2.0, United States condition files (University of Pittsburgh)

Status: read (README in each zip, file profile of all 92 US files on October 1, 2026).
The method paper (van Panhuis et al., JAMIA 2018, doi:10.1093/jamia/ocy123) still
has to be read in full.

**What it is.** Counts of reported cases of one disease in one place for one
time interval. One row is one count: a state, city or (rarely) county, a start
date, an end date and a number. The counts were copied from the weekly federal
notifiable disease reports (today's National Notifiable Diseases Surveillance
System, NNDSS) and its printed forerunners.

**Where it comes from.** Zenodo community `projecttycho`, one record per
disease. 95 US records; we downloaded 92 (all but COVID-19 and the two older
multi-disease "Level 1" and "Level 2" bundles). Each is a zip with one CSV of
20 columns and a README. No login. `scripts/01_fetch_tycho.py` re-downloads.

**Version and vintage.** Version 2.0, dated April 1, 2018. The project is not
being updated. Nothing after 2017 will arrive from this source.

**Coverage.** State-level weekly rows by disease (first to last year with a
state row that is not part of a running total):

| Disease | State weekly rows | Running-total rows |
|---|---|---|
| Measles | 1909 to 2001 | 1965 to 2001 |
| Pertussis (whooping cough) | 1909 to 2017 | 1983 to 2017 |
| Mumps | 1967 to 2017 | 1970 to 2017 |
| Diphtheria | 1920 to 1981 | 1956 to 1981 |
| Hepatitis A | 1966 to 2007, then "acute type A" 2006 to 2017 | 1988 to 2017 |
| Polio (acute poliomyelitis) | 1921 to 1971 | 1956 to 1965 |
| Rubella | 1966 to 2017 | 1970 to 2017 |
| Varicella (chickenpox) | 1972 to 2017 | 2002 to 2017 |
| Smallpox | 1900 to 1952 | none |

All counts are direct copies of what was reported. Tycho fills nothing in. The
gaps are real gaps: **a week with no report is simply absent from the file**,
while a reported zero is present as a zero. So a yearly sum of weekly rows
undercounts whenever weeks are missing, and the number of weeks present has to
be carried next to every yearly figure. The coverage check (`10_coverage.py`)
measures this by disease, state and year.

**Changes over time.**
- Two kinds of series are mixed in one file. `PartOfCumulativeCountSeries = 0`
  is a count for that week alone. `= 1` is a running total from the start of
  the year to that week. Adding the two together double counts. Later years
  often have only the running total for a disease.
- Many early years have city rows as well as state rows. City rows are not a
  breakdown of the state row and must not be added to it.
- Hepatitis A is split across two files with different condition names
  ("Viral hepatitis, type A" and "Acute type A viral hepatitis") that overlap
  in 2006 and 2007. Polio is split across "Acute poliomyelitis", "Acute
  paralytic poliomyelitis", "Acute nonparalytic poliomyelitis" and "Infantile
  paralysis"; the paralytic and nonparalytic files are parts of the first, not
  additions to it.
- Which diseases a state had to report, and what counted as a case, changed
  many times over the century. National case definitions were first
  standardized in 1990. Counts before and after are not strictly the same
  measure.
- Alaska and Hawaii appear before statehood only in some years.

**Gaps found once the files were summed by year** (see `data/COVERAGE.md`,
rebuilt by `scripts/11_coverage.py`). These are whole runs of years where the
weekly reports did not list the disease by state, so Tycho has nothing:
- Whooping cough: no state rows 1956 to 1973, and few before 1938.
- Measles: state rows thin out after 1991 and stop in 2002.
- Mumps: no state rows 2003 to 2010. Rubella: none 2003 to 2014.
- Polio: stops in 1971. Diphtheria: thin after 1960, stops in 1981.
- In the low-count years (roughly 1975 on) the weekly rows cover only a
  handful of weeks per state, so the weekly sum is not usable and the year-end
  running total is used instead.

**The year-end running total is provisional, and it is low.** Summed over
states it runs about 5% to 35% under the final national counts CDC printed
later (checked by eye against well-known national totals for a dozen years;
those totals are not used anywhere in the build). For measles in the 1980s and
1990s the running totals are erratic in both directions: 194 measles
state-years fail our consistency check (the running total fell during the
year, or the weekly rows add to more than the running total). The build marks
these rows (`check = 1`), the page says so on hover, and CDC's final annual
tables replace Tycho wherever we have them.

**Suppressed, censored or masked values.** None. Counts are as published.

**Missing data.** Absent row means no report, not zero. Never treat a missing
state-year as zero. A state-year with no rows is "no data".

**Revisions.** None; the file is frozen. The underlying weekly reports were
provisional when printed, so a Tycho yearly sum can differ from the final
annual figure CDC printed later in its annual summary.

**Units and rounding.** Whole cases. `Fatalities = 1` rows are deaths, not
cases, and are excluded.

**Known quirks.**
- Measles rows carry `PlaceOfAcquisition` (domestic, abroad, not stated) in
  later years. Domestic and abroad are parts of the total for those years.
- Polio and hepatitis B have age-split rows (`AgeRange` other than 0-130).
  Only 0-130 is used.
- Gonorrhea and malaria have civilian and military rows. Not used here.
- Varicella was never reportable in every state. Its state coverage is patchy
  for the whole record, which is why it is not a candidate disease even though
  its raw total is large.

**Uncertainty.** The publisher gives none. These are reported cases, not
infections. Reporting was far from complete for common childhood diseases:
CDC has long said that only a small share of measles cases were reported
before the vaccine. The share reported is not known by state and year, so the
viz shows reported cases and says so.

**License and attribution.** CC BY 4.0. Cite each dataset by DOI, for example:
Van Panhuis, W., Cross, A., Burke, D., Counts of Measles reported in UNITED
STATES OF AMERICA: 1888-2002 (version 2.0, April 1, 2018): Project Tycho data
release, DOI: 10.25337/T7/ptycho.v2.0/US.14189004.

---

## NNDSS Weekly Data (CDC, data.cdc.gov `x9gk-5huc`)

Status: file only.

**What it is.** The current weekly notifiable disease tables in one long file.
One row is a reporting area (state, region, territory or US total), an MMWR
year and week, and a disease label, with the count for that week, the running
total for the year, and the running total for the same week of the prior year.

**Where it comes from.** `https://data.cdc.gov/api/views/x9gk-5huc/rows.csv`,
232 MB, no login.

**Version and vintage.** Updated weekly; pulled October 1, 2026 (file updated
September 30, 2026). Covers MMWR 2022 week 1 to 2026 week 38.

**Coverage.** 2022 to 2026 directly; 2021 through the prior-year column. All
states. Direct counts; nothing filled.

**Changes over time.** Disease labels are split in ways the older data is not:
"Measles, Indigenous" and "Measles, Imported" (summed for the total);
"Poliomyelitis, paralytic" (used) and "Poliovirus infection, nonparalytic"
(not used). The hepatitis A label changed from "Hepatitis, A, acute" (2022,
2023) to "Hepatitis A, Confirmed" (2024 on); both appear in weeks 45 to 49 of
2023. Confirmed-only is a narrower count, so 2024 on is not strictly the same
measure as before. Diphtheria has no state rows in this file.

**Reporting areas.** New York City reports apart from the rest of New York.
The build adds the two. Area names switch from upper case to mixed case in
2025.

**Suppressed, censored or masked values.** Flag columns carry marks: `-` (no
reported cases), `N` (not reportable in that state), `U` (unavailable), `NN`
(not nationally notifiable), `NP` (not a reporting priority, to be confirmed
in the table notes). `N` and `U` are not zero and are shown as "no data".

**Missing data.** See flags. A blank count with `-` is a zero by CDC's note.

**How late reports change the count (measured).** Whooping cough for 2022 was
2,388 in the last week of 2022 and 3,044 when the same year was printed a year
later, 27% more. So for year Y the build takes the prior-year column from the
last week of Y+1. Only 2025 rests on its own last week and is marked
provisional on the page.

**Revisions.** Weekly counts are provisional and are revised for months. The
week 52 or 53 running total is not the final annual count. Where the final
annual table exists (see next section) it replaces the provisional number.
2026 is a partial year (through week 38) and is labeled as such or left out.

**Units and rounding.** Whole cases.

**Known quirks.** The prior-year running total at a given week is what was
known a year later, so it is closer to final than the same-year figure.

**Uncertainty.** None published. Provisional.

**License and attribution.** US government work, public domain. Credit CDC,
National Notifiable Diseases Surveillance System.

---

## NNDSS annual tables and MMWR Summary of Notifiable Diseases (CDC)

Status: read. Full per-year notes (document, page, table, marks, cutoff date)
are in `data/raw/bridge/NOTES.md`; the extract is rebuilt by
`scripts/02b_fetch_annual_summaries.py`.

**What it is.** The final yearly count of each notifiable disease by state.
Printed each year in MMWR as the "Summary of Notifiable Diseases" (to 2015),
then as "NNDSS Annual Tables" (2016 on).

**Where it comes from.** 1993 to 2015: Table 2 of each MMWR summary, read from
the text layer of the issue PDF on cdc.gov. 2016 and 2018 to 2022: tab-delimited
annual tables on CDC Stacks. 2023: PDF on Stacks. **2017: the Stacks records
redirect to 2018 and their files return 404, so the 2017 tables come from
Internet Archive captures of CDC's own files** (the rows match the first
captures from December 2018). 1984 to 1992: scanned summaries on Stacks, using
the OCR text already in the PDF.

**Coverage.** All seven diseases for every year 1993 to 2023, all 51 areas.
Before 1993 only the scan years that passed a strict test are used: measles
1984, 1988, 1990, 1991, 1992; whooping cough 1985, 1990, 1991, 1992. A scan
year is kept only if every state cell was readable, the states add to each
printed division row, and the divisions add to the printed U.S. row. The other
1980 to 1989 years failed on OCR damage and stay on Project Tycho or "no data".

**Mumps 1968 to 1992 (added October 6, 2026).** Read from the scanned summaries
for every year 1968 to 1992, with the same three-level sum test. Where the scan's
text layer was damaged, 112 cells (91 state rows) were read from the page
image and are listed in `checks_image_cells.csv`. Two 1971 cells are misprinted ("-99" for DC,
"8.784" for Ohio); Eric accepted the readings 99 and 8,784 on October 6, 2026,
and the flags record it. 1981 uses the by-area-and-age mumps table, since that
year's general table has no mumps column. States printed NN (not notifiable)
show as no data, and the build no longer fills them from Tycho. In 1968 to 1973
upstate New York is NN while New York City is printed; by Eric's decision New
York shows the City's count, labeled "New York City only" on the page.

**Checks run.** State sum against the printed U.S. row: 322 disease-years, no
mismatch. PDF against the separately parsed HTML edition, 2007 to 2015: 66
disease-years, no cell differs. Measles against Our World in Data's hand
transcription: 763 of 766 state-years identical; in the 3 that differ our value
is what the CDC table prints and it adds to the printed total.

**Changes over time.**
- Measles is printed as "indigenous" and "imported" before 2008; the total is
  our sum of the two. "Imported" includes cases from other states through 1994
  and only from other countries from 1995. We show the total only.
- Hepatitis A got a revised case definition in January 2019.
- Diphtheria and paralytic polio have no column in years with no U.S. cases.
  The issue says so in a sentence, and those state-years are zeros on that
  basis (25 disease-years).

**Suppressed, censored or masked values.** A dash is defined in every table as
"No reported cases" and is a zero. `N` (not reportable), `NN`, `U` and blank
cells (31 in all) are not numbers and show as "no data".

**Reporting areas.** New York City is printed apart from the rest of New York.
The extract adds the two.

**Revisions.** These are final counts, each with a stated cutoff date from
1994 on. They replace every other source for the same disease, state and year.

**Uncertainty.** None published. Reported cases only.

**License and attribution.** Public domain. Credit CDC, National Notifiable
Diseases Surveillance System.

---

## Vaccination coverage among young children, National Immunization Survey-Child (CDC, `fhky-rtsk`)

Status: file only. The NIS-Child method report still has to be read.

**What it is.** Survey estimates of the share of children vaccinated by a
given age, by vaccine and dose, for the nation, states and some cities. Each
row has an estimate, a 95% confidence interval and a sample size.

**Where it comes from.** `https://data.cdc.gov/api/views/fhky-rtsk/rows.csv`, 13 MB.

**Coverage.** Children born 2011 to 2022 (single birth years and two-year
pooled groups). Vaccines include 1+ dose MMR, DTaP (1+ to 4+ doses), polio
(1+ to 3+), hepatitis A (1+, 2+). By age 13, 19, 24 and 35 months.
**This file does not go back to the mid-1990s.** The earlier state estimates
(survey years 1995 on) were published as yearly tables in a different layout,
by survey year instead of birth year. They still have to be located and are a
separate series. The two must not be joined into one line without a visible
break.

**Changes over time.** In 2019 CDC changed from reporting by survey year
(children 19 to 35 months old at interview) to birth year (coverage by age 24
months). The survey frame also changed: landline only through 2010, landline
plus cell 2011 to 2017, cell only from 2018.

**Suppressed, censored or masked values.** Estimates with a wide interval or
small sample are flagged or withheld (codes to be confirmed in the method
report).

**Uncertainty.** A state's sample is a few hundred children a year. Ohio's
single-year MMR samples are 207 to 292, with intervals about 6 points either
side. A one-year move of 3 or 4 points in one state is inside the noise. The
viz shows the interval on hover and prefers the two-year pooled estimates.

**License and attribution.** Public domain. Credit CDC, National Immunization
Survey-Child (ChildVaxView).

---

## Vaccination coverage and exemptions among kindergartners (CDC, `ijqb-a7ye`)

Status: file only. The SchoolVaxView method notes still have to be read.

**What it is.** Each state's own count or survey of kindergartners meeting the
school vaccine requirement, by vaccine, plus exemption rates. Reported by the
states to CDC.

**Where it comes from.** `https://data.cdc.gov/api/views/ijqb-a7ye/rows.csv`.

**Coverage.** School years 2009-10 to 2025-26. Vaccines: MMR, DTP/DTaP/DT,
polio, hepatitis B, varicella. Some state-years are blank (Ohio 2010-11).

**Changes over time and known quirks.** This is not one survey. Each state
uses its own method, shown in `Survey Type` (census, sample, voluntary
response) with `Percent Surveyed` beside it, and methods change from year to
year within a state. What counts as "covered" follows each state's own school
requirement, so the number of doses differs between states. Comparing two
states is weaker than comparing one state with itself over time. Footnote
marks in `Footnotes` carry these differences and have to be decoded.

**Uncertainty.** None published. A census with 95% surveyed is solid; a
voluntary response with 30% surveyed is not. The viz shows the survey type
and percent surveyed on hover.

**License and attribution.** Public domain. Credit CDC, SchoolVaxView.

---

## State population and personal income, table SAINC1 (Bureau of Economic Analysis)

Status: file and footnotes read. BEA's regional methodology paper still to read.

**What it is.** For each state and year: total personal income, population, and
personal income per resident. Population is the Census Bureau's midyear
estimate, which BEA republishes.

**Where it comes from.** `https://apps.bea.gov/regional/zip/SAINC.zip`, file
`SAINC1__ALL_AREAS_1929_2025.csv`. No key needed for the bulk file.

**Version and vintage.** Last updated September 30, 2026, with revised
statistics for 2009 to 2025.

**Coverage.** 1929 to 2025, 50 states and DC. Alaska and Hawaii have no figures
before 1950, so they have no rate before 1950 on the page.

**Changes over time.** Population for census years and the years between is
revised after each census (intercensal estimates). The latest years are
postcensal estimates and will be revised.

**Missing data.** `(NA)` is not available, `(NM)` not meaningful. Both become
empty, never zero.

**Units and rounding.** Persons; dollars per person in current dollars, **not
adjusted for inflation**. The page says so next to the figure. A dollar figure
from 1950 cannot be compared with one from 2020 without a price index, and we
do not show one adjusted series yet.

**Uncertainty.** None published. Early-year state populations are estimates
between censuses.

**License and attribution.** Public domain. Credit U.S. Bureau of Economic
Analysis and U.S. Census Bureau.

---

## County-level MMR vaccination rates (Johns Hopkins, Dong et al.)

Status: files and README read. The JAMA paper's methods (doi:10.1001/jama.2025.8952) still to read.

**What it is.** The share of children with 2 MMR doses by county and school
year, gathered by the authors from each state's health department.

**Where it comes from.** `github.com/enshengdong/MMR_data`, files
`mmr_data_us_counties_v2.csv` (the rates) and `mmr_data_sources_v2.csv` (per
state: years, unit, age group, origin, link). The two file names read as if
swapped; the contents are as described here.

**Version and vintage.** v2, repository last changed September 28, 2026.

**Coverage.** School years 2017-18 to 2024-25. 16,380 county-years in 45
states. Counties with a figure grow from 982 (18 states) in 2017-18 to 2,712
(44 states) in 2024-25, so an early year's map is mostly empty and that is a
fact about publication, not about vaccination. Alaska reports by health region
(7 rows, not mappable to counties, left out). Five states have no county figure.

**Changes over time and known quirks.** Not one survey. 40 states report
kindergartners, 4 report K-12, 1 pre-K to 12, 1 a registry of 5 to 6 year
olds. Four states publish by school and the authors rolled these up to
counties. One state's requirement and counting rule differs from the next.
Compare a county with itself over time or with its own state, not across
state lines.

**Suppressed values.** Small counties are withheld by some states; these are
simply absent.

**Uncertainty.** None published.

**License and attribution.** **No license file in the repository.** The data is
public and tied to a JAMA paper. Before publication we need to either confirm
terms with the authors or drop the county layer. Cite: Dong E, Saiyed S,
Nearchou A, Okura Y, Gardner LM. Trends in County-Level MMR Vaccination
Coverage in Children in the United States. JAMA. 2025.

---

## County measles cases, 2025 on (Johns Hopkins Measles Tracking Team)

Status: file and README read.

**What it is.** Lab-confirmed measles cases by county and report date, compiled
from state and county health departments and verified news reports.

**Where it comes from.** `github.com/CSSEGISandData/measles_data`, file
`measles_county_all_updates.csv`. Updated Fridays; pulled with data through
September 25, 2026.

**Coverage.** January 2025 on. Only counties with at least one case. The build
sums by calendar year of the report date; the page shows 2025 only (2026 is
unfinished).

**Known quirks.** Dates are report dates, not illness dates. Kansas withholds
counts under five by county, Oklahoma gives no county, Tennessee reports by
region; those cases sit in "unknown county" rows and do not appear on a county
map. The 2025 county sum (2,285) is close to but not the same as CDC's
provisional state sum for 2025 (2,026 in our weekly extract); the two are
different compilations and neither is final.

**Revisions.** Earlier dates are revised as investigations finish.

**License and attribution.** CC BY 4.0. Cite "JHU Measles Tracking Team Data
Repository at Johns Hopkins University".

---

## State NIS estimates by survey year, 1995 to 2017, and national surveys before 1995

Status: read. Full notes, with each definition change quoted from its source,
are in `data/raw/vax_history/NOTES.md`; rebuilt by `scripts/04b_fetch_vax_history.py`.

**What it is.** (1) CDC's yearly table of vaccination coverage among children
19 to 35 months by state, from the National Immunization Survey, with 95%
intervals. (2) National-only figures before that: the U.S. Immunization Survey
(1959 to 1985, children 1 to 4) and the National Health Interview Survey (1991
to 1994). (3) The year each vaccine was first licensed.

**Where it comes from.** 1995 to 2014: CDC's "coverage by state" workbooks,
which survive only as Internet Archive captures of the original cdc.gov files
(2000 is still on CDC's server). 2015 to 2017: tables in each year's survey
user's guide and MMWR. Before 1995: Simpson, Ezzati-Rice and Zell, "Forty years
and four surveys", Am J Prev Med 2001, Table 1, **from a copy on a personal
website, not the publisher**, and Health, United States 1995. Licensure years:
CDC Pink Book chapters and MMWR.

**Coverage.** MMR 1+, DTP/DTaP 4+ and polio 3+ for all 51 areas in every year
1995 to 2017. Hepatitis A 2+ from 2008 (no state figures for 2016). No national
figure exists for 1986 to 1990. **No state figure exists before 1995.**

**Changes over time.**
- From 2019 CDC reports by birth year and by age 24 months instead of by survey
  year. The two are different measures. The page ends the survey-year line at
  2017 and starts the birth-year line with children born in 2016, drawn at the
  year they reach the age measured, with a gap between.
- Phone sample: landline only through 2010, landline and cell from 2011, cell
  only from 2018. CDC says 2012 on is not directly comparable with earlier years.
- "DTP" through 2005, "DTaP" from 2006; both count DTP, DTaP and DT doses.
- The pre-1995 surveys count 3+ DTP doses, not 4+, and took the parent's word
  without checking records. The authors say this understated coverage, by as
  much as 23%. A "don't know" answer added in 1976 breaks the series there.

**Checks run.** Two CDC workbooks per year, 4,316 cells, none differ. U.S. row
against MMWR 2004 to 2017, 66 cells, none differ. Pre-1995 figures confirmed
against Health, United States for 1970 to 1976 and 1983 to 1985; **1959 to 1969
and 1977 to 1982 have no second source.**

**Known quirks.** 1970 polio is 65.9 in two sources and 77.5 in a third; 65.9
is used. Polio drops from 87.6 (1964) to 73.9 (1965) as printed.

**Uncertainty.** A state's 95% interval is typically 3 to 5 points either
side. CDC calls intervals wider than 10 points possibly unreliable.

**License and attribution.** CDC material is public domain. The Simpson table
is a journal article; we use the numbers with citation.

---

## State indicators and party control

Status: read. One section per series, in the full template, is in
`data/raw/kpi/NOTES.md`; rebuilt by `scripts/08b_fetch_kpis.py`.

| Shown on the page | Source | Years | Trap |
|---|---|---|---|
| Median household income, 2025 dollars | Census CPS table H-8 | 1984 to 2025 | 2013 and 2017 printed twice after survey changes; we use the version that matches later years |
| Poverty rate | Census CPS historical table 19 | 1980 to 2025 | same doubled years; one state's two 2013 figures differ by 7 points, mostly sampling noise |
| Bachelor's degree or more, 25 and older | Decennial census 1940 to 2000; ACS 1-year 2005 to 2024 | census years, then yearly | no 2020 ACS; different surveys |
| Without health insurance | CPS 1987 to 2007 (two series), ACS 2008 to 2024 | 1987 to 2024 | three surveys, not spliced; ACS and CPS differ by up to 5 points in the same year |
| Share of jobs: manufacturing, government, farming | BEA SAEMP25 | 1969 to 2022 | table discontinued in 2024; industry classes change in 2001 |
| Party control | Klarner 1937 to 2011; Ballotpedia 2012 on | 1937 to 2025 | change of source and of definition at 2012 |

Built but not shown: unemployment rate (BLS, 1976 on), current-dollar income.

**Party control.** One field per state-year: Democratic, Republican, Divided,
or Nonpartisan legislature (Nebraska throughout; Minnesota 1937 to 1974). The
two sources agree on all but 10 of 1,000 state-years in their 1992 to 2011
overlap. They define a split chamber differently (no seat majority in one,
ties and coalitions in the other). Ballotpedia's reuse terms have to be
checked before publication. This is shown as a fact about the year and nothing
on the page relates it to disease or vaccination.

**Uncertainty.** Survey figures for small states carry wide margins; the
publisher's standard errors are kept in the extract's `note` column.

---

## Milestones

`data/milestones_national.json` and `data/milestones_pilot_states.json`. Not a
dataset from one publisher. Each entry has a URL that was fetched, a headline
copied from that page, and the date checked. Method and the list of events
wanted but not verified are in `data/MILESTONES_NOTES.md`.
