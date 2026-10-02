# State milestones, batch 8: VT, VA, WA, WV, WI, WY

Checked 2026-10-01. Files: `VT.json` (6), `VA.json` (6), `WA.json` (8), `WV.json` (8), `WI.json` (7), `WY.json` (5). 40 items.

## How each item was verified

Every URL was fetched in this session with `curl` and the user agent `Mozilla/5.0 (D4TP research; eric@data4thepeople.com)`. PDFs were downloaded and read with PyMuPDF. The `headline` was copied from the page's own `<h1>`, `<h2>`/`<h3>`/`<h4>` caption, `citation_title` tag, or the PDF's printed heading.

A script then loaded all six files and checked: all ten keys present and in order, `scope` matches the file name, `kind` and `diseases` use allowed values, dates are well formed and fall in 1929 to 2025, no duplicate (date, headline) within a state, no dashes in blurbs. It re-fetched all 40 URLs and confirmed the stored headline appears in the page text (whitespace collapsed, HTML entities decoded). All 40 passed. One CDC page timed out on the first pass and passed on the re-run.

Headlines checked against PDF text by the script, and also read by eye:

- VT 2016, `Act No. 37 (H.98). Health; public health; reportable diseases` (the PDF prints two spaces after `(H.98).`; stored with one).
- WA 2011, `K-12--IMMUNIZATION--EXEMPTION`.
- WA 2019, `MEASLES, MUMPS, AND RUBELLA VACCINE--SCHOOLS AND DAY CARE CENTERS`.

## Sites that blocked or failed

- Internet Archive was offline during this session ("Temporarily Offline", HTTP 503). **No item uses an Internet Archive capture.**
- Blocked scripted requests (403 or a browser check): law.justia.com, courtlistener.com pages, caselaw.findlaw.com, pubmed.ncbi.nlm.nih.gov, stacks.cdc.gov search, westvirginiawatch.com, encyclopediavirginia.org, amhistory.si.edu, the Wisconsin DHS site search, and Wisconsin DHS news lists before 2024.
- The session's web search allowance ran out early. Most discovery was done from the MMWR yearly index pages (1982 to 2026), PubMed title searches through the NCBI E-utilities API, and each state site's own news lists and search.

## Date rules used

- `date` is the event date when the page states one. For reports published in a later year than the event, `date` is the event date or year and `published` is the report's date. Examples: VT pertussis `1996` (published 1997-09-05), WA pertussis `1984` (published 1985-07-05), WV infant death `2004-12` (published 2005-01-28), WY pertussis total `2025` (published 2026-03-11).
- For newer MMWR pages, `published` is the page's `article:published_time`, which is one day before the printed issue date. This matches the pilot.
- Laws: VT 2012 uses the effective date on the summary page (2012-07-01). VT Act 37 uses 2016-07-01, the date the summary says the philosophical exemption ended; the act itself is from 2015. VA HB 1090 uses its delayed effective date (2021-07-01); it became Chapter 1223 on 2020-04-22. WA bills use the governor's approval date printed on the session law (both happen to be May 10). WV SB 286 uses the approval date (2015-03-31); it took effect 2015-06-16.

## Awkward display headlines

