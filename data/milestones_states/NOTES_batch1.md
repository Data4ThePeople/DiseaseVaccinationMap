# State milestones, batch 1: research notes

Checked 2026-10-01 (final re-fetch finished 2026-10-02). States: Alabama, Alaska, Arizona, Arkansas, Colorado, Connecticut.

| State | File | Items | Earliest | Latest |
|---|---|---|---|---|
| Alabama | `AL.json` | 8 | 1936 | 2025-08-25 |
| Alaska | `AK.json` | 7 | 1977-03-18 | 2025-01-16 |
| Arizona | `AZ.json` | 8 | 1985-03-14 | 2019-05-28 |
| Arkansas | `AR.json` | 8 | 1937 | 2025-12-30 |
| Colorado | `CO.json` | 8 | 1950 | 2025-05-25 |
| Connecticut | `CT.json` | 6 | 1931 | 2025-12-11 |

## How each item was verified

Every URL was fetched in this session with `curl` and the User-Agent `Mozilla/5.0 (D4TP research; eric@data4thepeople.com)`. PDFs were downloaded and read with PyMuPDF. Each headline was copied from the page's own `<h1>`, `<title>` or `citation_title`, or from the printed heading of the PDF.

A final script loaded all six files and checked: all ten keys present and in order, `scope` matches the file name, `diseases` and `kind` use allowed values, dates are well formed and fall in 1929 to 2025, no duplicate (date, headline) within a state, no en or em dashes in any blurb. It then fetched every URL again and looked for the stored headline in the page text. Result: 45 of 45 URLs returned HTTP 200 and 41 headlines matched the page text exactly. The other four are listed in the next section.

