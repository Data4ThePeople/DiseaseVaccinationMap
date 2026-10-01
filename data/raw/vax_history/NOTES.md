# Vaccination coverage history: sources, definitions, gaps

Built by `scripts/04b_fetch_vax_history.py` on October 1, 2026. Every number in
the three CSV files is parsed from a file in `src/`. The script types in no
values. `qa_checks.txt` is the check log the script writes on every run.

Words used below: "verified" means a check was run against a second downloaded
file. "Inferred" means it is my reading and no second file confirms it.

## 1. Files

| File | Rows | What it holds |
|---|---|---|
| `nis_state_survey_year.csv` | 4,896 | National Immunization Survey (NIS), children 19 to 35 months, survey years 1995 to 2017, 50 states, DC and the United States |
| `national_pre1995.csv` | 149 | National only: United States Immunization Survey (USIS) 1959 to 1985, National Health Interview Survey (NHIS) 1991 to 1994 |
| `licensure.csv` | 19 | Year each vaccine was first licensed, one row per source sentence |
| `qa_checks.txt` | | Check log |
| `src/` | 87 files, 20 MB | Every downloaded source |

Columns in `nis_state_survey_year.csv`: `ci_half_width` is filled when the
publisher prints "estimate ± x". `ci_low` and `ci_high` are filled when the
publisher prints a range. Neither is computed from the other. An empty
`estimate` means the publisher printed no number; the reason is in `flag`.

## 2. Sources by survey year (part A)

| Survey years | Vaccines | Source | Format |
|---|---|---|---|
| 1995 to 1999, 2001 to 2014 | MMR 1+, DTP 4+, polio 3+; DTP 3+ except 2005 to 2008; hepatitis A 2+ from 2008 | CDC table "Estimated Vaccination Coverage with Individual Vaccines and Selected Vaccination Series Among Children 19-35 Months of Age by State", one workbook per year. CDC removed these from cdc.gov. The copies are Internet Archive captures of the original cdc.gov URLs (2014 and 2015 captures). | xls, xlsx |
| 2000 | same | Same CDC table, still served at `ftp.cdc.gov/pub/vaccines_nis/00/antigen_state.xls` | xls |
| 2015, 2016, 2017 | MMR 1+, DTaP 4+, polio 3+ | Appendix Table F.7 of the NIS-Child public-use-file user's guide for each year (CDC and NORC). The 2015 guide is an Internet Archive capture. | PDF |
| 2015 | hepatitis A 2+ | MMWR 65(39), Table 3 | HTML |
| 2017 | hepatitis A 2+ | MMWR 67(40), Supplementary Table 2, stacks.cdc.gov/view/cdc/59415 | PDF |
| 2005 to 2008, 2015 to 2017 | DTP 3+, United States row only | Table 1 of the MMWR report on survey year 2008 (`mmwr_nis2008.htm`) and of MMWR 67(40) on 2017 | HTML |
| 2016 | hepatitis A 2+, United States row only | MMWR 67(40) Table 1 | HTML |

The exact URL of every file is in the `source_url` column and in the script.

The lead in the task brief was partly wrong. The 2017 user's guide does not
hold state tables for 1995 to 2017. It holds one state table for 2017 (Table
F.7) and one national series for 1995 to 2017 (Table G.4). The pages on
archive.cdc.gov list the yearly tables but every file link reads "Not
available". The files themselves survive only in the Internet Archive.

## 3. Coverage grid: states with an estimate, of 51 (50 states and DC)

| Years | MMR 1+ | DTP 4+ | DTP 3+ | Polio 3+ | Hep A 2+ |
|---|---|---|---|---|---|
| 1995 | 51 | 51 | 51 | 51 | not measured |
| 1996 | 51 | 51 | 50 | 51 | not measured |
| 1997 to 2004 | 51 | 51 | 51 | 51 | not measured |
| 2005 to 2007 | 51 | 51 | 0 (US only) | 51 | not measured |
| 2008 | 51 | 51 | 0 (US only) | 51 | 51 |
| 2009 to 2014 | 51 | 51 | 51 | 51 | 51 |
| 2015 | 51 | 51 | 0 (US only) | 51 | 51 |
| 2016 | 51 | 51 | 0 (US only) | 51 | 0 (US only) |
| 2017 | 51 | 51 | 0 (US only) | 51 | 51 |

