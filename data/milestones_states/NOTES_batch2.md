# State milestones, batch 2: research notes

States: Delaware (DE), District of Columbia (DC), Florida (FL), Georgia (GA), Hawaii (HI), Idaho (ID).
Files: `DE.json` (5 items), `DC.json` (6), `FL.json` (8), `GA.json` (7), `HI.json` (8), `ID.json` (8). 42 items in all.

Research ran on 2026-10-01. The final check script (keys, scope, allowed values, duplicates, and a fresh fetch of every URL to confirm the stored headline is in the page) ran on 2026-10-02 and found 0 problems. `checked` is "2026-10-01" in every item to match the format given for the project.

## How each item was verified

Every URL was fetched in this session with `curl` and the user agent "Mozilla/5.0 (D4TP research; eric@data4thepeople.com)". PDFs were downloaded and read with a text extractor (PyMuPDF). Each `headline` was copied from the page's own `<h1>`, `citation_title` tag or printed heading. No headline came from a search-result snippet.

Web search ran out of budget early in the session, and DuckDuckGo, Brave and Bing blocked scripted requests. Sources were then found through:

- the MMWR yearly index pages for 1982 to 2025 (all article titles downloaded and searched for the six state names);
- Europe PMC title searches (for PubMed Central records of Public Health Reports and MMWR);
- the Internet Archive's CDX index of each state health department's press release folder;
- state legislature and code sites, and the Caselaw Access Project (static.case.law) for court opinions. CourtListener's search API was used only to find case names; its opinion pages could not be fetched.

## Headline checks done by eye or by PDF text

- HI 1937, `AN UNUSUAL OUTBREAK OF MEASLES IN HAWAII, 1936-37`. The URL is the PDF of the whole Public Health Reports issue of December 17, 1937 on CDC Stacks. The article starts on the first page. The extracted text reads "1936-371" because a footnote mark "1" follows the title. Checked by reading the PDF text.
- HI 2018, `Hawai‘i Department of Health declares mumps outbreak over`. PDF news release. Matched in the PDF text.
- DC 1979, `Immunization of School Students Act of 1979`. PDF of D.C. Law 3-20. The first page prints `D. C. LAW 3-20` and then the act's name in quotation marks. The quotation marks were left off.
- FL 1957 and ID 1955. The PubMed Central pages show only the title and page scans. The first page of each scan was downloaded as an image and read by eye. The blurbs use only what that first page says.

## Internet Archive captures

- FL 2019-08-01, Florida Department of Health hepatitis A emergency release. The live `floridahealth.gov` newsroom address now returns 404.
- GA 2015-02-09 and GA 2019-11-18, Georgia Department of Public Health releases. The live `dph.georgia.gov` addresses return "Page not found".
- ID 2014-08-12, Idaho Department of Health and Welfare whooping cough release. The old newsroom address is gone from the live site.

## Headlines that are awkward as display headlines

- DE 1980: `AN ACT TO AMEND DELAWARE CODE, TITLE 14 BY PROVIDING FOR A DELAWARE PUBLIC SCHOOL ENROLLEES' IMMUNIZATION PROGRAM AND EXEMPTIONS.` All capitals, bare act title. The page's `<h1>` is only "Delaware General Assembly".
- DC 2021 and DC 2024: `D.C. Law 23-193. Minor Consent for Vaccinations Amendment Act of 2020.` and `D.C. Law 25-108. Immunization of School Students Amendment Act of 2023.` Bare law titles. The year in each act's name is one year before the year it took effect.
- FL 1998: `DEPARTMENT OF HEALTH, Appellant, v. Sara R. Johnson CURRY, and the Holmes County School Board, Appellees.` Case caption as printed. The short name is Department of Health v. Curry.
- GA 1951: `ANDERSON et al. v. THE STATE.` Case caption as printed. It does not say what the case is about.
- ID 1978: `39-4801. Immunization — exemptions.` Bare statute heading. The em dash is in the source. The page's `<title>` is "Section 39-4801 – Idaho State Legislature".
- ID 2025: `IDAHO MEDICAL FREEDOM ACT – Amends existing law to establish the Idaho Medical Freedom Act.` This is the bill's description line on the bill page. The page's `<title>` is "SENATE BILL 1210 – Idaho State Legislature".
- ID 1983: `Interstate Transmission of Measles in a Gypsy Population -- Washington, Idaho, Montana, California`. The 1983 title uses a word for Roma people that many readers now find offensive. The editor may want to drop this item or show it with care. The page does not say how many of the 44 cases were in Idaho.
- HI 2016: `Hepatitis A Outbreak 2016`. Generic page title.
- HI 2025: two headlines are in all capitals as printed, and one has an em dash that is in the source.
- GA 2025-01-28: the on-page `<h1>` is used. The page `<title>` and URL are cut short ("Metro Atlan").
- Old MMWR titles keep their double and triple hyphens as printed.
- FL 2019 names the state surgeon general in the headline. It is the release's own title.

