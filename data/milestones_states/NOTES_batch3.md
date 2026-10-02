# State milestones, batch 3: research notes

Checked 2026-10-01. Files: `IL.json` (8 items), `IN.json` (7), `IA.json` (7), `KS.json` (7), `KY.json` (7), `LA.json` (7). 43 items in all.

## How each item was verified

Every URL was fetched in this session with `curl` and the user agent `Mozilla/5.0 (D4TP research; eric@data4thepeople.com)`. PDFs were downloaded and read with PyMuPDF. Each `headline` was copied from the page's own `<h1>`, `citation_title` tag, or printed heading. No headline came from a search snippet.

A script then loaded all six files and checked: all ten keys present and in order, `scope` matches the file name, disease keys are valid, dates are well formed and fall in 1929 to 2025, no duplicate (date, headline) within a state. It re-fetched every URL (all returned HTTP 200) and confirmed the stored headline appears in the page text after collapsing white space. Result: 39 headlines matched by script, 4 checked by eye (below), 0 problems.

### Headlines checked by eye (scanned PDFs with no text layer)

Four Louisiana Morbidity Report issues are scanned images. The first or second page was rendered to an image and read:

- `MEASLES TRAGEDY IN LOUISIANA - 1975` (January 1976 issue, page 1). The printed heading has a second line, `(The Good, The Bad, and The Ugly)`, which was left off.
- `STATEWIDE RUBELLA OUTBREAK` (April 1978 issue, page 1). Printed subheading: `Recommendations to Physicians`.
- `LOUISIANA MUMPS OUTBREAK` (March/April 1987 issue, page 2; the URL ends in `#page=2`).
- `Large Hepatitis A Outbreak in Monroe Area` (September-October 1992 issue, page 1).

The numbers in these four blurbs were also read from the page images, not from extracted text.

## Internet Archive captures

None. All 43 URLs are live pages. The Wayback Machine index was used only to find the folder layout of the Louisiana Morbidity Report archive on `ldh.la.gov`; the files themselves were fetched from the live state site.

## Sites that blocked or failed

- `ilga.gov`: old-style URLs (`/legislation/publicacts/fulltext.asp`, `BillStatus.asp`) return 404. The new path `/Legislation/PublicActs/View/099-0249` works.
- `iga.in.gov` (Indiana Code): a JavaScript app; scripted requests get an empty shell.
- `law.justia.com`, `jamanetwork.com`, `academic.oup.com`: 403 browser check.
- `chicago.gov` PDF: 403.
- `pubmed.ncbi.nlm.nih.gov`: "cookies must be enabled". PubMed Central worked, but returned a reCAPTCHA page after several quick requests.
- `ldh.la.gov/news` search results load by JavaScript and could not be listed.
- `chfs.ky.gov`: some older page paths are 404; the measles page returned 504 once and then loaded.
- The session's web search budget ran out partway through. After that, candidates were found only by browsing primary sites: the MMWR yearly index pages (1982 to 2026, scanned for the six state names plus the disease names), NCBI E-utilities title searches of PubMed Central, the Louisiana Morbidity Report index, and state agency pages. Some events that a web search would have found are listed below as not verified.

## Thin sources (title-only pages)

Three items point to PubMed Central records of scanned journal articles. The record page shows only the title, authors, journal, date and a "read before" footnote. The blurbs say only what the record shows and do not describe findings.

- IL 1934, `Diphtheria Prevention in Chicago: The Health Officer's Problem`
- IN 1960, `A noncompulsory immunization law for Indiana school children`
- KY 1935, `Anterior Poliomyelitis in Kentucky During 1935`

The Kentucky 1982 Meade County hepatitis A record does show an abstract, and the blurb uses it.

## Headlines that are awkward as display headlines

