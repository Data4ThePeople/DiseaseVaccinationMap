# Milestones batch 5: research notes

States: Missouri, Montana, Nebraska, Nevada, New Hampshire, New Jersey. Checked 2026-10-01.

Files: `MO.json` (7 items), `MT.json` (7), `NE.json` (6), `NV.json` (6), `NH.json` (7), `NJ.json` (8). 41 items in all.

## How each item was verified

Every URL was fetched in this session with `curl` and the User-Agent `Mozilla/5.0 (D4TP research; eric@data4thepeople.com)`. The headline was copied from the page's own `<h1>`, `<title>` tag, `citation_title` tag or printed heading. A script then loaded all six files, checked the keys, the `scope`, the disease keys, the `kind` values, the date formats and duplicates, and re-fetched each URL to confirm the stored headline appears in the page. See "Final check" at the bottom for the result.

Old MMWR pages (1982 to 2011) carry the issue date in a `Date` meta tag and a `reportDate` script variable. That is the `published` value. For newer MMWR pages `published` is the `article:published_time` meta tag, which is one day before the printed issue date. This matches the pilot.

The web search tool ran out of its session budget early in this batch. Leads after that came from the CDC site search (`search.cdc.gov`), PubMed Central title searches, the CourtListener search API, and the Internet Archive index of each health department's news folder. This limited how many state news and legislature pages could be found, mostly for New Jersey policy items.

## Internet Archive captures (8 items)

- MO 2019-08-21 and MO 2025-04-18. The live `health.mo.gov` news URLs now return 404 after a site redesign.
- MT 2005-09-01 and MT 2013-05-15. Old `dphhs.mt.gov/newsevents/` pages that no longer exist on the live site.
- MT 2021-07-01. The House Bill 334 text. The live `leg.mt.gov` and `archive.legmt.gov` bill URLs returned 404.
- NH 2019-02-05, NH 2022-07-19 and NH 2024-07-09. The live `dhhs.nh.gov` site returned 403 "Access Denied" to scripted requests.
- NJ 1959-06-22. The live Justia page returned 403 (browser check). The same opinion was also read in full from the Harvard case law file `static.case.law/nj-super/56/cases/0245-01.json`.

## Headlines that are awkward as display headlines

- MO 1961: `167.181. Immunization of pupils against certain diseases compulsory — exceptions — records — to be at public expense, when — fluoride treatments administered, when — rulemaking authority, procedure.` Bare statute title. The em dashes are in the source.
- MO 2021: `20-1222 - B.W.C., et al v. Randall Williams, et al`. This is the GovInfo page title for the court opinion. It starts with the docket number.
- MT 1979: `Immunization Required -- Release And Acceptance Of Immunization Records -- Notice Of Exemptions Required`. Bare statute title.
- MT 1983: `Interstate Transmission of Measles in a Gypsy Population -- Washington, Idaho, Montana, California`. The 1983 CDC title uses an ethnic term that is now considered outdated or offensive. The blurb does not repeat it. The editor may want to drop this item.
- MT 2021: `AN ACT REVISING LAWS RELATED TO THE MEDICAL EXEMPTION TO STUDENT IMMUNIZATION REQUIREMENTS; ...`. This is the bill's own long title, with mixed capitals as in the page source. The page has no shorter visible heading. The line "house bill NO. 334" is in the page source but is hidden by the page's style sheet.
- NE 1973: `Nebraska Revised Statute 79-217`. Bare statute number.
- NV 1971: `NRS: CHAPTER 392 - PUPILS`. The page is the whole chapter. The link opens at section 392.435. The section's own heading is much longer.
- NH 1987: `Section 141-C:20-a Immunization.` Bare statute title.
- NH 2022: `Immunization Exemptions for Children`. Generic page title for the House Bill 1035 change.
- NH 1981 and NH 1984, NJ 1981: old MMWR titles carry the `Epidemiologic Notes and Reports` prefix as printed.
- NJ 1983 and NJ 1985: `Mumps Outbreak -- New Jersey` and `Measles -- New Jersey`. Short titles with no year.
- NV 2015: `Health District identifies 3rd and 4th measles cases`. Does not name the place.
- NE 2008, NE 2019, NJ 2021: long MMWR titles.

## Thin source

- NJ 1960-07, `New Jersey's action program to prevent poliomyelitis`. The PubMed Central record shows only the title, three authors, journal and date. The article PDF sits behind a browser check and could not be downloaded. The blurb says only what the record shows. PubMed Central sometimes returns a reCAPTCHA page to scripted requests; a retry a few seconds later worked.

