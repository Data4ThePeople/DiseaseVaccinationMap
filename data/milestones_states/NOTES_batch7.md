# Milestones batch 7: research notes

Checked 2026-10-01. States: PA (7 items), RI (6), SC (6), SD (8), TN (6), UT (7). Total 40.

## How each item was verified

Every URL was fetched in this session with `curl` and the user agent `Mozilla/5.0 (D4TP research; eric@data4thepeople.com)`. PDFs were downloaded and read with a text extractor (pypdf). Each `headline` was copied from the page's own `<h1>`, `citation_title` tag, on-page heading, or the PDF's printed heading.

A script then loaded all six files, checked the keys, `scope`, `kind`, date formats and duplicate (date, headline) pairs, re-fetched every URL, and confirmed the stored headline appears in the page. Result: 39 of 40 passed by string match. The one exception is noted below (RI 2006 PDF).

Web search stopped working partway through the session (the session search budget ran out, and DuckDuckGo, Bing and Brave either blocked or returned unusable results to scripted requests). After that, sources were found through the MMWR yearly index pages (1982 to 1998), the CDC site search API, PubMed E-utilities title searches, the Internet Archive CDX index of state health department sites, and by stepping through neighboring CDC Stacks record numbers. This is the main reason some well-known events are in "wanted, not verified".

## Sites that blocked or failed

- `stacks.cdc.gov/gsearch` (Stacks search): 403. Record pages and PDFs fetch fine.
- `pubmed.ncbi.nlm.nih.gov` record pages: cookie wall. PubMed E-utilities API works.
- PMC article PDFs and the Europe PMC PDF renderer: 403. PMC record pages fetch fine.
- `nytimes.com`: 403. `npr.org`: connection failed.
- `scdhec.gov`: no response (the agency was split up in 2024). Internet Archive captures used.
- `tn.gov/health/news/...`: old news release URLs return 404. Internet Archive captures used.
- `law.justia.com`: 403.
- `sdlegislature.gov/Statutes/13-28-7.1`: the public page is built by script and returns only "Loading..." to curl. The JSON uses the legislature's own static rendering of the same section, `sdlegislature.gov/api/Statutes/13-28-7.1.html`, which opens as a normal page in a browser.

## Internet Archive captures used

- RI 2006-10-10 `Pertussis Alert` (health.ri.gov PDF, captured 2009-06-19)
- SC 2015-09-22 `DHEC: DHEC vaccinates more than 3,700 ...` (captured 2018-09-30)
- SC 2018-10-30 `DHEC Confirms Measles in Spartanburg County Resident` (captured 2018-11-01)
- SC 2019-05 `DHEC Identifies Spread of Hepatitis A as Statewide Outbreak` (captured 2019-06-01)
- SD 2014-12-31 `Measles` (doh.sd.gov disease page, captured 2015-01-01)
- TN 2018-11-14 `TDH Continues Response to Hepatitis A Outbreak` (captured 2019-01-09)
- TN 2019-04-18 `TDH Confirms First Tennessee Measles Case for 2019` (captured 2019-04-20)

## Headlines that are awkward as display headlines

- PA 2017 `School Immunizations`. Bare rulemaking title from the Pennsylvania Bulletin (47 Pa.B. 1300).
- PA 1981 `Epidemiologic Notes and Reports A Continuing Measles Outbreak among School-Age Children Despite an Outbreak-Control Program with School Exclusion -- Pennsylvania`. Very long, with the MMWR section prefix.
- PA 2024 `Health Department Update on Measles Outbreak – January 18`. No year and no city in the headline. The en dash is in the source.
- RI 1998 `§ 16-38-2. Immunization.` Bare statute heading.
- RI 2025 `Measles Case Identified in Rhode Island / Identifican caso de sarampión en Rhode Island`. The release title is bilingual on the page.
- RI 2006 `Pertussis Alert`. Generic. The memo's subject line is "Pertussis Cases on the Rise".
- SC 1993 `SECTION 44-29-180. School pupils and day care center children to be vaccinated or immunized; department to monitor immunization records of children in day care; exemptions and exclusions.` Bare statute heading, very long.
- SC 2015 `DHEC: DHEC vaccinates more than 3,700 to help prevent spread of hepatitis A in Upstate`. The doubled "DHEC" is on the page.
- SD 1971 `Immunizations required for admission to school or early childhood program--Exceptions--Rules.` Statute catchline.
- SD 2014 `Measles`. Generic disease page title.
- SD 1996 `Toxigenic Corynebacterium diphtheriae -- Northern Plains Indian Community, August-October 1996`. Does not name South Dakota. The body does.
- TN 1936 `Poliomyelitis in Tennessee` and TN 1981 `Epidemiologic Notes and Reports Rubella Outbreak among Foreign- Exchange Students -- Tennessee` (the stray space after "Foreign-" is on the page).
- UT 1951 `THE EPIDEMIOLOGY OF POLIOMYELITIS—A Study of an Outbreak in Payson, Utah, 1951`. All capitals and an em dash, both as on the page.
- UT 2017 `H.B. 308 Public Health and Schools`. Bare bill title.
- UT 2025 `Public health officials warn of first measles case in Utah, media availability today`. Carries a press-logistics tail.