- `Public Act 099-0249` (IL 2015). Bare act number. This is Senate Bill 1410, the Certificate of Religious Exemption law. The page's printed description is only `AN ACT concerning education.`
- `72-6262. Same; certification of completion required, alternatives; duties of school boards.` (KS 1961). Bare statute caption; "Same" refers back to the section before it.
- `214.036 Exceptions to testing or immunization requirement.` (KY 1962). Bare statute caption.
- `902 KAR 2:060. Immunization schedules for attending child day care centers, certified family child care homes, other licensed facilities which care for children, preschool programs, and public and private primary and secondary schools.` (KY 2018). Very long regulation title. It does not say this is the hepatitis A change.
- `PROVISION OF INFORMATION RELATING TO IMMUNIZATION EXEMPTIONS BY SCHOOLS AND CHILD CARE CENTERS` (IA 2025). All capitals as printed in the Iowa Acts chapter heading (Chapter 106, House File 299).
- `VACCINES/VACCINATION: Requires that communication issued about immunization requirements include exemption information and applies exemptions not only to students seeking to enter school but also to students attending school` (LA 2024). This is the bill page's printed short title for House Bill 47 (Act 675). The page `<title>` is only `HB47`. The page prints two non-breaking spaces after the colon; one space is stored.
- `NOTICE: Legislative Changes in Immunization Laws for School-Aged Children` (LA 2008). A notice inside a newsletter issue; the heading wraps over three lines in the PDF.
- `Hepatitis A Outbreak` (IN 2017) and `Polio in Iowa` (IA 1952). Generic page titles.
- `Current Trends Pertussis Surveillance -- United States, 1986-1988` (KS 1986). A national report; Kansas is not in the title. The Kansas outbreak is described in the editorial note.
- `Epidemiologic Notes and Reports Follow-Up on Poliomyelitis -- United States, Canada, Netherlands` (IA 1979). Iowa is not in the title.
- `Epidemiologic Notes and Reports Multiple Measles Outbreaks on College Campuses -- Ohio, Massachusetts, Illinois` (IL 1985). The same page is listed in the pilot notes as fetched but unused for Ohio; here it is used for the Principia College outbreak.
- `Mumps Outbreaks on University Campuses -- Illinois, Wisconsin, South Dakota`, `Measles among Members of a Drum and Bugle Corps -- Arkansas, California, Kansas`, `Rubella Among Hispanic Adults --- Kansas, 1998, and Nebraska, 1999`, `Outbreaks of Pertussis Associated with Hospitals --- Kentucky, Pennsylvania, and Oregon, 2003`. Multi-state titles; each blurb covers only the state's part.
- `Measles Outbreak Associated with a Migrant Shelter — Chicago, Illinois, February–May 2024`. CDC's own title; it has an em dash and an en dash that are in the source. The editor may want to look at this one given the topic. The blurb states only counts and dates.
- Old MMWR titles carry section prefixes and double or triple hyphens exactly as printed.
- Louisiana 1975, 1978 and 1987 headlines are in capitals as printed.

## Dates and other judgment calls

- Rule used for outbreak reports: when the report came out in the same year as the event, `date` is the publication date. When it came out in a later year, `date` is the event date the page states and `published` holds the report date. Affected items: IL 2006-09-06 (published 2008-07-25), IN 2016-02 (2018-07-27), IA 2015-07 (2017-04-14), IA 1979-07-27 (1997-12-19), KS 1986 (1990-02-02), KS 1993-04-24 (1994-08-12), KS 1998-04-22 (2000-03-24), KY 2003-08 (2005-01-28). This differs a little from the pilot, where a 1988 Los Angeles outbreak is dated by its 1989 report.
- Iowa 1979 polio: the page is CDC's December 19, 1997 reprint of the July 27, 1979 MMWR article, with a 1997 editorial note. The "last polio outbreak in the United States" wording comes from that 1997 note.
- Old MMWR pages (before about 2015) do not print a date in the body. The date was read from the `reportDate` variable in the page source, for example `June 22, 1984 / 33(24);349-51`.
- Kansas statute: `date` is 1961, the first entry in the section's history line (`L. 1961, ch. 354, § 2`). The page shows the current text, last amended in 1994. The page does not say what the 1961 version required, and the blurb does not claim to.
- Kentucky statute: `date` is 1962 (`Created 1962 Ky. Acts ch. 95, sec. 4`). The text shown is the current version, effective September 9, 2021. The blurb says so.
- Kentucky regulation: `date` is 2018-07-01, from Section 7 ("Section 2 ... shall become effective for the school year beginning on or after July 1, 2018"). Section 2 lists two doses of hepatitis A vaccine for the age 5 to 6 group and others. The page does not say in plain words that hepatitis A was new that year; that came from a search summary and is not in the blurb.
- Louisiana 2008 notice: `date` is 2008-07-01, the effective date the notice gives for Acts 152 and 342. The newsletter issue is July-August 2008.
- Louisiana 2024: `date` is 2024-06-19, the day the bill page shows it was signed (effective August 1, 2024). The enrolled act PDF was also read.
- Louisiana 1975: `date` is 1975-11 (cases "appeared in late November, 1975"); the issue is January 1976. The count of 35 is 30 recovered plus 5 active cases identified by health workers as of January 7, 1976. The article also mentions 20 more recovered cases reported by residents but not investigated.
- Louisiana 1992: `date` is 1992-06-15, the day the state was notified; the issue is September-October 1992.
- Indiana hepatitis A page: `date` is 2017-12-01, the outbreak start the page gives. The page says it was last updated February 2026; `published` is null because no full date is given. A 2018 news story gives November 2017 as the start.
- Illinois 1989: the first Chicago report (September 1, 1989) is used so the item falls in the outbreak year. The May 18, 1990 update, with the full-year count of 2,232 cases and eight deaths, was also verified and can replace it.
- `published` is null wherever the page gives only a month or year (journal articles, newsletter issues, statutes).
- `diseases` tags on law items are a best fit. Iowa's tags follow the list in Iowa Code 139A.8 (no mumps). Kansas, Kentucky statute, Illinois and Louisiana 2024 use the six-disease school set.