The United States row is present for every vaccine in every year it was
measured.

## 4. What could not be obtained

- **DTP 3+ by state, 2005 to 2008 and 2015 to 2017.** CDC left the column out
  of the state table in those years. The national figure is in the file,
  flagged "national figure only".
- **Hepatitis A 2+ by state, 2016.** The MMWR report on 2016 has no state
  table. It sends readers to ChildVaxView Interactive, which drew its data
  from `ndmsia.cdc.gov`. That server no longer answers and the Internet
  Archive did not capture the 2016 hepatitis A view.
- **Hepatitis A 2+ before 2008.** Not measured for this age group. The 2008
  table says: "Prior years of hepatitis A data among 19-35 months of age is
  not available."
- **1996 Rhode Island, DTP 3+.** The cell is empty in both CDC workbooks for
  1996. The MMWR report on 1996 (file `mmwr_nis1996.htm`) prints
  "100 (+/-0.1%)" for that cell. The row is in the CSV with no estimate. I did
  not fill it from MMWR because the MMWR figures for that year are whole
  numbers from an earlier estimate (see 6.4).
- **Confidence interval for the 1996 Rhode Island cell, and for nothing else.**
  Every other state cell carries its interval.
- **Survey year 1994** (April to December 1994, the first NIS). Not requested
  and I found no CDC table file for it. MMWR printed it (listed in
  `method_nis_articles_list.html`).
- **National figures for 1986 to 1990.** Simpson et al., Table 2, footnote:
  "No nation-level data are available for 1986 through 1990."
- **Territories.** Guam, Puerto Rico and the U.S. Virgin Islands appear in some
  years and are dropped. CDC excludes them from the United States estimate.
- **A licensure year for diphtheria toxoid.** See section 9.

## 5. Uncertainty the publisher states

- CDC's technical notes for these tables (file `method_nis_tech_notes.html`):
  national estimates "have much smaller (less than ± 1%) confidence intervals,
  and are more precise than state or local area estimates." "State estimates
  with a CI half-width greater than 10 may be unreliable, but are reported and
  marked by a footnote."
- Measured in this file: the median state 95% confidence interval half-width,
  all five vaccines pooled, runs from 3.3 to 5.0 percentage points depending on
  the year. The widest single state cell is ± 10.8 (2013 Virginia, hepatitis
  A). Two state cells exceed ± 10, both hepatitis A in 2013 (Georgia ± 10.1,
  Virginia ± 10.8). The year-by-year table is in `qa_checks.txt`.
- So a state value of 90 with a half-width of 4 is a range of 86 to 94. Most
  year-to-year moves for one state are inside that range.