## Dates and judgment calls (inferred, not printed in one place)

- DE 1980-07-11. The session law page prints "Approved July 11, 1990". That is a typing or scanning error on the page. The law is in the 130th General Assembly (volume 62, 1979 to 1980), and the next two chapters on the same site (405 and 406) both print "Approved July 11, 1980". The current code section also cites "62 Del. Laws, c. 404". The date 1980 is inferred from those.
- DC 2022-03-18. The WTOP story, published Monday, March 21, 2022, says the judge ruled "on Friday". March 18 is worked out from that. The court's own opinion was not fetched.
- DC 1979. The `diseases` tag is measles only, the one in-scope disease that the text extractor found in the scanned law. The law covers "preventable childhood diseases" in general.
- FL 1986-07-14. `date` is the first day of the period the report covers. The report was published February 6, 1987.
- FL 1997. `date` is the school year the seventh grade requirement began. Published September 4, 1998.
- FL 2013-09-12. `date` is the day the county health department declared a communicable disease emergency. Published August 1, 2014.
- GA 1996. `date` is the year of the outbreak. Published September 4, 1998.
- GA 1951. The court record lists "smallpox, diphtheria and typhoid at least" as the required shots. Only diphtheria is in scope.
- HI 1937-03. `date` is the peak month of the epidemic, which ran from November 1936 to September 1937. Published December 17, 1937.
- HI 2020. `date` is the year the new school requirements began ("beginning fall 2020"). The page was posted October 29, 2019.
- HI 2016-08-15. `date` is the day the health department named the likely source. `published` is null because the page has no single posting date. Its last update is January 11, 2017.
- HI 2018-10-16 is the date on the news release. A separate health department page says the outbreak was determined over on October 5, 2018.
- ID 1955-04. `date` is the month the vaccine was given. Published July 1958.
- ID 1978. `date` is the year in the statute's history line ("1978, ch. 240"). The page shows the current text, which was last amended in 2025. `published` is null.
- ID 2025-04-04. The blurb says only what the bill page shows: the bill's name, the signing date and the effective date. It does not describe what the act does to school vaccine rules, because the bill text and statement of purpose were not read in this session.
- ID 2014. The release says "nearly twice as many cases". The blurb says "a large increase" to avoid a multiplier, since the page gives no percentage.
- `published` uses "YYYY-MM" for four Public Health Reports items where the record gives only a month.
- `diseases` tags on law, court and coverage items are a best fit and are not always spelled out on the page.

## Wanted, not verified (left out)

Delaware:

- 1947 polio epidemic ("Poliomyelitis in Delaware, 1947", Delaware State Medical Journal, 1948). PubMed record only; not in PubMed Central.
- "The status of measles in the state of Delaware" (Delaware Medical Journal, 1968) and "Rubella control measures in Delaware" (1970). PubMed records only.
- 2018 mumps outbreak final count. A later release, "Four More Mumps Cases Identified, Bringing Total to 19" (April 24, 2018), was fetched and its headline checked. Left out to avoid two mumps items in one year. It can be added.
- 2019 hepatitis A exposures at food establishments. Releases found in the archive index; not read.
- Any measles case in a Delaware resident in 2025. Only an advice release (March 20, 2025) was found.
- Pre-1980 school vaccine rules. No source found.

