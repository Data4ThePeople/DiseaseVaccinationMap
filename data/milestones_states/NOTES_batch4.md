# Milestones batch 4: research notes

States: Maine, Maryland, Massachusetts, Michigan, Minnesota, Mississippi.

Files: `ME.json` (6 items), `MD.json` (7), `MA.json` (7), `MI.json` (8), `MN.json` (7), `MS.json` (7). 42 items in all.

Research fetches were done on 2026-10-01. The final re-fetch check ran on 2026-10-02 after the first run was cut by a network error. The `checked` field is `2026-10-01` in every item, to match the other batches.

## How each item was verified

Every URL was fetched in this session with `curl` and the User-Agent `Mozilla/5.0 (D4TP research; eric@data4thepeople.com)`. PDFs were downloaded and read with a text extractor (PyMuPDF). The headline was copied from the page's own `<h1>`, `<title>` tag, `citation_title` tag or printed heading.

A build script holds, for each item, a short list of phrases from the source that support the date and the blurb. On the final run the script re-fetched all 42 URLs and checked: all keys present, `scope` matches the file name, disease keys and `kind` values are valid, date formats are valid, no duplicate (date, headline) in a state, the stored headline appears in the fetched page, and every supporting phrase appears in the fetched page. Result: 42 of 42 passed, every URL returned HTTP 200.

PDF headings were checked by the same script against the extracted text, with line breaks collapsed to spaces. Three items are PDFs: ME 1984 (session law), ME 2012 (pertussis report), MN 1967 (session law).

The web search tool ran out of its session budget after the first round of searches. Brave, Bing and DuckDuckGo returned captcha pages or unrelated results to scripted requests. Leads after that came from the MMWR yearly index pages (1982 to 2025), PubMed title searches through the NCBI E-utilities API, the Internet Archive index (CDX) of each health department's news folder, and state legislature sites. CDC Stacks search returned 403, so pre-1982 MMWR issues could not be located.

`published` for old MMWR pages (1983 to 2011) is the issue date, confirmed in each page's `Date` meta tag and `reportDate` variable.

## Internet Archive captures (15 items)

- ME 2012. Maine CDC pertussis report PDF. The live `maine.gov` URL returns 404 after a site rebuild.
- ME 2017-06-27. Old Maine CDC press release page (`press-release.shtml?id=758686`), no longer on the live site.
- MD 2019-04-19. The live `health.maryland.gov` URL returns 404.
- MA 2017-06-05, MA 2018-09-24, MA 2024-07-18. The live `mass.gov` site returns 403 to scripted requests.
- MI 2015-01, MI 2017-10-31, MI 2019-04-02. The live `michigan.gov` site returns 403 "Access Denied" to scripted requests.
- MN 2019-08-08. The live `health.state.mn.us` URL returned 403. Older Minnesota releases return 404. The 2024 release is live.
- MS 2012-04-09, MS 2015-01-12, MS 2019-07-31, MS 2023-07-17. The live `msdh.ms.gov` URLs return 404. Only 2025 and later releases are on the live site.

The three court opinions (MD 1982, MA 1971, MS 1979) use `static.case.law`, the Harvard Law School Caselaw Access Project file server. These are live pages, not archive captures. They are plain pages with the opinion text and no site navigation. CourtListener returned 202 (browser check) and Justia returned 403.

## Headlines that are awkward as display headlines