- The survey design aims for the same precision in every estimation area (a
  coefficient of variation of about 7.5%, 2017 user's guide, section 2), so
  small states are not less precise than large ones by design.
- Suppression rule, as printed on the tables. 2002 to 2006 and 2008:
  "Estimate=NA (Not Available) if the unweighted sample size for the numerator
  was <30 or (CI half width)/Estimate > 0.5 or (CI half width) >10." 2007:
  denominator under 30 or ratio above 0.6 or half-width above 10. 2009:
  denominator under 30 or ratio above 0.6. 2010 to 2012: denominator
  under 30 or ratio above 0.588 or half-width above 10. 2013 and 2014:
  denominator under 30 or ratio above 0.588, and "Estimates with confidence
  intervals >20 may not be reliable." The 1995 to 2001 tables print no rule.
  No state cell for these five vaccines is marked NA in any year.

## 6. Definitions and how they change

### 6.1 Who is counted and when
- Children aged 19 to 35 months at the time of the household interview. Each
  survey year therefore mixes about 28 months of births. The tables print the
  birth window: 1995 survey, born February 1992 to May 1994; 2005, February
  2002 to July 2004; 2014, January 2011 to May 2013. From the 2011 survey the
  window starts in January, before that in February (CDC technical notes).
- Status is taken on the interview date, not at a fixed age. MMWR 68(41) says
  the survey-year estimates "on average, assessed vaccination by age 27.5
  months."
- Estimates rest on vaccination histories reported by the child's providers.
  The 1995 MMWR report describes provider data being used "to adjust responses
  for the entire group of children surveyed." The 1999 report says "Children
  with provider data were weighted to represent all children surveyed." These
  are two different estimation methods. I did not find the document that dates
  the switch.

### 6.2 The 2019 switch from survey year to birth year
- MMWR 68(41), October 18, 2019 (file `method_mmwr_birth_year_2019.htm`):
  "With this report, CDC has transitioned to reporting NIS-Child data by birth
  year rather than survey year." Coverage is now "by age 24 months", estimated
  with the Kaplan-Meier method, pooling several survey years per birth year.
- The same report: "estimates by birth year might be slightly lower for some
  vaccines than were estimates by survey year." And: "Trends in vaccination
  coverage by birth year and survey year are similar."
- Consequence for this project: `nis_state_survey_year.csv` (survey years 1995
  to 2017) and `data/raw/cdc/fhky-rtsk.csv` (birth years 2011 to 2022) are two
  different measures. They overlap for children born 2011 to 2016, who sit in
  survey years 2012 to 2017. A chart that joins them needs a visible break.
  Hepatitis A is the extreme case: MMWR 67(40) gives 2+ doses as "75.3% versus
  39.6%" by age 35 months versus 24 months for children born January 2012.

### 6.3 Telephone sample frame
- 1995 to 2010: landline telephones only. Table G.4 of the 2017 guide: "Prior
  to 2011, estimates are single-frame, landline-sample estimates. From 2011
  onward, estimates are dual-frame (landline plus cell-phone) estimates."
- 2011: cell phones added, 11% of the unweighted sample. 2012: about half.
  The MMWR report on 2012 (`mmwr_nis2012.htm`): "estimates are not directly comparable between years
  because NIS methods were changed" and the 2012 estimates "should be
  considered a baseline against which subsequent trends in coverage can be
  evaluated."
- 2018 onward (outside this file): cell phones only (MMWR 68(41)).
- Households with no telephone are never interviewed. Weights adjust for them.
  The 2017 guide: "some bias might remain."

### 6.4 Measles: "MCV" versus "MMR"
- The CDC tables for 1995 to 2005 carry this footnote on the measles column:
  "One or more doses of measles-mumps-rubella vaccine; previous reports of
  vaccination coverage were for measles-containing vaccine (MCV)." From 2006
  the footnote reads only "1 or more doses of measles-mumps-rubella vaccine."
- MMWR at the time reported MCV. Verified: the MMWR notice on 1998 (`mmwr_nis1998.htm`,
  Table 1 for 1995 to 1998) prints MCV 89.9, 90.7,
  90.5 and 92.1 for 1995 to 1998. The CDC tables print MMR 89.8, 90.6, 90.4 and
  92.0. The MMR figure is 0.1 point lower in each year.
- The combined series (4:3:1 and longer) still count any measles-containing
  vaccine. Those series are not in this file.
- The `mmr_1` column is therefore MMR in every year. It is not the MCV figure
  MMWR printed for 1995 to 1998.

### 6.5 The 1995 to 1997 tables were re-estimated after MMWR printed them
- Verified: for 1995 the CDC table gives DTP 3+ 94.5, DTP 4+ 78.4, polio 87.8.
  The MMWR notice on 1998 gives 94.7, 78.5, 87.9. For 1996 and 1997 the gaps are 0.1 or
  zero. For 1998 the non-measles figures match exactly.
- The archived table pages say "Content on this page kept for historical
  reasons" and were last reviewed in December 2001. Inferred: CDC regenerated
  the 1995 to 2000 table set around 2001 with one method, which is why they are
  uniform in layout and differ slightly from the MMWR of the day.
- The MMWR reports for 1995 to 1997 print whole numbers.

### 6.6 DTP, DTaP and DT
- The column is headed "4+DTP" through 2005 and "4+DTaP" from 2006. The
  footnote is the same idea throughout: doses of "any diphtheria and tetanus
  toxoids and pertussis vaccines including diphtheria and tetanus toxoids, and
  any acellular pertussis vaccine (DTP/DTaP/DT)". So a dose of DT, which has no
  pertussis part, counts in every year. The 2013 table words the 4-dose
  footnote as DTaP only; the 2014 table restores the wider wording in its
  abbreviations note. Inferred: the measure did not change in 2013, only the
  footnote.
- Vaccine keys `dtp_3` and `dtp_4` cover all of these.

### 6.7 Polio
- "Three or more doses of any poliovirus vaccine" in every year, oral or
  inactivated.

### 6.8 Hepatitis A
- First published for 19 to 35 months in the 2008 survey. The 2008 footnote:
  ACIP "expanded the recommendation of administering hepatitis A vaccine from
  ≥24 months to children aged 12-23 months in May 2006."
- Many children in the 19 to 35 month window have not yet had time for the
  second dose. MMWR 67(40): "Coverage with ≥2 HepA doses was higher by age 35
  months than by age 24 months (e.g., 75.3% versus 39.6% for children born
  January 2012)." The 2+ figure in this file (40.4 in 2008, 59.7 in 2017) is
  low partly for that reason.

### 6.9 Other changes
- Children with no vaccinations: "Starting with the 2002 NIS-Child public-use
  data file, the definition of children with adequate provider data was
  expanded to include unvaccinated children" (2017 guide, section 2). The guide
  says the effect on state estimates is small.
- 2012: "beginning in 2012 all children with any provider-reported vaccination
  data are considered to have adequate provider data" (2017 guide). Table G.4
  marks 2012 for this.
- 2006: the table says "2006 estimates based on NIS dataset which was
  re-released on February 25, 2008 after correcting for Hispanic overcount in
  9 states." The file here is the corrected one.
- Sub-state areas changed over time (78 areas in 1994, 56 from 2007). State
  totals are not affected: "the geographic strata are nested within state."
- 2009 United States row carries the mark ¥: "US National estimates include the
  50 States plus DC, and exclude the Virgin Islands."

### 6.10 Marks kept in the `flag` column
| Flag | Meaning on the source table |
|---|---|
| `mark ***` (US DTP 3+, 1995 to 2001) | "% ± 95% Confidence Interval". A layout note, not a warning. |
| `row mark ¥` (US, 2009) | US excludes the Virgin Islands |
| `mark §§` (2015 hepatitis A, 6 states) | "Statistically significant increase in coverage compared to 2014 (p<0.05)" |
| `mark ††` (2017 West Virginia hepatitis A), `mark §` (2016 US DTP 3+) | Statistically significant change from the year before |
| `typo in source cell` (2009 Iowa hepatitis A) | The cell reads "47.8±7 .0". Read as 47.8 ± 7.0. |
| `cell is empty in the source table` | 1996 Rhode Island DTP 3+ |
| `national figure only...` | No state table carries this vaccine that year |

## 7. Sanity checks and what they found

All in `qa_checks.txt`.

1. **Two CDC workbooks per year.** For 1995 to 2014 the "by state" workbook was
   compared with the "by state and urban area" workbook, 4,316 cells. Zero
   differ.
2. **PDF extraction.** Table F.7 (PDF) was compared with the MMWR state table
   for MMR 1+ and DTaP 4+: 104 cells for 2015, 104 for 2017. Zero differ. The
   2016 Table F.7 has no second state source. Its United States row matches
   both Table G.4 and MMWR.
3. **Range.** No estimate outside 0 to 100. No half-width above 10.8. No
   estimate outside its own printed range. No duplicate rows. Lowest
   non-hepatitis-A state value is above 65.
4. **United States row against Table G.4 of the 2017 guide**, 69 cells. One
   differs: 2007 MMR is 92.3 in the CDC table and 93.2 in Table G.4. Table 1
   of the MMWR report on 2008 also prints 92.3 for 2007. Inferred: Table G.4 has two digits swapped.
   The file uses 92.3.
5. **United States row against MMWR.** 2004 to 2017: 66 cells against Table 1
   of the MMWR reports on 2008, 2012 and 2017, zero differ. 1995 to 1998:
   against the MMWR notice on 1998, differences of 0 to 0.2 as described in 6.4 and 6.5.
   1997 to 2003: the MMWR national tables are images. I read
   `mmwr_nis2001_table1.gif` and `mmwr_nis2003_table1.gif` by eye. All 1998 to
   2003 cells for DTP 3+, DTP 4+, polio and MMR match the file, with one
   exception: the 2003 report image appears to print 83.8 for 1999 DTP 4+,
   while the 2001 report image, the CDC table and Table G.4 all print 83.3. The
   image is low resolution. The file uses 83.3. For 1997 the image shows 95.5,
   81.5, 90.8, 90.5 against 95.4, 81.5, 90.7, 90.4 in the file (see 6.5).

Odd items, all listed above: 1996 Rhode Island empty cell; 2009 Iowa typo; 2007
Table G.4 swap; 1999 DTP 4+ in one MMWR image; 1995 to 1998 revisions.

## 8. Before 1995 (part B)

### Sources
- **USIS, children 1 to 4 years, 1959 to 1985**: Simpson DM, Ezzati-Rice TM,
  Zell ER. "Forty years and four surveys: how does our measuring measure up?"
  Am J Prev Med 2001;20(4S):6-14, Table 1. The authors were at CDC. The copy
  downloaded is from a personal website, not from the publisher. I did not
  fetch the publisher's copy, so the Health, United States checks below are
  the only official confirmation. Polio 3+ 1959 to 1985, DTP 3+ 1962 to 1985, measles
  1964 to 1985, rubella 1970 to 1985, mumps 1973 to 1985.
- **USIS, children 24 to 35 months, 1979 to 1985**, and **NHIS 1991**: same
  paper, Table 2.
- **NHIS, children 19 to 35 months, 1992 to 1994**: NCHS, Health, United
  States, 1995, Table 54, Total column (DTP 3+, polio 3+, measles-containing).
- Check sources, both official NCHS: Health, United States, 1978, Table 36
  (USIS 1970 to 1976) and Health, United States, 1986, Table 34 (USIS 1970,
  1976, 1983 to 1985). Only the one page of each is kept in `src/` because the
  full scans are 36 MB and 98 MB.

### Checks
- Simpson Table 1 against Health US 1986 Table 34: 24 cells, 23 equal. The one
  difference is polio 1970: Simpson 65.9, Health US 1986 77.5. Health US 1978
  prints 65.9. The file uses 65.9 and flags the cell.
- Simpson Table 1 against Health US 1978 Table 36, 1970 to 1976: measles,
  rubella, DTP and polio all match (7 of 7 each). Mumps 3 of 4 by machine: the
  scan's text layer reads 46.3 for 1976 where the page image shows 48.3. I
  looked at the page image. It matches.
- This check also settles which column the fourth number in Simpson's 1970 to
  1972 rows belongs to (rubella, not mumps). The script places numbers by
  their position on the page, and Health US 1978 confirms it: "Mumps
  vaccination was first reported in 1973."
- NHIS 1992 and 1993: Simpson Table 2 and Health US 1995 Table 54 give the same
  six figures. Simpson labels them 24 to 35 months, Health US labels them 19 to
  35 months. The file takes 1992 to 1994 from Health US with its label, and
  1991 from Simpson with a flag on the age label.
- Not checked against a second source: 1959 to 1969 and 1977 to 1982 (Simpson
  only).

### Definitions and warnings
- The USIS asked parents. "Answers based on either memory (recall) or an
  immunization record kept in the home were accepted without further
  validation" (Simpson). No provider records.
- Simpson, Table 1 footnote: the data are "known to underestimate coverage
  rates." In the text: the USIS "underestimated the true vaccination rate in
  preschoolers by as much as 23% for some antigens." Health US 1986 shows the
  size for 1985: measles 60.8 for all respondents and 76.9 for respondents who
  consulted a record; DTP 3+ 64.9 and 87.0.
- Break in 1976. Health US 1986: "Beginning in 1976, the category 'don't know'
  was added to response categories. Prior to 1976, the lack of this option
  resulted in some forced positive answers, particularly for vaccinations
  requiring multiple dose schedules, that is, polio and DTP." Simpson: results
  "before 1976 were not considered directly comparable to those obtained in
  later years."
- Odd, as printed: polio 3+ falls from 87.6 in 1964 to 73.9 in 1965, and the
  1965 polio and DTP figures are the same number (73.9). Simpson's text confirms
  the 1964 peak of 87.6. No second source for 1965.
- The age group is 1 to 4 years, not 19 to 35 months. Measles, mumps and
  rubella are one dose; DTP and polio are 3 or more doses.
- These three surveys do not form one series. USIS (parent recall, ages 1 to
  4), NHIS (household interview, 19 to 35 months) and NIS (provider records, 19
  to 35 months) measure different things in different ways. The jump from 60.8
  (measles, USIS 1985) to 82.5 (NHIS 1992) to 89.8 (NIS 1995) is partly method.
- No state figures exist for these years.

## 9. Licensure (part C)

One row per source sentence, with the sentence in `source_quote`. Sources are
the CDC Pink Book chapters (cdc.gov/pinkbook) and MMWR.

| Vaccine | Year | Date stated | Note |
|---|---|---|---|
| Inactivated polio (Salk) | 1955 | no | Pink Book and MMWR "Achievements in Public Health, 1900-1999" agree |
| Oral polio (Sabin) | 1961 | no | Monovalent types 1 and 2. Type 3 in 1962, trivalent in 1963 (separate row). |
| Measles | 1963 | no | Two sources agree |
| Mumps | 1967 | no | Two sources agree |
| Rubella | 1969 | no | Two sources agree |
| Combined MMR | 1971 | no | Pink Book |
| Whole-cell pertussis | 1914 | no | Pertussis vaccine alone |
| Whole-cell DTP | 1948 | no | The source says DTP was "available" in 1948. It does not say "licensed". |
| Acellular DTaP | 1991 | December 17, 1991 | Fourth and fifth doses only. First licensed for infants July 31, 1996 (separate row). |
| Hepatitis A | 1995 | February 1995 | Three sources agree on the year. No source read gives the day. |
| Diphtheria toxoid | 1923 | no | **Not a licensure year.** Table 1 of MMWR "Achievements in Public Health, 1900-1999" marks 1923 as "Vaccine developed (i.e., first published results of vaccine usage)". The Pink Book says only "Diphtheria toxoid developed in 1920s". I found no official page that gives a licensure year. |

For a chart, the year a vaccine was licensed is not the year children started
getting it widely. The DTaP rows show this: licensed in 1991, but only for the
booster doses until 1996.

## 10. Re-running

`.venv/bin/python scripts/04b_fetch_vax_history.py`. Files already in `src/`
are not fetched again. A cold run downloads about 160 MB (two Health, United
States scans, cut down to one page each) and takes a few minutes. The script
needs `xlrd`, `openpyxl`, `PyMuPDF`, `beautifulsoup4` and `lxml` in the venv.
Internet Archive URLs carry their capture timestamp, so they return the same
bytes each time.
