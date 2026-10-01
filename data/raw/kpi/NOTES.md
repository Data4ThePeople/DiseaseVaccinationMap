# State KPIs and party control: source notes

Built by `scripts/08b_fetch_kpis.py` on 2026-10-01. Every source file is in
`data/raw/kpi/src/`. Outputs:

- `kpi_state_year.csv` (22,899 rows): series, variant, state, year, value, unit, flag, note, source_url, source_file
- `party_control.csv` (4,590 rows): one row per state and year, 1937 to 2026
- `party_control_overlap.csv`: Klarner and Ballotpedia side by side, 1992 to 2011
- `party_control_ncsl_check.csv`: the 2012-on rows checked against NCSL's dated tables

How to read `kpi_state_year.csv`:

- `value` is empty when the publisher printed a mark instead of a number. The mark is in `flag`.
- `flag` also carries the publisher's footnote number for that year, in parentheses.
- `note` carries the footnote text, the publisher's standard error (`se=`) or 90 percent margin of error (`moe90=`), and for computed shares both inputs.
- When the publisher prints a year twice, both rows are kept. The plain `variant` (for example `cps_asec`) then has no row for that year, and two rows appear with a suffix (for example `cps_asec__2013_traditional_income_questions` and `cps_asec__2013_redesigned_income_questions`). A chart has to choose one on purpose. To continue the older line, use the "traditional" 2013 row and the "legacy" 2017 row. To match later years, use the "redesigned" 2013 row and the "updated" 2017 row. That reading comes from the publisher's footnotes quoted below.
- The federal sites carried a notice on the download date: "Due to a lapse in appropriations, this website is not being updated."

Summary of what was built:

| series | variant | years | state-years | empty |
|---|---|---|---|---|
| median_household_income | current_dollars (+4 twin variants) | 1984-2025 | 2,244 | 0 |
| median_household_income | 2025_dollars (+4 twin variants) | 1984-2025 | 2,244 | 0 |
| poverty_rate | cps_asec (+4 twin variants) | 1980-2025 | 2,448 | 0 |
| bachelors_or_higher_25plus | decennial_census | 1940-2000, every 10 years | 357 | 4 |
| bachelors_or_higher_25plus | acs_1yr | 2005-2024, no 2020 | 969 | 0 |
| uninsured_rate | cps_asec_original_HI4 (+4 twin variants) | 1987-2005 | 1,071 | 0 |
| uninsured_rate | cps_asec_HIA4 | 1999-2009 | 561 | 0 |
| uninsured_rate | cps_asec_HIB4 | 1999-2012 | 714 | 0 |
| uninsured_rate | acs_1yr_HIC4 | 2008-2024 | 867 | 51 (all of 2020) |
| employment_share_manufacturing / farm / government | SIC | 1969-2001 | 1,683 each | 0 |
| employment_share_manufacturing / farm / government | NAICS | 1998-2022 | 1,275 each | 10 (manufacturing only) |
| unemployment_rate | laus_annual_average | 1976-2025 | 2,550 | 0 |

---

## 1. Median household income

**What it is.** Median money income of households, by state, before taxes, not counting noncash benefits. Table H-8 of the Census Bureau's Historical Income Tables.

**Where it comes from.** Current Population Survey, Annual Social and Economic Supplement (CPS ASEC), a household sample survey taken each spring that asks about income in the prior calendar year. File: `census_h08.xlsx` from <https://www2.census.gov/programs-surveys/cps/tables/time-series/historical-income-households/h08.xlsx>. Footnotes: `census_income_cps_historic_footnotes.html`.

**Version and vintage.** Table title "Median Household Income by State: 1984 to 2025", source line "1985 to 2026 Annual Social and Economic Supplements". Footnote page last revised August 18, 2026.

**Coverage.** 50 states and DC, income years 1984 to 2025. No state table exists in this series before 1984.