## Dates and other judgment calls (things inferred, not stated outright)

- Statute items (MO 1961, MT 1979, NE 1973, NV 1971, NH 1987). The `date` is the earliest year in the history or source note printed under the current section. The pages show the current text, not the text as first enacted, so the blurbs say "now requires". An earlier law may have existed under a different section number; the pages do not say. For Missouri the note reads `(L. 1963 p. 200 § 8-18, ...) (Source: L. 1961 p. 349 §§ 1 to 6)`, and 1961 is used. For Nebraska the first sources are `Laws 1973, LB 173` and `LB 546`. "Rubeola" in the statutes is written as measles in the blurbs.
- `diseases` tags on law and court items are a best fit. They list the in-scope diseases the law names. The Missouri court case is about the exemption form, not one disease.
- MO 2021 court item. The URL is the GovInfo details page, which holds the opinion. The blurb's facts were read from the opinion PDF itself (`https://ecf.ca8.uscourts.gov/opndir/21/03/201222P.pdf`, filed March 5, 2021). The PDF has no usable title, so the GovInfo page title is the headline.
- MT 1955. The source is a 2017 newspaper history column. It quotes a Helena newspaper saying that "by the following summer" about 35,000 first and second graders were expected to get their first polio shots. The column places this after an August 1954 story, and the writer says "it was probably the summer of 1955". The year 1955 is that reading.
- MT 1983. `date` is 1983-09-04, the rash onset in Billings. The report covers four states and only three later cases were in Montana.
- MT 2021. `date` is the bill's stated effective date. That the bill became law was confirmed two ways: a Legislative Services summary PDF lists it as "Chapter Number Assigned", and the current code's history note shows `Ch. 294, L. 2021`. `published` is null.
- NE 1991. `date` is 1991 for a study of the 1991-92 school year. This is a vaccination coverage study, not an outbreak.
- NE 2008. `date` is 2008-09, the first month in the report's title. NE 1999 uses the first day of the period the county counted cases.
- NE 2025. The state's news release does not say "first since 2017". A Nebraska Health Alert Network update dated June 4, 2025 (also fetched) does. The blurb leaves that out.
- NV items from 2008 to 2025 are from the Southern Nevada Health District, which covers Clark County (Las Vegas), not the whole state. No state health department page was found.
- NV 2008. The headline is the page `<title>` text. The page body prints a longer, lower-case version.
- NH 1981. `date` is 1981-11-18, the rash onset of the New Hampshire case. Only three of the 25 cases were in New Hampshire.
- NH 2006. `date` is 2006-03, when the first hospital worker was seen. The report was published in 2007.
- NH 2022. `kind` is "policy". The source is a health department page that describes House Bill 1035. The statute page (`141-C:20-c`, also fetched) shows `2022, 55:1, eff. July 19, 2022`. It also shows a later change, `2026, 253:2, eff. Aug. 31, 2026`, which is outside the date range and is not used.
- NJ 1959. This is the appeals court ruling. The opinion says it affirms the lower court. Any later appeal was not checked.
- NJ 2010-01-29 (mumps). `date` is the "as of" date for the case count on the page. The outbreak began in New York in June 2009.
- NJ 2018. `date` is the rash onset of the first New Jersey case.
- NJ 2021. `date` is 2021-09-06, when the base learned of the exposure. No measles cases at the base are reported on the page; the item is about the vaccination campaign.

## Wanted, not verified (left out)

Missouri:

- 1970 to 1971 St. Louis measles epidemic. No source page found.
- 1989 measles in Missouri. Two national MMWR reports were fetched (237 Missouri cases in the first 26 weeks of 1989; a rate of 13.1 per 100,000 for the year). Left out because they are national reports, not Missouri reports.
- A Missouri Independent story on the first 2025 measles case. Blocked (403). The state's own release is used instead.
- When the religious exemption was added to Missouri law. Not stated on the statute page.

Montana:

- 1985 to 1988 measles outbreaks (Montana had one of the highest measles rates in 1988, per a search snippet). No Montana report found on the CDC site search.
- 2021 House Bill 702 (ban on discrimination by vaccination status). Fetched in a KFF Health News story and the legislative summary. Left out because it is mostly about COVID-19 era rules.
- 2023 changes to the exemption law (Ch. 534, L. 2023). The session law page returned 404.
- The live bill status page for House Bill 334. It needs JavaScript.

Nebraska:

- Any outbreak before 1990. None found on the CDC site search or PubMed Central.
- The 2009 bill that added the seventh grade whooping cough booster (in effect July 1, 2010). The requirement is in the text of section 79-217, but the bill page was not found.
- 2006 multi-state mumps outbreak in Nebraska. Not fetched.
- Rising religious exemptions (Flatwater Free Press, 2025). Seen in search results, not fetched.

Nevada:

- Any outbreak before 2005. None found. The 1974 MMWR issue on CDC Stacks was read; it only lists Nevada in the weekly tables.
- 2019 Assembly Bill 123 and the 2017 and 2019 debates on exemptions. A June 2020 Research Division brief was fetched but no bill page was.
- Washoe County's December 2025 measles case. Seen in search results, not fetched.
- A state health department (not county) page on any item.

New Hampshire:

- 2011 whooping cough outbreak (a Journal of Clinical Microbiology paper title was seen in a search, not fetched).
- The House Bill 1035 bill page itself.
- 2025 House Bill 358 on the religious exemption form. Seen in a search snippet only.
- University mumps outbreaks in 2016 and 2017. No source found.

New Jersey:

- 1974 religious exemption law (N.J.S.A. 26:1A-9.1) and the school immunization rules (N.J.A.C. 8:57-4). The state statute site needs JavaScript. The health department's rules page was fetched but states no dates.
- December 2007 Public Health Council vote adding vaccines for school (in effect 2008). No source found.
- January 2020 failure of the bill to end the religious exemption (S2173). No source found.
- 1948 Sadlock v. Board of Education of Carlstadt. Fetched and read. Left out because it is about smallpox vaccination, which is out of scope.
- Final count for the 2018 to 2019 Ocean County measles outbreaks from the state health department. The department's Measles Archive page was fetched but the MMWR report is used.

## Fetched and verified but not used (available if the editor wants more)

- "Hepatitis A vaccine now recommended for all children ages 2-18" (Missouri DHSS, 2019-08-29, Internet Archive)
- "Missouri DHSS announces possible measles exposure in St. Louis" (2025-05-04) and "Measles in Missouri – What Should You Know?" (2025-05-29), both Missouri DHSS on GovDelivery
- "Measles Outbreak Associated with Adopted Children from China — Missouri, Minnesota, and Washington, July 2013" (MMWR; title seen on the CDC site search, page not read)
- "Pertussis Cases on the Rise in Montana" (Montana DPHHS, March 2008) and "Pertussis outbreaks continue to occur throughout Montana" (April 2012), both Internet Archive
- "Montana Considers New Wave of Legislation to Loosen Vaccination Rules" (KFF Health News, 2023-03-10)
- "Montana House passes one bill on vaccine exemptions, two others fall short" (KTVH, 2021)
- "Measles Detected in Nebraska" (Nebraska DHHS Health Alert Network update, 2025-06-04, PDF)
- "Nebraska Revised Statute 79-221" (exemptions; first source Laws 1993)
- "Health District Reports Increase in Pertussis Cases" (Southern Nevada Health District, 2012-07-09)
- "Southern Nevada Health District Corrects Number of Mumps Cases" (2007-12-12)
- "Health Alert: Hepatitis a Outbreak" (Southern Nevada Health District, 2013-05-31)
- "IMMUNIZATION REQUIREMENTS FOR NEVADA STUDENTS" (Nevada Legislative Counsel Bureau Research Division, June 2020, PDF)
- "Hepatitis A Outbreak In New Hampshire Accelerating" (New Hampshire DHHS, 2019-04-16, Internet Archive)
- "Section 141-C:20-c Exemptions." (New Hampshire statute)
- "Mumps Outbreak --- New York, New Jersey, Quebec, 2009" (MMWR, November 2009)

## Final check

The script ran over all six files after the last edit. All 41 items passed: every key present, `scope` matches the file name, no duplicate (date, headline) within a state, every URL returned HTTP 200, and every stored headline was found in the re-fetched page. No blurb contains an em dash or en dash.

How the headline match works: HTML entities are decoded, tags are stripped and white space is collapsed before comparing. Two headlines only match that way and not as a raw string:

- MT 2005 `Immunization Requirement for 7th Graders Revised`. The page writes "th" in a superscript tag.
- MT 2021, the long act title. The page source breaks it across lines and tags.

No headline was checked by eye. The only PDFs read in this batch (the Eighth Circuit opinion, the Nebraska health alert, the Nevada research brief, the Montana legislative summary) are supporting documents, not item URLs.

`checked` is 2026-10-01 on every item, the day the pages were first fetched. The final script run finished early on 2026-10-02.