- VT 1979: `§ 1121. Immunizations required prior to attending school and child care facilities`. Bare statute title.
- VT 2012: `Act No. 157 (S.199). Health; immunizations`. Act summary heading.
- VT 2016: `Act No. 37 (H.98). Health; public health; reportable diseases`. Does not mention the philosophical exemption. The act's formal title is "An act relating to reportable disease registries and data".
- VT 2024 and 2025: `Health Department Confirms Case of Measles in Vermont` and `Vermont Department of Health Confirms Case of Measles`. Nearly the same. The department reused the second headline for a 2026 release at a different URL.
- VA 2021: `HB 1090 Immunizations; regulations by State Board of Health.` Bare bill title.
- VA 2025: `Updated: Virginia Health Officials Confirm First 2025 Measles Case in the State`. The "Updated:" prefix is on the page.
- VA 2021 and WI 2021 share one MMWR headline (`Public Health Actions to Control Measles Among Afghan Evacuees ...`). It is long and names neither state.
- WA 1979: `Immunization program—Purpose.` Section caption only; the em dash is in the source. The page `<h1>` is `RCW  28A.210.060`.
- WA 2011: `K-12--IMMUNIZATION--EXEMPTION`. All-caps session law caption.
- WA 2019: `MEASLES, MUMPS, AND RUBELLA VACCINE--SCHOOLS AND DAY CARE CENTERS`. All-caps session law caption.
- WV 2015: `Senate Bill 286`. Says nothing about the subject. The page's summary line is "Relating to compulsory immunizations of students; exemptions". The page `<h1>` is `Bill Status - 2015 Regular Session`.
- WV 2011: `Court Declines Review of School Vaccine, Religious-Flier Cases`. Covers two unrelated cases.
- WV 2025: `Immunizations - Religious and Philosophical Exemptions`. Generic page title.
- WV 1985, WI 1987, VA 1981: multi-state MMWR titles. Old MMWR titles keep the `Epidemiologic Notes and Reports` prefix and double or triple hyphens as printed. On the page the title breaks across lines; stored with single spaces, as in the pilot.
- WI 1989: `Treating measles: the appropriateness of admission to a Wisconsin children's hospital.` Does not name Milwaukee or the outbreak. Trailing period is in the page `<h1>`.
- WY 2001: `In the Matter of the Exemption From Immunization Requested by Susan Le-PAGE, Parent of Lisa LePage, a minor. Susan LePage, Appellant (Petitioner), v. State of Wyoming, Department of Health, Appellee (Respondent).` Very long. "Le-PAGE" is a scanning artifact in the Harvard copy and was kept because it is what the page shows. The case is usually cited as LePage v. State, 2001 WY 26.
- WY 2025 (pertussis): `Whooping Cough Continues Wyoming Spread`. The department used this same headline for a March 2025 release at a different URL.

## Thin sources

- VA 1935 and WV 1934-06 are PubMed Central records of scanned American Journal of Public Health articles. The page shows the title, author, issue and, for Virginia, a "read at" footnote. No abstract. The blurbs say only that. The Virginia `date` is 1935, the year in the title; the article was published in February 1936.
- WY 2001 is a bare HTML page on static.case.law (Harvard Caselaw Access Project) with no site styling.

## Inferred or best-fit, not spelled out on the page

- `diseases` tags on law and court items are a best fit. The Vermont, Washington and Wyoming pages do not list diseases. The Vermont 1979 tags follow a 2016 Vermont Department of Health report (fetched) that says the 1979 law covered rubella, measles, diphtheria, tetanus, pertussis and polio.
- VA HB 1090 is tagged `hepatitis_a`. The summary page does not name a vaccine. The chapter text (fetched, `legp604.exe?201+ful+CHAP1223`) lists two doses of hepatitis A vaccine among the requirements. The blurb does not claim hepatitis A was newly added.
- WY 2001: the LePage case was about a hepatitis B vaccine waiver. It is tagged with the six school-vaccine diseases because the ruling is about the religious waiver in the school immunization statute.
- WV 2011 is tagged with six diseases for the same reason. The 4th Circuit opinion PDF was fetched (decided March 22, 2011) but its only heading is a caption several hundred characters long, so the Education Week story is used. `date` is 2011-03, `published` is 2011-11-14.
- WA 1979: the September 1, 1979 date comes from the effective-date note on the RCW page for the 1979 act (1979 ex.s. c 118). The section was amended in 1984 and 1990, so the purpose wording shown may not be the 1979 wording.
- WI 1989: the abstract says "a Wisconsin children's hospital" and "a metropolitan measles outbreak". The authors' address is Milwaukee, but the blurb does not name the city.
- WI 2025: the release prints August 2, 2025. The page metadata says August 1.
- WV 2025: the page is a live how-to page and could change. It does not mention the court cases over the order.

## Wanted, not verified (left out)

Vermont:

- 2012 whooping cough epidemic in Vermont. No health department page found; Internet Archive was down.
- Any Vermont polio epidemic of the 1930s to 1950s. Nothing fetched.
- The 2011 and 2018 single measles cases. Only mentioned in passing on later releases.
- The governor's signing of H.98 on a specific day in May 2015. A WAMC story turned up in search but was not fetched.

Virginia:

- 1950 polio epidemic in Wytheville. Only a one-line museum listing could be fetched. The 1951 Physical Therapy Review article and the Virginia Health Bulletin are not online in a fetchable form.
- When Virginia first required vaccines for school and when the religious exemption was added. The Code pages (§ 22.1-271.2 and § 32.1-46) were fetched, but their history notes only list chapter numbers (earliest 1968 and 1982).
- 2006 mumps outbreak at a Virginia university (J Med Virol 2009). PubMed blocked.
- 1969 measles epidemic in Norfolk and the 1950s polio reports in Virginia Medical Monthly. Not online.
- Virginia's 2019 statewide hepatitis A outbreak notice. Not found on the health department site.