**Changes over time.** From the publisher's footnotes, by income year:
- 1984 (19): Hispanic weighting controls, 1980 census sample design introduced. 1985 (20): top recording limit for earnings raised, 1980 design fully in place. 1987 (21): new processing system. 1992 (22): 1990 census population controls. 1993 (23): paper to computer-assisted interviewing, and changed recording limits. 1994 (24), 1995 (25): 1990 census sample design, a 7,000 household sample cut. 1999 (29): 2000 census controls. 2000 (30): 28,000 household sample expansion. 2004 (revised): weights corrected. 2009 (36): top income interval for medians raised to $250,000. 2010 (37): 2010 census controls.
- **2013 is printed twice.** (38) is the part of the sample (about 68,000 addresses) that got income questions like the 2013 survey. (39) is the part (about 30,000 addresses) that got the redesigned income questions.
- **2017 is printed twice.** The unmarked 2017 is the older processing system. (40) "reflect the implementation of an updated data processing system ... and should be used to make comparisons to 2018 and subsequent years."
- 2020 (41): 2020 census controls. 2024 (42): Vintage 2025 population controls.
- Size of the twin-year gaps in this file: 2013 redesigned minus traditional, median across states +$1,510, range -$8,510 (MS) to +$11,740 (WY). 2017 updated minus legacy, median -$130, range -$3,880 (WA) to +$5,760 (AK). Most of that spread in small states is sampling noise, because the two 2013 rows come from different households.

**Suppressed or masked values and their codes.** The footnote page defines N (not available), B (base less than 75,000), X (not applicable), Z (zero or rounds to zero). None appears in the state cells of this table.

**Missing data.** None for 1984 to 2025.

**Revisions.** The whole table is reissued each September. Back years can change: the footnote page says "all estimates have undergone additional rounding. As a result, this year's estimates may differ from previous publications."

**Units and rounding.** Dollars. Two variants: `current_dollars`, and `2025_dollars`, which is the publisher's own inflation adjustment. Price year is 2025. The publisher's header and footnote 28 say it uses the Chained CPI-U (C-CPI-U) for 2000 on and the R-CPI-U-RS before 2000. Values are rounded by the publisher to four significant digits (for example 85150, 102500).

**Known quirks.** Footnote 28 on the web page still says "between 2000 and 2022" while the table header says 2000-2025. The 2004 column is labelled "2004 (revised)" with no number; the matching text is footnote 35.

**Uncertainty.** The table prints a standard error for every cell, kept as `se=` in `note`. From 2010 on these come from replicate weights. As a share of the estimate, the median standard error over all years runs from about 1.7 percent (California) to about 4.5 percent (Connecticut); the largest single cell is 9.7 percent (Maine, 2018). A 90 percent margin of error is about 1.645 times the standard error. Year-to-year moves in small states are often inside that margin.

**License and attribution.** U.S. government work, public domain. Cite: U.S. Census Bureau, Current Population Survey, 1985 to 2026 Annual Social and Economic Supplements, Historical Income Table H-8.

---

## 2. Poverty rate

**What it is.** Percent of people below the official poverty threshold, by state. Table 19 of the Historical Poverty Tables: People.

**Where it comes from.** CPS ASEC. File: `census_hstpov19.xlsx` from <https://www2.census.gov/programs-surveys/cps/tables/time-series/historical-poverty-people/hstpov19.xlsx>. Footnotes: `census_poverty_cps_historic_footnotes.html`.

**Version and vintage.** "Number of Poor and Poverty Rate by State: 1980 to 2025". Footnote page last revised August 28, 2026.

**Coverage.** 50 states and DC, 1980 to 2025. Table 19 has single years. (Table 21 on the same site holds 3-year averages from 2004 on and was not used.)

**Changes over time.** Same survey history as income, with poverty-table footnote numbers: 1981 (19) three technical changes to the poverty definition; 1984 (18); 1985 (17); 1987 and 1988 (16) new processing system; 1991 (15); 1992 (14) 1990 census controls; 1993 (13) computer-assisted interviewing; 1994 (12); 1995 (11); 1999 (10) 2000 census controls; 2000 (9) sample expansion; 2004 (8) weights corrected; 2010 (7) 2010 census controls; 2020 (3) 2020 census controls; 2024 (2) Vintage 2025 controls.
- **2013 is printed twice.** (6) is the traditional-question sample (about 68,000 addresses). (5) is the redesigned-question sample (about 30,000).
- **2017 is printed twice.** Unmarked is the older processing system. (4) is the updated system, "should be used to make comparisons to 2018 and subsequent years."
- Gap sizes in this file: 2013 redesigned minus traditional, median -0.1 point, range -4.2 (RI) to +7.2 (OK). 2017 updated minus legacy, median +0.1, range -2.3 (AK) to +1.3 (NJ).

