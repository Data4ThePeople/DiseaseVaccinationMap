# Milestones: research notes

Checked 2026-10-01. Files: `milestones_national.json` (47 items), `milestones_pilot_states.json` (23 items: OH 8, TX 7, CA 8).

## How each item was verified

Every URL in the two JSON files was fetched in this session with `curl` (or, for PDFs, downloaded and read with a PDF text extractor). The `headline` was copied from the page's own `<h1>` or `citation_title` tag, or from the document's own printed heading for PDFs. A script then checked that each HTML headline string appears verbatim in the saved page. No headline was taken from a search snippet.

`date` is the event date when the page states one, otherwise the publication date. `published` is the page's own publication or last-updated date when stated in full, otherwise null.

## National counts by decade

| Decade | Items |
|---|---|
| 1920s | 1 |
| 1930s | 2 |
| 1940s | 2 |
| 1950s | 4 |
| 1960s | 6 |
| 1970s | 2 |
| 1980s | 4 |
| 1990s | 7 |
| 2000s | 6 |
| 2010s | 6 |
| 2020s | 7 |

## Things the editor should know

### Thin sources (title-only pages)

Nine pre-1970 items point to PubMed Central records of scanned journal articles (1928, 1936 x2, 1942, 1948, 1955-10, 1967, 1968). The PMC page shows only the title, authors, journal, date and (sometimes) a "read before" footnote. The article PDF sits behind a browser check and could not be downloaded. The blurbs for these items say only what the record page shows. They do not describe findings.

### Headlines that are awkward as display headlines

- `Public Law 87-868` (1962). This is the Vaccination Assistance Act of 1962. The statute PDF has no cleaner heading. The short title appears in the body text.
- `TITLE III—VACCINE COMPENSATION` (1986). This is the National Childhood Vaccine Injury Act of 1986, which is Title III of Public Law 99-660. The link opens the PDF at that page. The heading has an em dash that is in the source.
- `Historical Vaccine Concerns` (1955, Cutter incident). Generic CDC page title.
- `History of Measles` (1963), `Impact of U.S. MMR Vaccination Program` (1964 rubella epidemic), `Vaccine History: Developments by Year` (1971 MMR), `About the Vaccines for Children (VFC) Program` (1993), `Dr. Albert Sabin: A Closer Look` (1961). Generic history-page titles that do not name the event.
- `Measles Cases and Outbreaks` (2026). A live CDC page that is updated weekly. The count in the blurb (3,659 as of September 24, 2026) will go stale. Re-fetch before publishing.
- `Poliomyelitis Prevention in the United States` (2000). Does not say this is the switch to IPV only.
- Old MMWR titles carry section prefixes and double or triple hyphens exactly as printed: `Current Trends ...`, `Epidemiologic Notes and Reports ...`, `International Notes ...`, `Notice to Readers ...`, `Measles --- United States, 2000`.
- Several ACIP titles are very long (1997 DTaP, 2006 Tdap, 2018 mumps third dose).
- `U.S. Reports: Bruesewitz v. Wyeth, 562 U.S. 223 (2011).` is the PDF's embedded title. The first printed line of the opinion is `BRUESEWITZ et al. v. WYETH LLC, fka WYETH, INC., et al.`
- `Section 3313.671 | Proof of required immunizations - exceptions.` (Ohio statute), `SB-277 Public health: vaccinations.`, `SB-276 Immunizations: medical exemptions.`, `AB-2109 Communicable disease: immunization exemption.` (California bills). Bare statute and bill titles. For the California bills the page `<h1>` also appends the session, for example `(2015-2016)`. That suffix was left off.
- `Texas Immunization Exemptions` (2025). Generic page title for the House Bill 1586 change.
- `Ohio measles outbreak continues to grow` (CNN, 2014). This is the on-page headline. The browser tab title is different: `2014 measles outbreak: Ohio cases more than double`.

### Dates and other judgment calls

- Ohio items from the Ohio Department of Health use Internet Archive (Wayback Machine) URLs. The live `odh.ohio.gov` site returned 404 to every scripted request, including the home page.
- Ohio 2025-03-26 release: the archived page prints both "March 26, 2025" and "March 25, 2025 FOR IMMEDIATE RELEASE". The JSON uses March 26.
- Ohio statute: `date` is 2023-10-03, the effective date of the current version shown on the page. It is not the date the school requirement was first enacted.
- Texas 1971 school law: the source is a 1975 Public Health Reports article by two Texas State Department of Health staff. `kind` is "history page", `date` is 1971, `published` is 1975-01-01 as CDC Stacks lists it (the issue is January-February 1975).
- Texarkana 1970: the source is a CDC teaching case study (2003 version) based on a 1972 JAMA paper. `kind` is "history page".
- Texas 2025 outbreak start: the source is an MMWR report published 2026-06-18. `date` is 2025-01-29, the first day of the period the report covers.
- "Measles --- United States, 2000" was published in 2002. `date` is 2000. The page says the data suggest measles "is no longer endemic". It does not use the word "declared". The CDC History of Measles page (used for 1963) is the one that says measles "was declared eliminated" in 2000.
- Rubella elimination: `date` is 2004-10 (when the panel met), `published` is 2005-03-25.
- The 2026-01-05 CDC release does not name hepatitis A in its text. The blurb only lists the vaccines the release names as recommended for all children.
- The 2025-12-08 Education Week item is the only news source in the national list. The Supreme Court's own order was not fetched.
- `diseases` tags on law and schedule items are a best fit and are not always spelled out on the page.