## Dates and other judgment calls (things inferred rather than stated outright)

- RI statute, `date` 1998. The page gives the current text and a history note ending "P.L. 1998, ch. 34, § 1". 1998 is the last amendment year listed. The page does not say what changed that year, and the blurb does not claim it. This follows the pilot's Ohio statute item (dated at the current version). A separate source, the 1981 Public Health Reports article used for the 1979 outbreak, says "In 1970, the State adopted a law requiring immunization of students entering school for the first time", but the statute's history note lists 1968 and 1969 session laws, not 1970. If the editor prefers, drop this item or move it.
- SC statute, `date` 1993. Same approach: the history note ends "1993 Act No. 35, SECTION 1" and the page does not say what changed. The URL is the whole chapter page (Title 44, Chapter 29); the reader has to scroll to Section 44-29-180.
- SD statute, `date` 1971. The source note reads "SL 1971, ch 141; SL 1972, ch 97; ...". The blurb says the law "traces to a 1971 session law". That 1971 is the first enactment is an inference from the source note, and the diseases listed are from the current text, not the 1971 text.
- TN 1978 law. The Public Health Reports article opens by saying the law "was enacted ... in April 1978" and amended a 1967 law. Later the same article says "Public Chapter 922, enacted on April 27, 1977" and gives an October 2, 1977 deadline, while also describing work that began in January 1978 and the 1978-79 school year. The 1977 dates look like misprints in the article. The JSON uses 1978-04 from the opening sentence. Worth a second look by the editor.
- TN 1936. Thin source: the PMC record shows only the title, author, journal, date and a footnote that the paper was read on November 19, 1935. The blurb says only that. `date` is the publication month.
- UT 1951 and SD 1985. PMC record pages with an abstract; the blurbs use only the abstract.
- UT 2017 H.B. 308. The headline, signing date (24 Mar 2017) and effective date (1 Jul 2018) are on the bill page. The description of what the bill does comes from the enrolled bill PDF (`le.utah.gov/~2017/bills/hbillenr/HB0308.pdf`), which was also fetched.
- SC 2019 hepatitis A. The archived release has no release date on the page. `date` is 2019-05 because the release cites counts through May 10, 2019; `published` is null. A search snippet gave May 13, 2019, which was not confirmed on the page.
- SC 2015 hepatitis A. The archived URL slug says 2018-03-20 (a site migration date). The release itself is dated September 22, 2015, and that is the date used.
- SC 2026-04-27 (end of the Upstate measles outbreak, 997 cases) falls after the 1929 to 2025 range in the brief. It is included because it closes the 2025 outbreak and the pilot has 2026 items. Drop it if the range is strict.
- SD 2014. `date` is 2014-12-31, the "as of" date for the case count on the archived page. The page does not name Mitchell. It says five of six cases were Davison County residents.
- SD 1986-12-18 is the onset date of the first reported mumps case. UT 1996-04-09, PA 1981-09-09 and TN 2016-04-15 are the first dates of the periods the reports cover. PA 1963-01 is the month of the first Berks County clinic. RI 1979-01-17 is the day the first case was reported to the health department (some cases began in late November 1978).
- PA 1991-02 (Philadelphia measles). The source is a 2015 retrospective by 6abc, so `kind` is "history page". The page says the outbreak began in October 1990; February 1991 is when it reports the school count and the cluster of deaths.
- PA 2003 hepatitis A. `date` is the MMWR issue date (2003-11-28). The count is as of November 20.
- `published` is null where the page gives only a month or issue (Public Health Reports "1981 May-Jun", "1981 Jan-Feb", "Jun 1958"; PMC "1955 Apr", "1936 Feb", "1990 Sep"; Rhode Island Medical Journal February 2013) or no date at all (statutes, SD 2014 page).
- PA 1965 `published` is 1965-05-19 and RI 1967 is 1967-05-01, as CDC Stacks lists them.
- `diseases` on law and rule items (PA 2017, RI 1998, SC 1993, UT 2017) are a best fit. The RI and SC statutes and the Utah bill page do not list diseases by name. The SD statute and the TN article do.
- RI 2006 `Pertussis Alert`: the PDF's text layer returns the heading with each letter doubled ("PPeerrttuussssiiss AAlleerrtt"), a common artifact of bold type, so the script's string match failed on this one item. No PDF page renderer was available on this machine, so this heading was read from the text layer and not checked by eye on a rendered page. The rest of the PDF text (date, "Re: Pertussis Cases on the Rise", the count of 50) extracts normally.
- RI 2011 Rhode Island Medical Journal PDF: heading matched by script against the PDF text.
- RI 2025 page is served as ISO-8859-1; the headline matches once decoded that way.

## Wanted, not verified (left out)

Pennsylvania:

- May 2019 state declaration of a hepatitis A outbreak. The release could not be located without search.
- 1991 court order to vaccinate children in the Philadelphia outbreak. New York Times (1991) and NPR (2015) pages were blocked or unreachable.
- When Pennsylvania first required school vaccinations, and the origin of the religious and moral or ethical exemptions (24 P.S. § 13-1303a). The Department of Education circular was fetched and names the exemptions but gives no enactment dates.
- The August 1, 2017 effective date of the school immunization rule. Seen in a search snippet, not found in the Bulletin text.
- 1979 polio outbreak among the Amish in Lancaster County; 1980 measles in Montgomery County (MMWR 1981, before the HTML archive); 1983 pertussis rise. PubMed titles only.

Rhode Island:

- The 1970 school immunization law as its own item (see the statute note above).
- 1953, 1955 and 1960 polio outbreaks (Rhode Island Medical Journal titles in PubMed only).
- The 1963 statewide End Polio campaign (mentioned inside the 1967 article only).
- Any Rhode Island exemption-law change or bill. None found.
- 2013 measles case (the 2025 release mentions it; no page for it was fetched).

South Carolina:

- Anything before 1990. No MMWR report naming South Carolina for these diseases appears in the 1982 to 1998 indexes. The August 4, 1939 Public Health Reports issue (said in a search snippet to report 99 polio cases in the state in four weeks) was downloaded, but the scan has no text layer and could not be read. "Poliomyelitis-Newberry County, South Carolina, 1961" (JAMA 1963) is not openly available.
- When the school requirement and the religious exemption were enacted. Only the statute's history note was available.
- November 2, 2018 update on added Spartanburg County measles cases. The archive capture timed out.
- February 2019 Aiken County hepatitis A outbreak declaration (mentioned inside the May 2019 release).
- "A Regional Measles Outbreak - South Carolina, 2025-2026" (NEJM, 2026). Not fetched; NEJM blocks scripted requests.

South Dakota:

- Final count for the 2014 to 2015 measles outbreak centered in Mitchell (13 cases per a search snippet). Only the December 31, 2014 count was on a fetched page.
- "Epidemiology of diphtheria in South Dakota" (S D J Med, 2000). PubMed title only.
- 2020 bill to end school vaccine requirements. Not located.
- "Pertussis Cases Rise In South Dakota" (November 16, 2018). The page fetched but shows only the title and date, no body text, so it was left out.

Tennessee:

- Current statute text (T.C.A. § 49-6-5001) and any recent exemption changes. Justia blocked; no state page located.
- "Indigenous measles eliminated in Tennessee" (1983), "The Memphis State University rubella outbreak" (JAMA 1974), and the 1995 Shelby County hepatitis A epidemic. PubMed titles only.
- 2025 measles cases. No state release located.

Utah:

- "Diphtheria epidemic in Utah in 1947" (Public Health Reports, April 1948). PubMed title only; the Stacks record was not located.
- 1975 one-dose and 1992 two-dose school measles requirements as their own items. They are mentioned inside the 1996 MMWR report only.
- Current statute text (Utah Code 53G-9-303) and the personal exemption's origin.
- Final count for the 2025 to 2026 measles outbreak. The state response page is live and changes.

## Fetched and verified but not used

- PA: "Measles Outbreak in a Boarding School --- Pennsylvania, 2003" (MMWR 2004-04-16); "Hospital-Associated Measles Outbreak — Pennsylvania, March–April 2009" (MMWR 2012-01-20); "Health Department Update on Measles Outbreak – January 5, 2024" and "Health department cautions Philadelphians about recent measles cases" (phila.gov); "School Immunization Requirements" (Pennsylvania Department of Education circular).
- RI: "Immunization and Communicable Disease Testing in Preschool, School, Colleges or Universities (216-RICR-30-05-3)" (Rhode Island Department of State; effective 01/04/2022, a refile with no changes); "Rhode Island Pertussis Surveillance Report", January to December 2005 (archived PDF).
- SC: "DPH Confirms Measles in Upstate Resident" (2024-09-19); "Use of Nowcasting to Estimate Real-Time Transmission Trends During a Measles Outbreak — South Carolina, October 2025–March 2026" (MMWR 2026-08-27).
- SD: "South Dakota Department of Health Launches Vaccination Clinics Following New Measles Cases" (2025-06-18); "Why South Dakota Didn’t Have a Measles Outbreak" (2025-08-07, a column by the health secretary).
- TN: "Measles Cases in Shelby County Now Being Investigated" (2016-04-22, archived); "TDH Urges Tennesseans at Risk for Hepatitis A to Get Vaccinated Now" (2018-07-19, archived); "Outbreaks of Respiratory Illness Mistakenly Attributed to Pertussis --- New Hampshire, Massachusetts, and Tennessee, 2004--2006" (MMWR 2007-08-24).
- UT: "Hepatitis A Virus Outbreaks Associated with Drug Use and Homelessness — California, Kentucky, Michigan, and Utah, 2017" (MMWR 2018-11-02); "Measles Hospitalizations in Utah, 2025–2026" (NEJM Evidence via PMC, 2026-07-14; says 602 cases were reported from June 20, 2025 to April 14, 2026).