**Suppressed or masked values and their codes.** (B) base less than 75,000; (N) not applicable or not available; (Z) rounds to zero. None appears in the percent column.

**Missing data.** None for 1980 to 2025.

**Revisions.** Reissued each September; see the rounding statement under income.

**Units and rounding.** Percent, one decimal.

**Known quirks.** The column header cites footnote "(29)" for the margin of error, but on the footnote page the margin-of-error text is number 30 and number 29 is about work experience. The year footnotes line up correctly. The table has no United States row.

**Uncertainty.** A 90 percent margin of error is printed for every cell, kept as `moe90=`. "MOEs ... for years through 2003 are based on standard errors calculated using generalized variance function (GVF) parameters. MOEs for 2004 and beyond are based on standard errors calculated using replicate weights." Median margin by state runs from 1.0 point (California) to 3.1 points (New Mexico). The largest is 7.7 points (DC, 1984). Early-1980s margins for small states are 6 to 7 points (Alaska 1980: 9.6 percent plus or minus 7.1).

**License and attribution.** Public domain. Cite: U.S. Census Bureau, Current Population Survey, Annual Social and Economic Supplements, Historical Poverty Tables, Table 19.

---

## 3. Bachelor's degree or more, age 25 and older

**What it is.** Percent of the population 25 and older with a bachelor's degree or higher.

**Where it comes from.** Two sources, kept as two variants.
- `decennial_census`: Census 2000 PHC-T-41, "A Half-Century of Learning", Table 6a. File `census_phct41_table06.csv` from <https://www2.census.gov/programs-surveys/decennial/2000/phc/phc-t-41/table06.csv>.
- `acs_1yr`: American Community Survey 1-year data profile DP02, through the Census API (`https://api.census.gov/data/{year}/acs/acs1/profile`). One JSON per year, `census_acs1_dp02_{year}.json`, plus the variable list `census_acs1_dp02_{year}_variables.json`. The API key was used for the request and is not stored.

**Version and vintage.** PHC-T-41 internet release April 6, 2006. ACS files as served by the API on 2026-10-01.

**Coverage.** Decennial: 1940, 1950, 1960, 1970, 1980, 1990, 2000. ACS: 2005 to 2024 except 2020. The 2025 ACS 1-year was not on the API on the download date. There is no state figure in these sources between census years before 2005, so the line has ten-year gaps until then.

**Changes over time.**
- The decennial question changed from years of school completed (1940 to 1980) to highest degree (1990 on). PHC-T-41 presents them as one series; the table itself does not mark the change. This is general knowledge about the census, not something read in the downloaded file.
- "1950 to 2000 data based on a sample" (table header); 1940 is from the full count.
- Decennial to ACS is a change of survey. Do not splice. Median state step from 2000 (census) to 2005 (ACS) is +2.6 points over five years.
- ACS 2005 covered households only. "Group quarters data were collected beginning in 2006" (`doc_census_acs_comparing_2014_5yr.html`).
- "New questions were added to the 2008 ACS" for educational attainment (same page). They concern college credit below a degree; the page urges caution in comparisons across 2008.
- The variable holding the figure moves: DP02_0016E (2005), DP02_0066E (2006 to 2007), DP02_0067E or PE (2008 to 2018), DP02_0068PE (2019 on). The script finds it by label each year and asserts exactly one match.
- 2019 to 2021: the median state rises 1.9 points across the missing 2020, against 0.5 the year before. Vermont rises 5.7. This is what the publisher's files say; the cause was not looked into here.

**Suppressed or masked values and their codes.** Decennial: `--` for Alaska and Hawaii in 1940 and 1950, "because they were not states at that time." ACS: none met.

**Missing data.** 2020: the Census Bureau did not release standard ACS 1-year products (footnote in the HIC-4 table: "As a result of disruptions to data collection stemming from the COVID-19 pandemic"). No rows are written for 2020 in this series.

**Revisions.** PHC-T-41 is static. ACS 1-year estimates are not revised after release.

**Units and rounding.** Percent, one decimal.