## Wanted, not verified (left out)

National:

- 1938 founding of the National Foundation for Infantile Paralysis (March of Dimes). No source page fetched.
- 1949 combined DTP vaccine as its own item. Only mentioned in passing on the CHOP history page ("combined in 1948").
- 1952 polio peak (about 57,900 cases). Seen only in a search snippet. The 1951 and 1953 Public Health Reports records were fetched but show no text.
- 1954 Salk field trial.
- 1963 trivalent oral polio vaccine licensure.
- 1967 mumps vaccine and 1969 rubella vaccine licensures as separate items. Covered only inside the CHOP and CDC history pages.
- 1966 to 1967 federal measles eradication announcement as a dated event. Only the 1967 paper title is used.
- 1977 Childhood Immunization Initiative announcement as its own item (the 1982 MMWR follow-up is used) and the 1978 goal to eliminate measles by 1982 (mentioned on the CDC History of Measles page).
- 1988 start of the Vaccine Injury Compensation Program and the April 8, 1988 MMWR notice on the vaccine injury act. HRSA and PubMed blocked scripted requests. The MMWR HTML page was not found.
- 1990 start of the Vaccine Adverse Event Reporting System. MMWR page fetched; left out because it is not tied to one disease.
- 1991 first acellular pertussis (DTaP) licensure and 2005 Tdap licensures (FDA pages not fetched).
- 2010 national pertussis count. Only the California report is used.
- September 2025 ACIP vote on the combined MMRV vaccine. The HHS press release returned 403.
- September 2026 Supreme Court denial of a New York family's request for a religious exemption. The Washington Post page was blocked. An OSV News story was fetched but not used.
- Congress.gov pages for the 1962 and 1986 acts. Blocked (403). The statute PDFs from govinfo.gov are used instead.
- Supreme Court school vaccination rulings (Jacobson v. Massachusetts 1905, Zucht v. King 1922) fall before 1928.

Ohio:

- 2014 Amish measles outbreak final count (383 cases, NEJM 2016). NEJM returned 403. The CNN story from May 2014 is used instead.
- 2014 mumps outbreak tied to Ohio State University. A conference abstract was fetched but not used.
- 1993 Cincinnati pertussis epidemic (NEJM 1994). Blocked.
- When Ohio first enacted school-entry vaccine requirements. No source fetched.

Texas:

- 2013 measles outbreak linked to a Tarrant County church. No state health department page fetched.
- 1971 House Bill 140 legislative record. The Legislative Reference Library page was fetched but the caption did not come through.
- 2003 House Bill 2292 bill page. Fetched (`78(R) History for HB 2292`) but the House Research Organization report is used because its title is clearer.

California:

- 1961 law requiring polio vaccination for school with a personal belief exemption (AB 1940). PubMed blocked scripted requests.
- June 2010 state declaration of a pertussis epidemic (state press release). Not found.
- 2014 pertussis epidemic MMWR and 2010 AB 354 (Tdap for 7th grade). Both fetched and verified, left out to keep the state list at eight. They can be added.

## Fetched and verified but not used (available if the editor wants more)

- "Recommended Procedures for Diphtheria Immunization: Sub-Committee on Evaluation of Administrative Practices of the Committee on Administrative Practice" (AJPH, June 1935)
- "Poliomyelitis in the United States, 1951" (Public Health Reports, June 1952)
- "Notice to Readers: 50th Anniversary of the First Effective Polio Vaccine --- April 12, 2005" (MMWR)
- "Progress of measles eradication in the United States" (Public Health Reports, March 1968)
- "Editorial. Childhood immunization initiative off to a good start" (Public Health Reports, May-June 1978)
- "Notice to Readers Deadline for Filing Claims for Compensation Under the National Childhood Vaccine Injury Act" (MMWR, 1990-08-10)
- "Reported Vaccine-Preventable Diseases -- United States, 1993, and the Childhood Immunization Initiative" (MMWR, 1994-02-04)
- "Prevention of Hepatitis A Through Active or Passive Immunization" (MMWR, 1996-12-27 and 1999-10-01)
- "Poliomyelitis Prevention in the United States: Introduction of A Sequential Vaccination Schedule ..." (MMWR, 1997-01-24)
- "Update: Measles --- United States, January--July 2008" (MMWR, 2008-08-22)
- "Updated Recommendations for Use of ... (Tdap) in Pregnant Women ..." (MMWR, 2013-02-22)
- "Pertussis Epidemic — California, 2014" (MMWR, 2014-12-05)
- "Epidemiologic Notes and Reports Multiple Measles Outbreaks on College Campuses -- Ohio, Massachusetts, Illinois" (MMWR, 1985-03-15)
- "Texas announces end ..." companion pages: "DSHS provides update on measles outbreak" (Texas DSHS)