District of Columbia:

- Any outbreak or report before 1979. Nothing found in the MMWR index or PubMed Central titles.
- The federal court opinion in the 2022 minor consent case (Booth v. Bowser; Mazer v. D.C. Department of Health). CourtListener pages could not be fetched. The WTOP story is used.
- A measles case in a District resident in 2025. Releases found were for 2011, 2015, 2017, 2024 and 2026.
- 2022 to 2023 enforcement of school immunization rules. A June 6, 2022 mayor's release was fetched but not used.

Florida:

- First enactment of the school immunization law. The current statute page (section 1003.22) was fetched, but its history line starts in 2002.
- "Measles--Florida" (MMWR, 1981, two reports). Before the online MMWR index begins.
- 1946 polio epidemic and 1976 Dade County diphtheria outbreak. PubMed records only.
- Flynn v. Estevez (Florida First District Court of Appeal, 2017), on a religious school and the religious exemption. Found on static.case.law but not read.
- February 2024 measles cases at a Broward County elementary school. No source fetched.
- Any rule or law change that followed the September 2025 announcement. Not fetched. The item covers the announcement only.

Georgia:

- First enactment of the school immunization statute (O.C.G.A. 20-2-771). Justia was blocked.
- 1961 oral polio vaccine campaign in Atlanta (JAMA, 1962) and "Summertime measles--Georgia" (1979). PubMed records only.
- Hepatitis A outbreak of 2018 and after. No state page found.
- Anything on Warm Springs and polio. The New Georgia Encyclopedia search returned nothing usable.

Hawaii:

- 2014 measles cases (15 confirmed). Mentioned only inside a February 2015 health department article, which was fetched but not used.
- 2023 measles case in a returning traveler (release of April 10, 2023). Fetched and verified; left out to keep the list at eight.
- The 1981 rubella outbreak paper and 1950s polio papers. PubMed records only.
- The text of the administrative rule (Hawaii Administrative Rules 11-157) for the 2020 change. The health department's announcement is used.

Idaho:

- 1978 session law itself. Only the current statute page with its history line was fetched.
- 2021 law requiring schools to describe exemptions (session law chapter 263) and the 2025 amendment of section 39-4801 (chapter 174). Seen only in the statute history lines; the bills were not identified.
- What Senate Bill 1210 does to school rules. Idaho Capital Sun returned 403 and the statement of purpose PDF did not download.
- 1999 New York Times story on Idaho's immunization registry. Blocked (403).
- "Detecting poliovirus in vaccine lots used in Idaho in 1955" (Public Health Reports, 1959). Fetched, title only; not used because the 1958 article covers the same event.
- September 2023 first measles case releases and the March 2024 whooping cough release. Fetched and verified; left out to keep the list at eight.

## Fetched and verified but not used

- "Measles Among Children of Migrant Workers -- Florida" (MMWR, 1983-09-16)
- "Measles -- Duval County, Florida, 1991-1992" (MMWR, 1993-02-05)
- "Measles Outbreak in an Unvaccinated Family and a Possibly Associated International Traveler — Orange County, Florida, December 2012–January 2013" (MMWR, 2014-09-12)
- "Florida plans to end vaccine mandates statewide, including for schoolchildren" (CNN, 2025-09-03)
- "Pertussis outbreak in an Amish Community: Kent County, Delaware, 2018" (Delaware Journal of Public Health, 2019)
- "§ 38–502. Certification of immunization required." and "§ 38–506. Exemption from immunization." (D.C. Law Library, current code text)
- "39-4802. Exemptions." (Idaho Statutes)
- "Pertussis (whooping cough) on the rise in southwest Idaho" (Idaho Department of Health and Welfare, 2024-03-08)
- "DOH CONFIRMS SECOND CASE OF MEASLES IN HAWAIʻI" (2025-04-17)
- "District of Columbia Confirms Case of Measles" (DC Health, 2015-05-20)