**Known quirks.** `census_phct41_table06.csv` holds only the both-sexes panel although the web page calls it Table 6; the file calls it Table 6a.

**Uncertainty.** Decennial: no error margins are printed. ACS: 90 percent margin of error kept as `moe90=`. Median by state 0.2 point (Florida) to 1.2 points (Wyoming); largest 1.7 (Wyoming, 2021).

**License and attribution.** Public domain. Cite: U.S. Census Bureau, Decennial Census of Population, 1940 to 2000 (PHC-T-41); U.S. Census Bureau, American Community Survey 1-year estimates, Table DP02. Census asks API users to state: "This product uses the Census Bureau Data API but is not endorsed or certified by the Census Bureau."

---

## 4. People without health insurance

**What it is.** Percent of people with no health insurance coverage. Four separate series. They are different surveys or different processing of the same survey. They are not spliced.

**Where it comes from.**
- `cps_asec_original_HI4`: CPS ASEC, Table HI-4, 1987 to 2005. `census_orghihistt4.txt`.
- `cps_asec_HIA4`: CPS ASEC, Table HIA-4, 1999 to 2009. `census_hihistt4.xls`.
- `cps_asec_HIB4`: CPS ASEC, Table HIB-4, 1999 to 2012. `census_hihistt4b.xls`.
- `acs_1yr_HIC4`: ACS 1-year, Table HIC-4_ACS, 2008 to 2024. `census_hic04_acs.xlsx`.
All under <https://www2.census.gov/programs-surveys/demo/tables/health-insurance/time-series/>. Series pages saved as `census_hi_series_page_*.html`.

**Version and vintage.** HI-4 source line: 1988 to 2006 supplements. HIA: released March 2007 and extended to 2009. HIB: released September 13, 2011 and extended to 2012. HIC-4_ACS: internet release 9/11/2025.

**Coverage.** 50 states and DC in every series. Census publishes no state CPS table after 2012: the HHI series that replaced HIB (2013 on, 2017 on) has national tables only. So CPS state coverage is 1987 to 2012 and ACS is 2008 to 2024.

**Changes over time.**
- CPS asks in spring whether a person had coverage at any time in the prior calendar year. ACS asks about coverage at the time of the interview, all year round. That is the known break between them. Where both exist (2008 to 2012), ACS minus HIB has a median of -0.6 point but ranges from -5.4 (DC, 2009) to +4.9 (OK, 2008).
- HI-4 footnotes: 1987 (2/) new processing system; 1991 (3/); 1992 (4/) 1990 census controls; 1993 (5/) computer-assisted interviewing; 1994 (6/) "Health insurance questions were redesigned"; 1997 (7/) people whose only coverage is the Indian Health Service counted as uninsured from the March 1998 survey; 2000 (9/) sample expansion.
- **1999 is printed twice in HI-4.** Unmarked, and (8/) "Estimates reflect the results of follow-up verification questions and of Census 2000 based population controls." The verification question lowers the rate: median -0.9 point, range -2.1 (SC) to -0.2 (AR).
- **2004 is printed twice in HI-4.** Unmarked, and (15/) "revised based on improvements to the algorithm that assigned coverage to dependents, and there was an adjustment to the weights." Median -0.1 point.
- HIA: "The 2005 and 2006 [CPS ASEC] data were revised in March 2007 ... Because the data after the revision is not consistent with earlier data, the Census Bureau introduced a new historical series (HIA-1 to HIA-8) and discontinued the original series. The data for 1999 to 2003 ... were revised using an approximation method." HIA minus original, 2000 to 2005: median -0.5 point.
- HIB: "On September 13, 2011, the Census Bureau released revised estimates ... Data from the 2000-2010 [CPS ASEC] have been revised." HIB minus HIA, 1999 to 2009: median -0.5 point.
- ACS: "Data was not available prior to 2008" (`doc_census_acs_comparing_2014_5yr.html`). Universe is the civilian noninstitutionalized population.

**Suppressed or masked values and their codes.** `(B)` appears in standard-error cells (DC 2005 in HI-4) and is kept as `se=(B)`; the percent itself is printed. ACS 2020 cells hold `N` with footnote 2; `flag` is `N; (2)` and value is empty.

