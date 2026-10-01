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
"Measles, Indigenous" and "Measles, Imported" (sum for the total); "Hepatitis
A, Confirmed"; "Poliomyelitis, paralytic" and "Poliovirus infection,
nonparalytic". To be checked against the label list for each year.

**Suppressed, censored or masked values.** Flag columns carry marks: `-` (no
reported cases), `N` (not reportable in that state), `U` (unavailable), `NN`
(not nationally notifiable), `NP` (not a reporting priority, to be confirmed
in the table notes). `N` and `U` are not zero and are shown as "no data".

**Missing data.** See flags. A blank count with `-` is a zero by CDC's note.

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

Status: not yet pulled. Being extracted into `data/raw/bridge/` with its own
`NOTES.md`; this section is completed from that before any of it is charted.

**What it is.** The final yearly count of each notifiable disease by state.
Printed each year in MMWR as the "Summary of Notifiable Diseases" (1952 to
2015), then as "NNDSS Annual Tables" (2016 on).

**Why we need it.** State-level measles is not in Tycho after 2001 and not in
the current weekly file before 2021. The other diseases need 2018 to 2020.

**Known traps so far.** The tables moved in January 2025 from CDC WONDER to
CDC Stacks and data.cdc.gov; WONDER's old menu is a stub and blocks scripted
requests. Some years exist only as PDF tables, so every extracted disease-year
is checked against the table's own US total row.

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

## Not yet pulled (placeholders)

Nothing from these may be charted until its section is written out in full.

- **State population by year** (Census Bureau intercensal and postcensal
  estimates, 1900 on) for rates per 100,000.
- **State NIS estimates by survey year, 1995 to about 2017** (CDC yearly
  tables) for the earlier vaccination line.
- **National vaccination before 1995** (United States Immunization Survey,
  1959 to 1985). National only. No state figures exist for these years.
- **County kindergarten MMR coverage** (Johns Hopkins, 2017-18 to 2023-24,
  38 states) and **county measles cases 2025 on** (Johns Hopkins
  `CSSEGISandData/measles_data`).
- **State KPIs**: BEA per-capita personal income (1929 on) and employment by
  industry; Census median household income, poverty, education, health
  insurance.
- **Party control of state government**: Klarner, State Partisan Balance Data
  1937 to 2011 (Harvard Dataverse); Ballotpedia trifectas 1992 on.
- **Milestones** (`data/milestones_*.json`): not a dataset from one publisher.
  Each entry carries its own URL and the date it was checked.