## Inferred, not stated on the page

- IN 1960: the disease tags (diphtheria, pertussis, polio) are a guess. The record page does not say which diseases the law covered.
- KS 1961, KY 1962, IL 2015, LA 2024: disease tags, as above.
- KS 2019: the story says the rules "will go into effect on August 2"; the year 2019 comes from the story's date.
- LA 2024: the year comes from the page's "2024 Regular Session" label; the history lines print only month and day.

## Wanted, not verified (left out)

Illinois:

- 1956 Chicago polio outbreak (1,111 cases). JAMA and American Journal of Epidemiology pages returned 403; the Chicago health department history PDF returned 403.
- When Illinois first required vaccination for school entry. No source fetched. The current School Code section (105 ILCS 5/27-8.1) URL was not found on the new ilga.gov site.
- 2015 measles cluster at a Palatine day care, and any 2025 state press release. Not searched (search budget).
- Illinois court rulings on school vaccination. Not searched.

Indiana:

- Indiana Code 20-34-4-2 (required immunizations) and 20-34-3-2 (religious objection). iga.in.gov could not be read by script; Justia returned 403.
- 2012 measles cases around the Super Bowl in Indianapolis. No source fetched.
- 2025 measles cases in Indiana. No state release fetched.
- A hepatitis A outbreak in a religious community (Epidemiology and Infection, 2000). PubMed Central returned a reCAPTCHA page.
- What the 1960 "noncompulsory" law said. Only the article's title page was reachable.

Iowa:

- 1977 law requiring vaccination for school entry and the 1991 move to two doses. The 2006 MMWR mumps report states both in one sentence, but no statute or session law page was fetched, so there is no separate item.
- 1952 gamma globulin field trial in Sioux City as its own item with a primary source. Only the Iowa PBS history page is used.
- Final count for the 2006 mumps epidemic. The item uses the count as of March 28, 2006.

Kansas:

- 1988 to 1989 mumps outbreak in Douglas County (269 cases). PubMed blocked; no MMWR page names it.
- A report on the 1986 pertussis outbreak itself. Only the national surveillance report that describes it was found.
- March 2025 release on the first case of the southwest Kansas measles outbreak. Not fetched; the end-of-outbreak release is used.
- 2018 measles cases in Johnson County. No source fetched.

Kentucky:

- End of the hepatitis A outbreak (declared over as of December 31, 2021, with 5,094 cases). This is stated on the state's Hepatitis A Virus page, which was fetched; left out because the page title is generic and the list already has two hepatitis A items. It can be added.
- February 2023 measles case tied to a large gathering at Asbury University. No release or CDC alert fetched.
- 2024 to 2025 whooping cough rise and infant deaths. No release fetched.
- The 2026 measles outbreak (an August 18, 2026 release title on the state news page says it was the highest number of cases in 35 years). Outside the 1929 to 2025 range.
- KRS 214.034 (the requirement itself). Fetched; its history line was not read in full, so it is not used.
- Court rulings on school vaccination in Kentucky. Not searched.