**Missing data.** ACS 2020, all 51. Nothing else.

**Revisions.** The three CPS series are frozen. HIC-4_ACS is reissued each September with one more year.

**Units and rounding.** Percent. HI-4, HIA and ACS: one decimal. HIB is published unrounded (for example 24.607289738) and is stored as published.

**Known quirks.** HIB marks 2010 with footnote (10), which the series page does not define. HIA's United States row for 2008 has a typo, "15,4"; national rows are not loaded. In the HI-4 text file "District of / Columbia:" is split over two lines.

**Uncertainty.** CPS tables print standard errors (`se=`): median by state 0.5 point (Pennsylvania) to 1.5 (DC) in HI-4. HIB standard errors use replicate weights. ACS prints 90 percent margins (`moe90=`): median 0.1 point (California) to 1.0 (Wyoming).

**License and attribution.** Public domain. Cite: U.S. Census Bureau, Current Population Survey, Annual Social and Economic Supplements (Health Insurance Historical Tables HI-4, HIA-4, HIB-4); U.S. Census Bureau, American Community Survey 1-year estimates (HIC-4_ACS).

---

## 5. Employment mix: manufacturing, farm, government

**What it is.** Share of total employment in three groups. Computed here as BEA line / BEA total x 100. Both inputs are in `note` (`num=`, `den=`).
- Total: "A count of jobs, both full-time and part-time. It includes wage and salary jobs, sole proprietorships, and individual general partners, but not unpaid family workers nor volunteers."
- Farm (line 70): "the number of workers engaged in the direct production of agricultural commodities ... whether as a sole proprietor, partner, or hired laborer."
- Manufacturing: line 400 (SIC division D) or line 500 (NAICS 31-33).
- Government and government enterprises: line 900 (SIC) or 2000 (NAICS). Federal civilian, military, state and local. "It includes the military."

**Where it comes from.** BEA regional table SAEMP25, "Total full-time and part-time employment by industry": SAEMP25S (SIC) and SAEMP25N (NAICS). **BEA discontinued this table on September 27, 2024** "due to budget constraints" (BEA notice, Survey of Current Business, August 2024). The live bulk zip no longer contains it and `https://apps.bea.gov/regional/zip/SAEMP.zip` returns a web page. The data here are BEA's own archived release: `bea_archive_0324pistate_SAINC.zip` from <https://apps.bea.gov/regional/histdata/releases/0324pistate/SAINC.zip>, which BEA's "Discontinued or Delayed Statistics" page links as the archive for SAEMP25.

**Version and vintage.** Archive release of March 2024. SAEMP25N: "Last updated: September 29, 2023-- new statistics for 2022; revised statistics for 2002-2021." SAEMP25S: "Last updated: March 6, 2019-- revised statistics for 1969-2001."

**Coverage.** 50 states and DC. SIC 1969 to 2001. NAICS 1998 to 2022. **The series ends in 2022 and will not be extended.**

**Changes over time.**
- SIC: "1969-74 are based on the 1967 [SIC]. 1975-87 are based on the 1972 SIC. 1988-2001 are based on the 1987 SIC."
- NAICS: "1998-2006 are based on the 2002 [NAICS]. 2007-2010 ... 2007 NAICS. 2011-2016 ... 2012 NAICS. 2017 forward ... 2017 NAICS."
- **SIC to NAICS break.** Both classifications are published for 1998 to 2001, and both are kept (`variant` = `SIC` or `NAICS`). In those four years the farm and government shares are identical in the two. The manufacturing share is lower under NAICS in every state: median -0.7 point, from -0.1 (Hawaii) to -3.4 (Delaware, 1998). BEA's definition file says "Manufacturing" "does not have the same definition in both systems."

**Suppressed or masked values and their codes.** "(D) Not shown to avoid disclosure of confidential information; estimates are included in higher-level totals." "(T) Estimate for employment suppressed to cover corresponding estimate for earnings." "(NA) Not available." In the lines used here only (D) occurs: 10 manufacturing cells under NAICS (AK 2020; DC 2002, 2017, 2020, 2021, 2022; HI 2021; WY 2002, 2017, 2022). Value is empty, `flag` = `(D)`.

**Missing data.** Nothing before 1969 in this table. Nothing after 2022.