Washington:

- The state health department's own July 2015 release on the Clallam County measles death. Not found; CNN is used.
- 2019 hepatitis A outbreak declaration. Not looked up after the list reached eight.

West Virginia:

- The text of Executive Order 7-25 on the governor's site. The health office page that describes it is used.
- Court rulings on the order: the July 24, 2025 Raleigh County preliminary injunction (a governor's office release was fetched), the November 2025 ruling, and the state Supreme Court's action. No court document fetched.
- When West Virginia first required school vaccination. The Code page lists bills back to 1987 only.
- "Polio years in West Virginia" and "Pertussis revisited: West Virginia, 1979-1984" (West Virginia Medical Journal). Not online.

Wisconsin:

- When the school immunization law and the personal conviction waiver were enacted. The statute page (252.04) was fetched, but its history starts at the 1993 renumbering.
- Final counts for the 1989 to 1990 Milwaukee measles outbreak ("Measles in Milwaukee", Wisconsin Medical Journal 1990). Not online.
- Later counts for the 2025 Oconto County outbreak. Seen only in search snippets from news sites.
- 1986 central Wisconsin pertussis outbreak (J Infect Dis 1988). Not fetchable.
- 1950s polio in Wisconsin (Wisconsin Medical Journal). Not online.

Wyoming:

- Anything before 1990. No Wyoming-titled MMWR report on these diseases exists in the 1982 to 2026 indexes, and PubMed has no older Wyoming titles.
- When Wyo. Stat. 21-4-309 was enacted. The statute text was fetched from wyoleg.gov, but it carries no history note.
- Jones v. State Department of Health (2001 WY 28), the companion case on medical waivers. Not fetched.
- "Assessment of vaccine exemptions among Wyoming school children, 2009 and 2011" (J Sch Nurs 2014). PubMed blocked.

## Fetched and verified but not used

- "Epidemiologic Notes and Reports Measles Outbreak -- Washington, 1989: Failure of Delayed Postexposure Prophylaxis with Vaccine" (MMWR, 1990-09-14)
- "Notes from the Field: Absence of Asymptomatic Mumps Virus Shedding Among Vaccinated College Students During a Mumps Outbreak — Washington, February–June 2017" (MMWR)
- "Notes from the Field: Measles in a Micronesian Community — King County, Washington, 2014" (MMWR)
- "Rubella in Seattle-King County Washington." (Am J Public Health, November 1977, PMC1653749; has an abstract)
- "Rubella screening and follow-up immunization in Vermont." (Am J Public Health, March 1979, PMC1619087; title only)
- "Comparison of an Active and Passive Surveillance System of Primary Care Providers for Hepatitis, Measles, Rubella, and Salmonellosis in Vermont" (Am J Public Health, July 1983, PMC1650894)
- "Health Department Confirms Case of Measles in Vermont" (second 2024 case, 2024-07-09)
- "Report Concerning the Mandatory Immunization of School Personnel" (Vermont Department of Health, 2016-01-15; says Act 40 of 1979 made immunizations mandatory for school entry)
- "Governor Patrick Morrisey Provides Guidance on Religious Exemptions from School Vaccine Mandates" (2025-05-09) and "Governor Patrick Morrisey Applauds Preliminary Injunction in Vaccine Religious Exemption Case" (2025-07-24), West Virginia Office of the Governor
- "§16-3-4. Compulsory immunization of school children; information disseminated; offenses; penalties." (West Virginia Code)
- "Whooping Cough Cases Increasing in Wyoming" (2025-02-11) and "Whooping Cough Continues Wyoming Spread" (2025-03-07), Wyoming Department of Health
- "Mandatory Vaccines and Waivers" (Wyoming Department of Health; describes religious and medical waivers under Wyo. Stat. 21-4-309)
- "Parental Vaccine Refusal in Wisconsin: A Case-Control Study" (WMJ, February 2009, PMC6359894)
- "Immunizations: Requirements" (Wisconsin DHS; 2024 rule changes cover meningococcal and chickenpox vaccines, which are out of scope)
