# Milestones batch 6: research notes (NM, NY, NC, ND, OK, OR)

Checked 2026-10-01. Files: `NM.json` (7), `NY.json` (8), `NC.json` (8), `ND.json` (7), `OK.json` (7), `OR.json` (8). 45 items.

## How each item was verified

Every URL was fetched in this session with `curl` and the User-Agent `Mozilla/5.0 (D4TP research; eric@data4thepeople.com)`. PDFs were downloaded and read with a text extractor (pypdf). Each `headline` was copied from the page's own `<h1>`, `<title>` or `citation_title` tag, or from the printed heading of the PDF. A script then loaded all six files, checked the keys, `scope`, `kind`, date formats and duplicate (date, headline) pairs, re-fetched every URL, and confirmed the stored headline appears in the page text. All 45 passed. One earlier run was cut off by a network outage and one PubMed Central page briefly returned a browser check; the full check was run again afterward and all 45 items passed with HTTP 200 and the headline found. The four PDF headings (Phillips v. City of New York, North Dakota House Bill 1093, the North Dakota health advisory, the Oklahoma guide) were matched by the script against the extracted text, not by eye.

The web search tool hit its session limit after the first round of searches. After that, sources were found through MMWR yearly index pages, PubMed Central title searches (NCBI E-utilities), the Internet Archive index, state agency news listings and direct URL fetches. The lists are thinner on mid-century state items than more searching would have allowed.

## Internet Archive captures

- NY 2019-04-09, New York City emergency declaration. The live `nyc.gov` page loads its text with JavaScript and shows only "News" to a scripted request. The capture is of the same `www1.nyc.gov` page.
- NY 2019-06-13, Governor's signing release. The live `governor.ny.gov` page returned 403.

## Headlines that are awkward as display headlines

- ND `HOUSE BILL NO. 1093` (1975). Bare bill number. The printed heading block is "CHAPTER 224 / HOUSE BILL NO. 1093 / (Eagles) / INOCULATIONS". The link opens the 62-page Health chapter of the 1975 Session Laws at page 18. A friendlier option that was also fetched and verified is the Dakota Datebook entry `Measles in Schools` (Prairie Public, 2020-12-08), which opens with the 1975 law.
- ND Dakota Datebook titles are short and generic: `Whooping Cough`, `Worst Polio Outbreak`, `Polio Vaccinations Expand`, `Sabin Oral Vaccine`.
- OR `SB 132 Enrolled` (2013). The page has no `<h1>`. The visible heading is "2013 Regular Session SB 132 Enrolled". The `<title>` is "SB132 2013 Regular Session - Oregon Legislative Information System".
- OR `433.267 Immunization of school children; rules; exceptions; effect of failure to comply.` Bare statute title. The URL is the whole ORS chapter 433 page, which has no anchor for the section.
- NC `§ 130A-152. Immunization required.` Bare statute title.
- NC `Infectious Diseases` (1939) and `Polio in North Carolina` (1948 and 1959). Generic encyclopedia titles. `Polio in North Carolina` is used twice, at two dates.
- NM `EXEMPTION FROM SCHOOL, CHILDCARE, AND PRE-SCHOOL IMMUNIZATION`. Rule title in capitals. On the page it is preceded by "PART 3".
- OK `SCHOOL ADMINISTRATOR’S GUIDE TO OKLAHOMA’S IMMUNIZATION LAW`. In capitals, printed over three lines on page 2 of the PDF and joined here. The cover page says "School Administrator’s Guide To Immunizations". It is used twice (1970 and 1990).
- NY `De Blasio Administration's Health Department Declares Public Health Emergency Due to Measles Crisis` and `Governor Cuomo Signs Legislation Removing Non-Medical Exemptions from School Vaccination Requirements`. Both name an official as the actor. They are the real headlines. The blurbs do not name anyone.
- Old MMWR titles keep their section prefixes and double or triple hyphens as printed.
- OR `Suffer the Infants: A Severe Case of Pertussis in Oregon, 2012`. A case report, not a count of the 2012 outbreak.