**Revisions.** None from here on; the table is closed. Before that BEA revised back years each September.

**Units and rounding.** Percent of total employment, rounded here to three decimals. Inputs are whole numbers of jobs.

**Known quirks.** These are jobs, not people: a person with two jobs counts twice. Jobs are counted where the work is, so DC's government share (27.5 percent in 2022) reflects commuters. BEA notes nonfarm proprietors are "largely on a place-of-residence basis."

**Uncertainty.** BEA publishes no error margins. The estimates are built mostly from administrative records.

**License and attribution.** Public domain. Cite: U.S. Bureau of Economic Analysis, Regional Economic Accounts, Table SAEMP25 (discontinued), archive release of March 2024.

---

## 6. Unemployment rate

**What it is.** Annual average unemployment rate: unemployed as a percent of the civilian labor force, people 16 and older.

**Where it comes from.** BLS Local Area Unemployment Statistics (LAUS), "States and selected areas: Employment status of the civilian noninstitutional population, 1976 to 2025 annual averages." `bls_staadata.zip` (holds `staadata.xlsx`) from <https://www.bls.gov/lau/staadata.zip>. Method pages: `doc_bls_laumthd.htm`, `doc_bls_launews1.htm`, `doc_bls_notescps.htm`. The BLS API key was not needed.

**Version and vintage.** File dated March 23, 2026 inside the zip.

**Coverage.** 50 states and DC, 1976 to 2025. The file also has Los Angeles County and New York City, which are dropped.

**Changes over time.** State figures are not direct survey counts. "Estimates for states are derived from signal-plus-noise models that use the monthly employment and unemployment measures tabulated from the Current Population Survey (CPS) as the primary inputs," with payroll employment and unemployment insurance claims as further inputs, and are forced to sum to the national CPS totals. BLS re-estimates the whole history with the current method, so the file has no marked break.

**Suppressed or masked values and their codes.** None.

**Missing data.** None. **2025 carries footnote (1): "Annual estimates for 2025 are 11-month averages that exclude October. Data for October 2025 were not collected due to the federal government shutdown."** `flag` = `(1)` on all 51 rows for 2025.

**Revisions.** "Each year, historical estimates ... are revised to reflect new population controls from the Census Bureau, updated input data, and re-estimation." The latest revision was issued April 8, 2026. Expect small changes to recent years next spring.

**Units and rounding.** Percent, one decimal.

**Known quirks.** Annual averages are of not-seasonally-adjusted months.

**Uncertainty.** This file prints no error ranges. BLS notes that state CPS sub-samples "range from approximately 500 to 4,600 households," which is why it models state figures; it publishes 90 percent intervals elsewhere (Geographic Profile), not loaded here.

**License and attribution.** Public domain. Cite: U.S. Bureau of Labor Statistics, Local Area Unemployment Statistics.

---

## 7. Party control of state government

**What it is.** For each state and year: the governor's party, which party controlled the state senate and the state house, and a derived `trifecta` field. A plain record of who held office.

Values:
- `governor`: Democratic, Republican, Other (a governor not of either major party), or empty.
- `senate`, `house`: Democratic, Republican, Split, Nonpartisan, or empty.
- `trifecta`: "Democratic" or "Republican" when the governor and both chambers are that party; "Nonpartisan legislature" when legislators were elected without party labels; "Divided" for every other complete case; empty when the source is missing a piece.
- The source's own code for every field is repeated at the start of `flag` (for example `klarner codes: govparty_c=0.5, sen_cont_alt=0.5, hs_cont_alt=1`), so nothing is lost by the wording above.

**Where it comes from.**
- 1937 to 2011: Carl Klarner, "State Partisan Balance Data, 1937 - 2011", Harvard Dataverse, doi:10.7910/DVN/LZHMG3. Data file `klarner_Partisan_Balance_For_Use2011_06_09b.xlsx`; codebooks `klarner_Partisan_Balance_For_Use2012_10_18_Codebook.docx` and `klarner_StatePartisanBalance1934to2011_SourceFiles_2011_05_24_Codebook.doc`; source file `klarner_StatePartisanBalance1934to2011_SourceFiles_2011_05_24.xlsx` (used for its `partisan_elections` column).
- 2012 to 2026: Ballotpedia, "Party control of [State] state government", one page per state, `ballotpedia_party_control_{ST}.html`. Each page has a table of Governor, Senate and House by year from 1992. Method page: `ballotpedia_who_runs_the_states_methodology.html`.
- Check only: NCSL "State & Legislative Partisan Composition" yearly PDFs for 2015 to 2021 and 2025 (`ncsl_Legis_Control_{year}.pdf`). NCSL's PDFs for 2012 to 2014 and 2022 to 2024 were not found on its server (the guessed file names return 404 and its web page shows only the current year), which is why Ballotpedia is the source for 2012 on.