- ME 1984: `AN ACT to Correct Errors and Inconsistencies in the School Immunization Law and other Related Laws.` Bare act title. The title undersells the act, which replaced the school immunization section with new sections 6352 to 6358. In the PDF the title is printed over three lines.
- ME 2012: `Infectious Disease Epidemiology Report Pertussis, 2012`. Two printed lines of the report's heading ("Infectious Disease Epidemiology Report" and "Pertussis, 2012") joined with a space. The PDF's embedded title is "Background", which is wrong.
- ME 2019: the act's long title, as printed on the chaptered law page. The page `<title>` adds the prefix `PUBLIC Law, Chapter 154,`.
- ME 2020: `‘No’ vote – to keep state’s new vaccine law – wins by overwhelming margin`. From the page `<title>`. It has curly quotes and spaced en dashes, as in the source. The page's `<h1>` tags hold only the newspaper name.
- ME 2021: `Maine Vaccine Laws`. Generic page title.
- MD 1982 court: `IRVING DAVIS, SR. v. STATE OF MARYLAND`. Case caption in capitals. An Education Week story on the same ruling was fetched and has a plainer headline: `Md. High Court Invalidates Exemptions From Immunization` (https://www.edweek.org/education/md-high-court-invalidates-exemptions-from-immunization/1982/10, published 1982-10-20). The editor can swap it in.
- MA 1971: `Beulah G. Dalli & another vs. Board of Education & others.` Case caption.
- MS 1979: `Charles H. BROWN et al. v. Joe A. STONE, Houston Municipal Separate School District, et al.` Case caption with mixed capitals as in the source.
- MD 1975: `Control of a measles outbreak in an elementary school. Baltimore County, Md. 1975.` Printed with the periods, as in the page `<h1>`.
- MD 1982 and MD/MA 1992: `Pertussis -- Maryland, 1982` and `Pertussis Outbreaks -- Massachusetts and Maryland, 1992`. Old MMWR titles with double hyphens. The 1992 report is used in both the Maryland and Massachusetts files, with a different blurb in each.
- MA 1985: `Epidemiologic Notes and Reports Multiple Measles Outbreaks on College Campuses -- Ohio, Massachusetts, Illinois`. Section prefix as printed. It names three states. The pilot notes list this page as fetched and not used for Ohio.
- MA 2017, MA 2018 and MA 2024: on the page the `<h1>` starts with the label `Press Release`. The label was left off. The `<title>` tag has the headline without it.
- MI 2019: `Measles cases reach 34 in Michigan, highest number since 1991 Four additional cases confirmed in Oakland County`. The page's `<h1>` runs the headline and the subhead together with no punctuation.
- MI 2015: `Preliminary data shows a statewide decrease in school-age vaccine waiver rates`. A January 2016 release used as the source for the January 2015 rule. It does not name the rule.
- MI 1932: `Pearl Kendrick, Grace Eldering, and the Pertussis Vaccine`. The page's `citation_title` tag adds ` - Volume 16, Number 8—August 2010 - Emerging Infectious Diseases journal - CDC`. The on-page heading without that suffix is used.
- MN 1967: `CHAPTER 858—H. F. No. 1191`. Bare session law heading. The em dash is in the source.
- MN 1942: `Sister Kenny Institute`. Does not name the event.
- MN 2005, MN 2011: old MMWR titles with triple and double hyphens as printed.

## Thin sources (title-only pages)

- MD 1960, MI 1939 and MI 1956 point to PubMed Central records of scanned journal articles. The record shows only the title, authors, journal and date. The PDFs sit behind a browser check. The blurbs say only what the record shows and do not describe findings.
- MD 1975 is also a PubMed Central record, but it shows the article's abstract, and the blurb is taken from it.

## Dates and other judgment calls

- ME 2019-05-24. The chaptered law page does not print the approval date. The date comes from the bill status page, which was also fetched: `https://legislature.maine.gov/legis/bills/display_ps.asp?LD=798&snum=129` ("Governor's Action: Signed, May 24, 2019").
- ME 2020-03-03. The Press Herald page's `article:published_time` is 2020-03-04T02:23 UTC, which is the evening of March 3 in Maine. `published` is 2020-03-03. The story reports early returns (76 percent of polling places). The final official tally was not fetched from a primary source.
- ME 1984-07-25 is the effective date printed at the end of the chapter. `published` is null. The act was passed in the 1984 session and is numbered Public Laws 1983, chapter 661.
- ME 2021-09-01. The Maine CDC page is `www.maine.gov`. The same page is also served at `www1.maine.gov`.
- MD 1960, MI 1939, MI 1956, ME 2012, MD 1982 (pertussis), MA 1955: `date` is the year of the event named in the title or text. `published` is null for the journal records, because the records give only a month.
- MD 1975-04-18 is the first day of the outbreak period in the abstract. The article was published in May-June 1977.
- MD 1992-11-16 and MA 1992-11-16 are the days the first case was reported to each state health department. Both happen to be November 16.
- MI 1982-11-14 is the first rash onset date in the report.
- MI 2015-01. `kind` is "policy" because the item is used for the rule change. The page is a press release dated 2016-01-28. The release itself says the drop in waivers was "a result of" the rule. The blurb gives the two facts without the cause.
- MI 1932. `kind` is "history page". The article is a 2010 historical review. `published` is null because the page gives only "August 2010".
- MN 1942-12-17. `published` is the page's "First Published" date, 2012-07-31. The page says it was last modified 2025-12-04.
- MN 2017-04-10 is the day the state was notified. `published` is 2017-07-14, the printed issue date. The page's `article:published_time` tag says 2017-07-12. The pilot used the meta tag date for newer MMWR pages, so this one differs by two days from that convention.
- MS 2023-07-17 is the day the exemptions began. The release is dated 2023-07-14.
- MS 2015-01-12. The claim that Mississippi had the highest kindergarten rate comes from the state release, which cites an MMWR report. The MMWR report itself was not fetched.
- Blurbs for MN 2011, MN 2017, MN 2024 and MA 2017 leave out the ethnic and community details that the sources give.
- `diseases` tags on law and court items are a best fit and are not always spelled out on the page.

## Wanted, not verified (left out)

Maine:

- Polio in Maine in the 1940s and 1950s. PubMed lists Journal of the Maine Medical Association articles (1952, 1956, 1960), but that journal is not in PubMed Central and PubMed blocks scripted requests.
- 1964 diphtheria outbreak at the State Hospital in Augusta and the 1967 "Measles eradication in Maine" article. Same journal, same problem.
- When Maine first required immunization for school. Public Laws 1981, chapter 693 (the education code rewrite) was fetched and has an immunization section, and it also carries an older exclusion provision. The first enactment was not found.
- Official final count for the March 3, 2020 referendum. The Secretary of State posts it only as a spreadsheet. Ballotpedia was fetched and says the question was defeated.
- 2019 measles case (the last one before 2026) and the hepatitis A outbreak that began in 2019. No press release found.
- February 2026 measles cases. The Maine DHHS release was fetched ("Maine CDC Confirms Case of Measles in Maine", 2026-02-06, first case since 2019) but it is outside the 1929 to 2025 range.

Maryland:

- First enactment of the school immunization requirement. The 1982 court opinion cites Education Article section 7-402 and 1978 and 1979 regulations. No statute page was fetched.
- November 2007 Prince George's County court summons for parents of unvaccinated students. News stories exist, but the vaccines at issue were chickenpox and hepatitis B, which are out of scope.
- Baltimore diphtheria immunization in the 1930s and 1940s. No page found.
- 1951 infectious hepatitis outbreak in Baltimore (American Journal of Public Health, 1953). Listed by PubMed. The record was not fetched.
- 2012 congenital rubella cases (MMWR, three states) and 2014 pertussis in a health care worker (MMWR). Seen in the index, left out as minor.

Massachusetts:

- "Measles among children with religious exemptions to vaccination--Massachusetts, Ohio" (MMWR, 1981-11-13). Listed by PubMed. Issues before 1982 are not on the MMWR site and the CDC Stacks search was blocked.
- 2016 mumps outbreak at Harvard and other colleges. The state's October 2016 update is a `mass.gov` document that returned 403 and has no archive capture.
- 2006 measles outbreak in Boston. Not found in the MMWR index.
- Statutes of 1967, chapter 590 (the school immunization law the 1971 court case examined). Session law page not found.
- New England Journal of Medicine papers on the 1955 polio epidemic. Not fetched.

Michigan:

- April 12, 1955 announcement in Ann Arbor of the Salk vaccine field trial results. The University of Michigan School of Public Health page returned 403 (browser check). The national list has an item for this date.
- 1958 Detroit polio epidemic (JAMA, 1959 and 1960). Listed by PubMed only.
- 1978 Public Health Code school immunization sections. Not fetched.
- 1990 Kent County measles outbreak (Pediatric Infectious Disease Journal, 1992). Listed by PubMed only.
- "Diphtheria Prevention in Detroit" (1931) and "Measles in Detroit, 1935" in PubMed Central. The first returned a captcha page. The second was not fetched.

Minnesota:

- 1946 polio epidemic. The Sister Kenny page mentions it in passing. No page of its own was found on MNopedia.
- 1977 and 1979 measles outbreaks (Minnesota Medicine). Listed by PubMed only.
- When the exemption for "conscientiously held beliefs" was added. The current statute page was fetched and lists amendments in 1973, 1978 and later, but the session laws for those years were not fetched.
- August 25, 2017 release declaring the measles outbreak over. The URL is in the archive index. The live page returns 404 and the capture was not fetched.
- 2022 measles releases. In the archive index, not fetched.

Mississippi:

- Enactment of the school vaccination law (Mississippi Code section 41-23-37). The 1979 opinion quotes it from the "1972 Supp." No statute page was fetched.
- The April 2023 federal court order in Bosarge v. Edney. CourtListener returned 202. The state health department's release and Board of Health statement are the sources used.
- Anything before 1979. PubMed lists a 1959 article on polio in Mississippi in 1958 and a 1982 article on a hepatitis A outbreak at a day care center in Forrest County. Neither journal is in PubMed Central.
- No MMWR outbreak report for Mississippi and these diseases was found in the 1982 to 2025 index pages.

## Fetched and verified but not used (available if the editor wants more)

- "Md. High Court Invalidates Exemptions From Immunization" (Education Week, 1982-10-20)
- "Measles Case Confirmed; Possible Exposures in Baltimore Area" (Maryland Department of Health, 2019-04-05, Internet Archive capture)
- "Section 15: Vaccination and immunization" (Massachusetts General Laws chapter 76, current text, malegislature.gov)
- "Epidemiologic Notes and Reports Transmission of Pertussis from Adult to Infant -- Michigan, 1993" (MMWR, 1995-02-03)
- "Hepatitis A vaccination continues to be urged for high risk groups Cases top 900 in state outbreak" (Michigan DHHS, 2018-11-08, Internet Archive capture; 905 cases as of November 7, 2018)
- "MDCH and Physician Organizations Remind Parents about New Immunization Rules" (Michigan, 2010-08-16, Internet Archive capture)
- "Notes from the Field: False-Positive Measles Test — Maine, February 2012" (MMWR)
- "121A.15 HEALTH STANDARDS; IMMUNIZATIONS; SCHOOL CHILDREN." (Minnesota Statutes, current text)
- "Health Officials Investigate Measles Exposure in Mississippi (Updated April 23)" (Mississippi State Department of Health, 2019-04-19, Internet Archive capture)
- "Position Statement of the Mississippi State Board of Health" (PDF, 2023-07-14)
- "Maine Voters Turn Out In Force To Decide Party Primaries, Vaccination Referendum" (Maine Public, 2020-03-03)

## Final check

Run on 2026-10-02. All six files loaded. 42 items. All keys present, `scope` matches each file name, no duplicate (date, headline) within a state. All 42 URLs re-fetched with HTTP 200. Headline found in the fetched page or PDF text for 42 of 42. Supporting phrases for each blurb found for 42 of 42.