## Dates and other judgment calls (inferred, not stated outright)

- `diseases` tags on law, rule and court items are a best fit. The Oklahoma guide does not say which vaccines the 1970 law covered. The Oregon statute and New Mexico rule name no diseases. Phillips v. City of New York is about the school requirement as a whole.
- ND Datebook dates. Each entry says "On this date in <year>" and was published on that calendar day, so the date is built from the two: 1946-07-19, 1955-10-11, 1962-09-17. For 1938-10-14 the entry cites The Halliday Promoter, October 14, 1938 (the archive page was posted 2022-05-27 and first aired 10/14/2012). The 1962 date is the day the Bismarck Tribune reported the clinic, which the entry says was held on a Sunday.
- ND 1975-03-20 is the approval date printed in the session law. The 1975 text has only a medical exemption plus a line that parents must be told of their right to refuse. The current statute (N.D.C.C. 23-07-17.1, fetched) lists religious, philosophical and moral beliefs. When that wording was added was not verified.
- OK 1970-04-15 comes from the statute history note in the guide's appendix ("Added by Laws 1970, c. 225, § 1, emerg. eff. April 15, 1970"). The guide's own text says only "In 1970". The guide's revision date is April 2011, so `published` is null.
- NC 1957 is the first year in the history note at the end of G.S. 130A-152. The blurb describes the current text. NCpedia says the 1957 law covered diphtheria, tetanus and whooping cough before age one and smallpox before school.
- NC 1959: the source is a history page from the North Carolina History Project (a John Locke Foundation site). NCpedia says the same thing ("In 1959 North Carolina became the first state to initiate compulsory inoculation with the Salk vaccine"). The 1959 session law itself was not fetched.
- NY 1989-04: the source is a 1991 Public Health Reports article by New York State Department of Health staff. `kind` is "history page" and `published` is null because PMC gives only "1991 May-Jun".
- NY 2019-05-17 is the MMWR issue date. The page's metadata date is 2019-05-16.
- OR 1973 is the first year in the history note of ORS 433.267 ("1973 c.566 §2"). The blurb describes the current text.
- OR 2013: the OLIS page shows SB 132 became chapter 516 of the 2013 laws. No signing date is on the page, so the date is the year only.
- OR 2019-05-06: the KVAL story covers only the House vote. The OLIS page for HB 3063 (fetched) shows the bill's last location as "In Senate Committee" with no chapter number, so it did not become law. The blurb does not say that because the news page does not.
- OR 2012: the date comes from the article title. The article was published in 2015.
- Title-only PubMed Central records (blurbs say only what the record shows): NC 1936-02, OR 1972-01, OR 1978-05. The article PDFs were not read.
- NM 2024-10-29 and NC 2024-12-03: the sources give a doubling or a multiple, not a percentage, and no prior-year count. The blurbs avoid a multiplier.
- OK 2016-12-15: the Enid News & Eagle page puts most of the story behind a script. The blurb uses only the two opening paragraphs that are in the page.

## Wanted, not verified (left out)

New Mexico:

- 1959 school immunization law (NMSA 24-5-1 to 24-5-3). Justia returned 403. The "Laws 1959, ch. 329" history was seen only in a search snippet.
- 1996 measles outbreak. Mentioned only in passing in the 2025 state release.
- Any item before 1984. None found.
- May 2024 "Department of Health confirms first cases of measles since 2021". Seen in the state news listing, not fetched.

New York:

- 1966 enactment of Public Health Law 2164 and its later religious exemption. `nysenate.gov` returned 403.
- 2019 bill page for S2994A/A2371. `nysenate.gov` returned 403.
- F.F. v. State of New York (Appellate Division, 2021), which upheld the 2019 repeal. `nycourts.gov` returned 403.
- March 2019 Rockland County emergency declaration. Not fetched.
- 1916 and 1944 polio epidemics. 1916 is out of range. No 1944 page fetched.

North Carolina:

- 1944 Hickory emergency polio hospital. Only mentioned on the Polio in North Carolina page.
- 1939 and 1959 session laws themselves. Only encyclopedia pages were fetched.
- 2015 Senate Bill 346 (would have ended the religious exemption, withdrawn). Not fetched.
- 2025 and 2026 measles cases. The state press release listing was fetched but no measles release was opened.
- 1978 Buncombe County measles outbreak (MMWR, 1978). Only the CDC Stacks record page was fetched, not the PDF.

North Dakota:

- 2011 measles case and the 2025 outbreak's final count. Not fetched.
- When religious, philosophical and moral exemptions were added to the school law. Not found.
- North Dakota having no measles cases during the 1989 to 1991 national epidemic. A 2025 Bismarck Tribune story says so in its opening lines; the rest is behind a paywall. Left out.
- 1949 polio outbreak paper. PubMed record only (blocked).

Oklahoma:

- 1998 addition of hepatitis A vaccine to the school requirements. The guide's table shows a hepatitis A column starting with kindergarten in 1998-1999, but the extracted text is hard to read with confidence.
- 1976 amendment as its own item. It is in the guide ("extended requirements to all children attending Oklahoma schools").
- Final count for the 2025 measles cases. Not fetched.
- Polio-era items. The Oklahoma Historical Society encyclopedia has no search a script can use.

Oregon:

- 1973 House Bill 2042 and the 1981 "exclusion day" law as dated events. Seen only in a search summary that drew on advocacy sites.
- 2015 Senate Bill 442. Not fetched.
- 2019 measles cases in Multnomah County. The Oregon Health Authority release returned 404.
- The Oregon Health Authority's own releases for the 2024 measles outbreak and the 2025 whooping cough record. News stories are used. The KTVZ story says it reprints the agency's announcement.
- 1991 measles (93 cases). Seen only in a search snippet.

## Fetched and verified but not used (available if the editor wants more)

- NM: "Measles Outbreak — New Mexico, 2025" (MMWR, 2026-03-12), 99 outbreak cases February to August and the September 26 end date. "New Mexico reports 100 measles cases" was seen in the listing only.
- NY: "Epidemiologic Notes and Reports Measles Outbreak -- New York City" (MMWR, 1984-10-19); "Rubella and Congenital Rubella Syndrome -- New York City" (MMWR, 1986-12-19); "Mumps Outbreak --- New York, New Jersey, Quebec, 2009" (MMWR, 2009-11-20); "Notes from the Field: Measles Outbreak Among Members of a Religious Community — Brooklyn, New York, March–June 2013" (MMWR, 2013-09-13); "Mayor de Blasio, Health Officials Declare End of Measles Outbreak in New York City" (2019-09-03, Internet Archive capture); "New Law on School Vaccination Requirements" (New York State Department of Health publication 2196, June 2019); title-only PMC records "Resurgence of measles in New York" (1972), "The control of measles in New York City" (1974), "Factors in Participation in the 1954 Poliomyelitis Vaccine Field Trials, Erie County, New York" (1959).
- NC: "Epidemiologic Notes and Reports Foodborne Hepatitis A -- Alaska, Florida, North Carolina, Washington" (MMWR, 1990-04-13); "§ 130A-157. Religious exemption." (history note starts 1957).
- ND: Dakota Datebook entries "Measles in Schools", "Vaccine Mandates" (a 1919 law banned vaccination as a condition of school until the 1975 law replaced it), "Salk Polio Vaccine Shortage" (1955-07-08), "The Salk Vaccine" (1954 Fargo trial clinics); N.D.C.C. chapter 23-07 (current text of 23-07-17.1); 2021 state health department testimony on House Bill 1377.
- OR: "Notes from the Field: Retrospective Analysis of Wild-Type Measles Virus in Wastewater During a Measles Outbreak — Oregon, March 24–September 22, 2024" (MMWR, 2026-01-15); the OLIS page for 2019 HB 3063; "Five-Year Follow-up of a Severe Case of Pertussis in Oregon, 2012" (Public Health Reports, 2019).