**Version and vintage.** Klarner: Dataverse version 1, released 2013-02-26. Ballotpedia: pages as of 2026-10-01. NCSL: each PDF prints its own date (for example "As of Jan. 25, 2015", "FINAL (Feb. 1, 2021)", "29-Aug-25").

**Coverage.** 50 states, 1937 to 2026. Nothing before 1937: Klarner's file has rows for 1934 to 1936, but no governor is coded in them and only a handful of chamber codes are filled, so they are not loaded. His rows for 2012 to 2015 are empty. 2026 is flagged "year in progress when downloaded". DC has a row for every year with all fields empty and `flag` = "not a state: no state government".

**What date in the year (`as_of`).**
- Klarner: `year` is the "year of legislative session", from the view of the party in government: a chamber won in the 1982 election is coded from 1983. Chamber control uses the `_cont_alt` variables, where a chamber that changed hands mid-session is "coded as the party in control when the budget was passed." No calendar date is given. **The codebook does not say what date the governor's party refers to** ("How these scores were arrived at (excepting those of the governor) is described in this code book").
- Ballotpedia: "the partisan affiliation of the governor or governors who held the office for the majority of each year"; a legislature is a party's "when one party had majority control in both legislative chambers for most of a given year." That text is written for 1992 to 2013. That the same rule is applied to later years is an inference.
- NCSL: a snapshot on the date printed on each PDF.

**How ties, coalitions and independents are coded.**
- Klarner chamber: 1 Democratic, 0 Republican, 0.5 "split control". Before 1959 the code is from seat counts only (0.5 = neither party has a majority of seats). From 1959, if a party has more than 50 percent of seats it is coded for that party; otherwise control is decided from the party of the chamber leader and of committee chairs, and 0.5 means tied seats with shared arrangements. Legislators who are not Democrats or Republicans are counted as "ind" and are in the seat total, so a party can be the largest and still be coded 0.5. Klarner 0.5 is written as `Split` here.
- Klarner governor: 1 Democrat, 0 Republican, 0.5 "non-major party governor". Written as `Other` here. 31 state-years, for example Minnesota 1937-38 and 1999-2002, Maine 1975-78 and 1995-2002, Connecticut 1991-94, Alaska 1991-94.
- Ballotpedia chamber: D, R, or S. A chamber is a party's when it "had majorities or at least functional control (due [to] a tie-breaking lieutenant governor or coalitions with allied legislators outside of the party)". S is used "when one legislative chamber was run according to a bipartisan power-sharing agreement or by a bipartisan coalition instead of the regular party leadership." Written as `Split` here. So the two sources define the middle category differently. Example: Alaska's House is S for 2019 to 2026 and its Senate S for 2023 to 2026 in Ballotpedia.
- Ballotpedia governor: D, R, or I. I is written as `Other`.
- Three Ballotpedia cells carry a footnote, kept in `flag`: Mississippi Senate 2007, Washington Senate 2017, West Virginia governor 2017 (party changes during the year).
- NCSL: "This is based on the number of members of each party, and does not take into account coalitions that might change effective control."

**Nonpartisan legislatures.**
- Nebraska: every year 1937 to 2026 is `Nonpartisan legislature`. It has one chamber; it is put under `senate`, and `house` is empty. Klarner's source file sets `partisan_elections=0` for Nebraska in every year; Ballotpedia prints "-".
- Minnesota: 1937 to 1974 is `Nonpartisan legislature`, because Klarner's source file sets `partisan_elections=0` for both chambers in those years. For 1951 to 1974 Klarner still records seat counts and a control code for the two caucuses; those codes are kept in `flag` ("klarner still codes caucus control senate=..., house=...") but are not used for `trifecta`. Klarner flags both chambers as partisan from 1975. Whether the Minnesota Senate's first election with party labels came later than the House's was not checked against a Minnesota source.