Web search was not available for most of this work (the session's search budget ran out early). Sources were found by reading the MMWR yearly index pages (1982 to 1998, 2007 to 2026), PubMed and PMC title searches through the NCBI E-utilities API, and the news archives of each state health department. The MMWR index pages for 1999 to 2006 return 404, so MMWR reports from those years were found only through PubMed titles.

## Headlines that did not match the page text by script

Two PDF headings checked by eye:

- CT 1972, `Poliomyelitis — Connecticut`. The scan's text layer reads `POLIOM YELITIS — C onnecticut` in the heading and `Poliomyelitis —  C onn ecticut` in the contents box. The stored headline is the contents-box form with the stray spaces removed.
- AR 2003, `AN ACT TO REVISE THE RELIGIOUS EXEMPTION TO THE SCHOOL IMMUNIZATION REQUIREMENTS.` This is the printed "Subtitle" on page 1 of Act 999. The PDF text has line numbers between the two lines of the subtitle.

Two court headlines that come from the archive's metadata record, not the opinion page itself. This departs from the "page's own heading" rule and the editor should decide whether to keep them:

- AZ 1987, `Maricopa County Health Department v. Harmon`
- AR 2002, `McCarthy v. Boozman`

Both opinions are hosted by the Harvard Law School Caselaw Access Project (`static.case.law`). The printed heading on each opinion page is the full list of parties (for the Arizona case it runs about 900 characters). The short case name is the `name_abbreviation` field in the archive's own JSON record for the same case (`.../cases/0161-01.json` and `.../cases/0945-01.json`), which was fetched and checked. The `url` in the data file points to the readable HTML opinion.

## Headlines that are awkward as display headlines

- AR: `Polio` (1937), `Vaccination` (1967) and `Pertussis` (2001). Bare entry titles from the Encyclopedia of Arkansas. They do not name the event.
- AL: `IMMUNIZATION OF CHILDREN IN SCHOOLS AND CONGREGATED CARE SETTINGS` (2009). All-caps chapter title of the State Board of Health rule. The line above it in the PDF reads `CHAPTER 420-6-1`.
- AR: `AN ACT TO REVISE THE RELIGIOUS EXEMPTION TO THE SCHOOL IMMUNIZATION REQUIREMENTS.` (2003). All caps. The act in fact adds a philosophical exemption, which the title does not say.
- CT: `AN ACT CONCERNING IMMUNIZATIONS.` (2021). All caps and generic. This is Public Act 21-6.
- CO: `House Bill 14-1288` (2014) and `Senate Bill 20-163, School Entry Immunization` (2020). Bare bill names from the state health department's pages.
- AZ: `Measles -- Arizona` (1985). Bare MMWR title.
- AZ: `Epidemiologic Notes and Reports Erythromycin-Resistant Bordetella pertussis -- Yuma County, Arizona, May-October 1994`. Section prefix and a Latin name.
- AZ: `New Vaccine Exemption Form Being Used this Year` (2013). "This year" has no year in it.
- AR: `Arkansas Reports Highest Number of Whooping Cough Cases In FifteenYear Collection History` (2025). "FifteenYear" is run together on the source page.
- AL 1936, CO 1950, CT 1931, AL 1953: long journal article titles.
- AK 2014: `Pertussis Outbreak in the Interior Region ― Alaska, Fall 2014`. The dash is a horizontal bar character (U+2015), as in the PDF. The AZ 2016 MMWR title uses the same character.
- Old MMWR titles keep double and triple hyphens as printed.

## Thin sources (title-only pages)

Four items point to PubMed Central records of scanned articles. The record page shows the title, authors, journal and date only. The blurbs say what the article is about and nothing about its findings.

- AL 1936, American Journal of Public Health, February 1937
- AL 1953, Public Health Reports, November 1953
- CO 1950, American Journal of Public Health, October 1952
- CT 1931, Yale Journal of Biology and Medicine, May 1943

## Internet Archive captures

None. All 45 URLs are live pages.

## Dates and other judgment calls

- `published` is null where the source gives only a month and year (the four PMC items above, AL 1967) or no date at all (AL 2009 rule, CO 2014 page).
- AK 1977: the PDF is printed "March 18, 1977 / Vol. 26 / No. 11". The CDC Stacks record for the same file says March 11, 1977. The JSON uses March 18.
- AK 2001: the source is a 2017 state bulletin that says hepatitis A vaccination became a school and daycare requirement in 2001. `kind` is "history page".
- AK 2014 and 2017, AR 2016, CO 2017 and 2025, AZ 1985, 1994, 2002 and 2016, AL 2002: `date` is the first event date the report states (first report, first case or start of the outbreak period). `published` is the report's own date.
- AL 1967: `date` is 1967-08. The paper covers cases reported from August 2 through November 20, 1967, and was published in December 1971.
- AL 2009: `date` is the effective date of the current version of the rule (October 23, 2009). The rule's own history line says it dates from October 1, 1982. The underlying statute (Code of Alabama 16-30-1 to 16-30-5) was not fetched.
- AZ 1987: the ruling is dated October 8, 1987. The school exclusion it concerns ran to March 18, 1986.
- AZ 2013 (two items) and AZ 2019 are posts on the Arizona Department of Health Services director's blog. Two are tagged "press release" and the exemption form post is tagged "policy". None is a formal press release.
- AR 1937, 1967, 2001: Encyclopedia of Arkansas entries (Central Arkansas Library System), tagged "history page". `published` is each entry's "Last updated" date. These are a secondary reference, not primary sources.
- AR 1967: the entry says rubella was added after 1973. The `diseases` list includes rubella.
- AR 2002: `diseases` is a best fit. The opinion refers to the immunization statute without listing every disease in the passage read.
- CO 1978: the source is a 2019 Colorado Public Radio story, tagged "history page". The 1978 act itself was not fetched.
- CO 2014 and 2020: the sources are the state health department's pages about each bill. They give the month only. The signed act for SB 20-163 was fetched from `leg.colorado.gov`, but its approval date is handwritten and did not come through the text layer. The bill pages on `leg.colorado.gov` return HTTP 406 to scripted requests.
- CO 2025: the blurb count is nine secondary cases plus one tertiary case, as in the report's summary box.
- CT 1931: `date` is the first year of the study period. The article was published in May 1943.
- CT 1972: `date` is October 25, 1972, the day the report says the cases were reported. `published` is the issue's release date, October 27, 1972.
- CT 2021: the act's text strikes the religious exemption clause. The plain statement that the act "eliminated the religious exemption" comes from the Attorney General's 2024 release and the Office of Legislative Research report 2021-R-0134, both fetched.
- CT 2024: the source is the Attorney General's statement, tagged "press release". The Supreme Court's order was not fetched.
- AR 2025-12-30 is the last item in range. The release covers the full 2025 count.
- `diseases` on law, rule and court items is a best fit and is not always spelled out on the page.

## Wanted, not verified (left out)

Alabama:

- When the school vaccination law (Code of Alabama 16-30-1 to 16-30-5) was first enacted. The legislature's code site is a JavaScript app and returned no text.
- 1946 polio epidemic. Only title-level records were found ("Poliomyelitis in Alabama: Epidemiological Considerations", Yale J Biol Med, 1946).
- "The status of measles eradication in Alabama" (1968) and a 1969 county rubella campaign. PubMed titles only; not in PMC.

Alaska:

- March 1, 1977 statewide school exclusion (7,418 students), from "Enforcement of school immunization law in Alaska", JAMA 1978. PubMed blocks scripted requests. The 1977 MMWR report used here gives the deadline but not the count.
- June 1976 measles outbreak in Shungnak (MMWR vol. 25, no. 35). Not fetched.
- 1950s polio in Alaska and the 1964 to 1966 measles vaccine field trials. PubMed titles only.
- Alaska Epidemiology Bulletins before 2015. The URL pattern that works for recent bulletins returned nothing for 1976, 1977, 1985, 2000 and 2001.

Arizona:

- The 2025 measles outbreak. No Arizona Department of Health Services page with a 2025 date and case count could be fetched. The department's measles page loads its numbers with JavaScript and the press release archive came back empty. A January 8, 2026 blog post says the state was "managing the largest measles outbreak in this state since the early 1990s", but it falls outside the date range and gives no start date or count. This is the main gap in the batch.
- When the school vaccination requirement and the personal belief exemption were enacted. The statute text (A.R.S. 15-872 and 15-873) was fetched, but the page has no dates.
- 2008 Tucson measles outbreak linked to hospitals. No source page found.
- "The effect of policy changes on hepatitis A vaccine uptake in Arizona children, 1995-2008" (Public Health Reports, 2011) and the 2017 Maricopa County hepatitis A outbreak abstract. PMC returned a browser check for both.

Arkansas:

- Act 244 of 1967 itself. Only the encyclopedia entry is used.
- 1973 "Every Child by '74" vaccination campaign. Mentioned in three encyclopedia entries; no page of its own was fetched.
- 1981 measles outbreak at Harding College. Mentioned in the encyclopedia's Measles entry, with no case count.
- 2001 to 2002 pertussis outbreak primary source (Archives of Pediatrics and Adolescent Medicine, 2004). Not in PMC.
- April 2025 first measles case release. The guessed URL returned 404. The second-case release is used.
- 2018 to 2019 hepatitis A outbreak. Not searched for.

Colorado:

- HB 78-1089 (the 1978 act) and the HB 14-1288 bill page. Legislature site returned 406 and 403.
- Exact signing date of SB 20-163 (see above).
- 2012 pertussis epidemic and the 2018 to 2019 hepatitis A outbreak. No state page found.
- "An outbreak of pertussis-like syndrome in Boulder County, Colorado" (1990) and "Routine immunization of Colorado's children" (1955). PubMed titles only.

Connecticut:

- When the school vaccination requirement and the religious exemption were first enacted. No source fetched.
- 2023 Second Circuit ruling and 2024 Connecticut Supreme Court ruling (Spillane v. Lamont) on Public Act 21-6. Opinions not fetched. The Attorney General's 2024 release mentions the lower court rulings.
- 2021 Fairfield County measles cases. The 2021 press release index showed no measles item in its static HTML.
- "Measles outbreak in Northeastern Connecticut" (Connecticut Medicine, 1974). PubMed title only.

## Fetched and verified but not used (available if the editor wants more)

- AL: "Alabama Department of Public Health investigates mumps at the University of Alabama" (2017-02-23); "Hepatitis A outbreak under investigation in North Alabama" (2018-12-26); "ADPH investigates pertussis outbreak in East Alabama" (2017-05-04, title seen in index only); "Three Cases of Congenital Rubella Syndrome in the Postelimination Era — Maryland, Alabama, and Illinois, 2012" (MMWR, title seen in index only).
- AK: "Measles Confirmed in the Municipality of Anchorage — What Alaska Clinicians Should Know" (Alaska Public Health Alert, 2025-05-22).
- AZ: "Five AZ Measles Cases from a Disneyland Exposure" (director's blog, 2015-01-23); "AZ Measles Outbreak Winds Down" (2015-02-13); "Largest Measles Outbreak of the Year Just got Bigger (but don’t worry!)" (2016-10-28); "Confirmed Measles Cases in Arizona" (2016-05-27); "Travel Smart, Stay Protected: What You Need to Know About Measles and Travel" (2025-08-14, says Arizona had 5 reported cases).
- AR: "Cude v. State." (Arkansas Supreme Court, 1964-04-06) and "Wright v. DeWitt School District." (1965-01-11), both from `static.case.law`. Left out because both concern smallpox vaccination, which is outside the disease list. "Measles among Members of a Drum and Bugle Corps -- Arkansas, California, Kansas" (MMWR, 1983-11-04). "Texarkana — Epidemic Measles in a Divided City" (already used for Texas in the pilot; not re-fetched here).
- CO: "Public Health Economic Burden Associated with Two Single Measles Case Investigations — Colorado, 2016–2017" and "Notes from the Field: Wastewater Surveillance for Measles Virus During a Measles Outbreak — Colorado, August 2025" (MMWR, titles seen in index only).
- CT: "Follow-Up on Poliomyelitis — Connecticut, New York, Massachusetts, New Hampshire" (MMWR, week ending 1972-10-28; says nine of 11 suspect cases were confirmed as type 1 polio, all in unvaccinated children at a school in Greenwich); "Connecticut School Immunization Requirements" (Office of Legislative Research, 2021-07-30).

## Sites that blocked or failed scripted requests

`pubmed.ncbi.nlm.nih.gov` (cookie wall), `law.justia.com` (403), `www.courtlistener.com` opinion pages (202 challenge; the search API works), `leg.colorado.gov/bills/...` (406), `www.leg.state.co.us` (403), `azmirror.com` (403), `stacks.cdc.gov/gsearch` (Access Denied; item pages and PDFs work), `alison.legislature.state.al.us` and `admincode.legislature.state.al.us` (JavaScript apps), `pmc.ncbi.nlm.nih.gov` (occasional reCAPTCHA page after many requests in a row).