Louisiana:

- When Louisiana first required vaccination for school entry. The 1976 morbidity report mentions "a state law requiring school children" to be immunized but gives no date. The current statute's history starts with Acts 1990, No. 1047.
- February 2025 state health department memo on vaccine promotion. Not fetched, and it is not tied to one disease.
- 2017 mumps cases at Louisiana State University. No release fetched.
- 2018 onward hepatitis A outbreak. No state page fetched.
- Polio in Louisiana in the 1950s. Only a 1956 household immunity study title was found.

## Fetched and verified but not used (available if the editor wants more)

Illinois:

- "Outbreak of Measles Among Christian Science Students -- Missouri and Illinois, 1994" (MMWR, 1994-07-01). 49 cases reported to the Jersey County Health Department.
- "Epidemiologic Notes and Reports Update: Measles Outbreak -- Chicago, 1989" (MMWR, 1990-05-18). 2,232 cases and eight deaths in 1989.
- "Mumps Outbreak at a University and Recommendation for a Third Dose of Measles-Mumps-Rubella Vaccine — Illinois, 2015–2016" (MMWR, 2016-07-29).
- "Pertussis Outbreak Among Adults at an Oil Refinery --- Illinois, August--October 2002" (MMWR, 2003-01-10).
- "Notes from the Field: Measles Outbreak — Cook County, Illinois, October–November 2023" (MMWR, 2024-03-14).

Indiana:

- "Measles Outbreaks on University Campuses--Indiana, Ohio, Texas" (MMWR, 1983-04-22). 174 cases at Indiana University.
- "Measles at an International Gymnastics Competition -- Indiana, 1991" (MMWR, 1992-02-21).
- "Respiratory Diphtheria Caused by Corynebacterium ulcerans -- Terre Haute, Indiana, 1996" (MMWR, 1997). Title seen in the MMWR index; page not read.

Iowa:

- "Postexposure Prophylaxis, Isolation, and Quarantine To Control an Import-Associated Measles Outbreak --- Iowa, 2004" (MMWR, 2004-10-22).
- "Epidemiologic Notes and Reports Poliomyelitis -- United States, Canada" (MMWR reprint, 1997-12-19; original 1979).
- Iowa Code 139A.8, "Immunization of children" (current text, PDF).

Kansas:

- "Notes from the Field: Rubella Infection in an Unvaccinated Pregnant Woman — Johnson County, Kansas, December 2017" (MMWR, October 2018).
- "Ascertainment of Secondary Cases of Hepatitis A -- Kansas, 1996-1997" (MMWR, 1999-07-23).
- "Measles Update and Frequently Asked Questions" (Kansas Department of Health and Environment, 2025-05-12). 51 cases as of May 7, 2025.
- "KDHE now requires meningitis, hepatitis A vaccines for school-age children" (KSHB, 2019-07-18).

Kentucky:

- "Epidemiologic Notes and Reports Transmission of Measles Across State Lines -- Kentucky, New Hampshire, Tennessee, Virginia" (MMWR, 1982-03-19). One Kentucky case.
- "Hepatitis A Virus Outbreaks Associated with Drug Use and Homelessness — California, Kentucky, Michigan, and Utah, 2017" (MMWR, 2018-11-02).
- "Health Officials Announce Measles Case in Kentucky" (state release, 2025-02-26).

Louisiana:

- Louisiana Revised Statutes 17:170 (current text on legis.la.gov).
- Act 675 of 2024, enrolled text (PDF).
- The Louisiana Morbidity Report index for 1967 to 2018 lists many more titles that were not opened, among them "K.O. Measles Campaign In Orleans And St. Bernard Parishes" (8/1967), "State Health Department Launches Rubella Control Program" (9/1969), "Measles Outbreak Washington - St.Tammany (41 Cases)" (7/1985), "Measles Outbreak-(Shreveport)" (3-4/1990) and "Measles Outbreak In Jefferson Parish" (5-6/1995). Issue files follow the pattern `.../LMR/60s70s80s90s/<decade>/<year>/<month><yy>.pdf`.