**Suppressed or masked values and their codes.** None.

**Missing data.** 49 state-years outside DC have an empty `trifecta` because Klarner has no code for some piece: Alaska 1937 to 1958 and Hawaii 1937 to 1959 (no governor coded; Klarner does code the territorial legislatures in some of those years), Alabama and Maryland 1937 to 1938 (no chamber codes).

**Revisions.** Klarner's file is frozen. Ballotpedia pages are edited over time; the saved HTML is the record of what was used.

**Units and rounding.** Not applicable.

**Known quirks and how the sources agree.**
- Overlap of Klarner and Ballotpedia, 1992 to 2011, 1,000 state-years (`party_control_overlap.csv`): the governor differs in 4, the senate in 17, the house in 9. 28 state-years differ on at least one office. The derived `trifecta` differs in 10.
  - Governor: AK 1994 (Klarner Other, Ballotpedia Republican), AR 1996 (Republican, Democratic), FL 2010 (Republican, Other), VA 2010 (Democratic, Republican). AR 1996 and FL 2010 are years with a change during the year.
  - Chambers: most differences are a `Split` in one source against a party in the other (AK Senate 2009-11, VA Senate 1998-99, NC House 2003-04, TN Senate 2007-08, MT House 2009), which follows from the different definitions above. Opposite-party differences: AK Senate 2007-08, AZ Senate 1992, LA Senate 2011, MS Senate 2011, TN Senate 1996, TN House 2009, VT House 1992, WI Senate 1996 and 1998.
  - Trifecta: AK 2007, AK 2008, AR 1996, AZ 1992, FL 2010, LA 2011, NC 2003, NC 2004, WI 1996, WI 1998.
  - The two are not fully independent: Ballotpedia says it "cross-checked our data for the years through 2011 with the legislative partisan balance data compiled by ... Dr. Carl Klarner."
- Ballotpedia against NCSL, 2015 to 2021 and 2025, 400 state-years (`party_control_ncsl_check.csv`): governor differs in 1, legislature in 10, state control in 9.
  - Alaska 2017 to 2021 and 2025: Ballotpedia has the House as S (coalition); NCSL counts seats and prints Republican. For 2019, 2020, 2021 and 2025 that makes Ballotpedia `Divided` and NCSL Republican.
  - Connecticut 2017 and 2018: Senate tied 18 to 18; Ballotpedia D (NCSL's own note: "LG Wyman (D) casts tie-breaking votes"), NCSL "Split*".
  - New York 2017 and Washington 2017: Ballotpedia has the Senate as R; NCSL prints "Dem*" with the note "controlled by coalition w/Rs functional control".
  - Louisiana 2016: NCSL's table dated Jan. 29, 2016 prints a Republican governor; Ballotpedia has Democratic for 2016, and NCSL's 2017 table prints Dem.
- Ballotpedia's headline count for 2026 ("23 Republican trifectas, 16 Democratic trifectas, and 11 divided governments") includes Nebraska with the Republican count. This file has 22 Republican, 16 Democratic, 11 Divided, 1 Nonpartisan legislature for 2026.
- California, New Jersey and New York call the lower chamber "Assembly" on Ballotpedia; it is stored under `house`.
- The join year 2011 to 2012 is a change of source and of definition. A change in a state's value between 2011 and 2012 should be checked in `party_control_overlap.csv` before it is shown as a change of control.

**Uncertainty.** No error margins apply. The uncertainty is definitional: which date, and what counts as control. The disagreement counts above are the measure of it.

**License and attribution.** Klarner: CC0 1.0 on Dataverse. He asks: "Klarner, Carl E. 2003. 'Measurement of the Partisan Balance of State Government.' State Politics and Policy Quarterly 3 (Fall): 309-19," plus the dataset. Ballotpedia: cite "Ballotpedia, Party control of [State] state government, accessed October 1, 2026" with the page URL; its reuse terms were not checked here and should be before publishing. NCSL: used only as a check; cite "National Conference of State Legislatures, State Partisan Composition" if mentioned.
