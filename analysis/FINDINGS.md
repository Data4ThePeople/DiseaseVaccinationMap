# Findings: vaccination declines, outbreaks, and the mumps record

Step 1 analysis, October 6, 2026. Every number below is recomputed by
`analysis/01_vaccination_and_outbreaks.py` (output in
`analysis/findings_numbers.txt`) unless it is quoted from a linked source.

**Read this first.** These are pairings in time and place, not causes. A drop
in school vaccination coverage followed by an outbreak in the same county is
worth reporting. It does not show that one produced the other: outbreaks also
depend on travel, on who is unvaccinated and how closely they live, and on
chance. Kindergarten coverage is reported by each state in its own way, and
most counties have figures only from 2017-18 or 2019-20 on.

---

## Part 1. Where coverage fell and disease followed

The pattern is clearest at the county level, and almost all of it is measles
in 2025 and 2026. At the state level the link is moderate for measles and weak
for whooping cough.

### 1. Mohave County, Arizona, and southwest Utah (strongest decline)

- **The data.** The share of Mohave County kindergartners with 2 MMR doses fell
  from 92.1% in 2017-18 to 76.0% in 2023-24, and was 78.4% in 2024-25. That is
  the largest drop among the outbreak counties. The Johns Hopkins tracker counts
  216 confirmed measles cases in Mohave County in 2025 and 69 more in 2026.
- **Next door.** Washington County, Utah, fell from 88.5% (2018-19) to 79.2%
  (2024-25). Utah reports cases by health district, not county; the tracker
  counts 155 cases in 2025 and 112 in 2026 in Utah's Southwest district.
- **Source at the time.** Utah DHHS, "2025–2026 Utah measles response" (updated
  September 29, 2026): 724 Utah residents diagnosed in this outbreak, 197 in 2025
  and 527 in 2026, "most" of them unvaccinated.
  https://epi.utah.gov/measles-response/ (a live page; the count will change).
- **Gap.** I could not fetch an Arizona or Mohave County source in this session
  (web search was used up). I have not confirmed whether the Arizona and Utah
  cases are one outbreak, so the page should not say they are.

### 2. Spartanburg County, South Carolina (largest outbreak)

- **The data.** Coverage fell from 95.1% (2019-20) to 90.0% (2024-25). South
  Carolina's county figures cover all grades, K through 12, not just
  kindergarten. The tracker counts 330 cases in Spartanburg County in 2025 and
  610 in 2026, the most of any county.
- **Sources at the time.**
  - SC Department of Public Health, "DPH Confirms Measles Outbreak in Upstate
    Region" (October 2, 2025). https://dph.sc.gov/news/dph-confirms-measles-outbreak-upstate-region
  - "DPH Announces End to Measles Outbreak in Upstate at 997 Cases" (April 27,
    2026): 997 cases from October 2025 through March 2026, 932 in unvaccinated
    people. https://dph.sc.gov/news/dph-announces-end-measles-outbreak-upstate-997-cases

### 3. Gaines County, Texas (low for years, not a sudden drop)

- **The data.** Coverage was already 80.4% in 2019-20, stayed near 81% to 83%,
  and was 77.3% in 2024-25, far below the Texas county median (94.5%). 414
  cases in 2025.
- **Sources at the time.**
  - CDC MMWR, "Notes from the Field: Initial Public Health Response to a Measles
    Outbreak in a Close-Knit West Texas Community": 207 cases from January 29 to
    February 28, 2025. https://www.cdc.gov/mmwr/volumes/75/wr/mm7523a2.htm
  - Texas DSHS, "Texas announces end of West Texas measles outbreak" (August 18,
    2025): 762 confirmed cases. https://www.dshs.texas.gov/news-alerts/texas-announces-end-west-texas-measles-outbreak
  - Background: Texas House Research Organization, "Conscientious Objection to
    Immunization" (2003), on the law that created the exemption.
    https://hro.house.texas.gov/interim/int78-1.pdf
- **How to tell it.** This is a story about a pocket that stayed low, not about a
  decline. It may be the more accurate frame for how outbreaks start.

### 4. Lancaster County, Pennsylvania, and Collier County, Florida (2026, outside the page)

- Lancaster fell from 95.5% (2017-18) to 88.5% (2024-25); 359 cases in 2026.
- Collier fell from 93.8% to 86.3% over the same years; 99 cases in 2026.
- Both outbreaks are in 2026, after the page's 2025 cutoff, and I have no
  contemporary source for either yet.
- Florida context, sourced: WUSF/AP, "Florida plans to become first state to
  eliminate all childhood vaccine mandates" (September 3, 2025).
  https://www.wusf.org/health-news-florida/2025-09-03/florida-to-eliminate-childhood-vaccine
  Collier's decline began years before that announcement.

### 5. Idaho (the clearest statewide decline)

- **The data.** Kindergartners with a non-medical exemption rose from 3.5%
  (2009-10) to 17.0% (2025-26), the highest of any state in the CDC file.
  Kindergarten MMR coverage fell from 87.0% to 75.2% over the same years.
- **Disease.** Whooping cough reached 59.9 cases per 100,000 in 2024, 417% above
  Idaho's 2015 to 2019 average. The U.S. rate also rose in 2024, but by 126%.
  Measles returned in 2023.
- **Sources at the time.**
  - Idaho DHW, "Measles is back in Idaho" (October 6, 2023): 10 cases in
    southwest Idaho, after two cases in the state in the prior 20 years.
    https://healthandwelfare.idaho.gov/dhw-voice/measles-back-idaho
  - Idaho Legislature, Senate Bill 1210, the Idaho Medical Freedom Act (signed
    April 4, 2025). https://legislature.idaho.gov/sessioninfo/2025/legislation/S1210/
- **Gap.** No Idaho source on the 2024 whooping cough rise yet.

### 6. The reverse sequence: outbreak, then a law, then coverage rose

Four states ended non-medical exemptions after outbreaks or rising exemption
rates, and their kindergarten MMR coverage went up afterward. The timing is
documented; whether the laws were the reason is not something this data shows.

| State | Law | MMR before | MMR after |
|---|---|---|---|
| California | SB 277, June 30, 2015, after the Disneyland outbreak | 92.3% (2013-14) | 97.3% (2016-17) |
| Maine | Public Law 2019, ch. 154, in effect September 2021 | 89.9% (2013-14) | 98.0% (2025-26) |
| New York | Signed June 13, 2019, during a year with 911 measles cases | all exemptions 1.3% (2018-19) | all exemptions 0.1% (2019-20) |
| Connecticut | Public Act 21-6, April 28, 2021 | 95.3% (2020-21) | 98.6% (2025-26) |

All four laws are in the verified milestone files with their URLs. Washington
removed the personal exemption for MMR in May 2019 after the Clark County
outbreak; state coverage rose to 94.4% the next school year and has since
fallen back to 90.6%.

### 7. What the state-level data does not show

- **Measles, 2025.** Across 46 states (Alaska, Delaware, the District of
  Columbia, Montana and West Virginia have no kindergarten figure in one of the
  two years and are left out), a larger drop in kindergarten MMR
  coverage from 2019-20 to 2024-25 goes with a higher 2025 measles rate, but
  only moderately (rank correlation -0.45; leaving out any one state moves it
  between -0.42 and -0.52). The measles counts are provisional, and 17 states
  changed how they count kindergartners between the two years. Wisconsin is the
  clearest case: it went from a sample of about 3% of students (92.8% in
  2019-20) to a count of nearly all of them (84.8% in 2024-25), so its drop is
  partly a change in method. Most states had few or no cases;
  the 2025 total (2,026, provisional) sits mostly in a handful of counties.
- **Whooping cough, 2024.** Cases rose from 7,063 in 2023 to 43,321 in 2024
  across the country. States with large DTaP drops (Idaho, Wisconsin) rose
  sharply, but so did states with almost no drop (Rhode Island +324%,
  Connecticut +339%, New York +241% against their own 2015 to 2019 averages).
  The rank correlation is weak (-0.24). I would not build a story on a
  state-level whooping cough link.
- **Earlier outbreaks.** Minnesota 2017, Clark County 2019 and New York 2019
  happened before most county coverage figures begin, so the data cannot show
  what coverage was beforehand.

### Data cautions found along the way

- **Wisconsin county figures** jump in 2022-23 (Iowa County from 91% to 59%,
  Lafayette County from 84% to 57% and back to 87%). This looks like a change in
  how Wisconsin reports, not a real drop. Wisconsin counties should be left out
  until it is checked.
- South Carolina and four other states report coverage for all grades, not
  kindergarten, so they are not directly comparable with the rest.

---

## Part 2. The mumps "wave" in the mid-20th century

**Short version: the wave on the map is mostly the start of the record, then
the vaccine era.**

1. **Mumps was common long before 1968.** Our state-level mumps record begins
   in 1968 because that is when state reports start in Project Tycho. Before
   then, about 110 large cities reported mumps from 1924 to 1932: between 24,585
   and 47,208 cases a year in those cities alone. City reporting of mumps then
   stops in the data. CDC counted 185,691 U.S. cases in 1967 (source below). So
   when mumps appears on the map in 1968 at its highest level, that is the first
   year it was counted state by state, not the start of an epidemic.
2. **The decline lines up with the vaccine.** The mumps vaccine was licensed in
   1967 and recommended for routine use in 1977. CDC reported a 98% decline from
   185,691 cases in 1967 to 2,982 in 1985. CDC's final tables give 152,209 for
   1968, and our state sum now matches it, with New York counted as New York
   City only that year. Our 1985 sum is 2,982, the same as CDC's.
3. **The 1987 resurgence is the best mumps story for this project.** CDC
   reported 12,848 cases in 1987. The rise was steepest among 10 to 14 year olds
   (an increase of almost 600%) and 15 to 19 year olds (more than 700%). CDC said
   the shift was "attributable to the relatively underimmunized cohort of
   children born between 1967 and 1977", children born after the vaccine existed
   but before it was routinely given. CDC also compared states: in 1987, the 14
   states without a school requirement for mumps vaccine had 11.5 cases per
   100,000, against 1.1 in the 15 areas that required it from kindergarten
   through 12th grade. In our data Illinois (2,737 cases, 24.0 per 100,000),
   Wisconsin (36.3 per 100,000) and Tennessee (25.2) led that year. Campus
   outbreaks in Illinois, Wisconsin and South Dakota are in the milestone files.
   - CDC MMWR, "Recommendations of the Immunization Practices Advisory
     Committee Mumps Prevention" (June 9, 1989).
     https://www.cdc.gov/mmwr/preview/mmwrhtml/00001404.htm
   - CDC MMWR, "Mumps Outbreaks on University Campuses -- Illinois, Wisconsin,
     South Dakota" (1987). https://www.cdc.gov/mmwr/preview/mmwrhtml/00000944.htm
   - This is the one historical case where CDC itself tied a gap in vaccination
     to a rise in disease at the time, which makes it a cleaner fit for your
     question than any of the recent measles pairings.
4. **Later mumps outbreaks are a different story.** 2006 (6,584 cases, starting
   in Iowa) and 2016 to 2017 (6,369 and 6,109; Arkansas, Hawaii, Washington,
   several universities) happened largely among people who had been vaccinated,
   and led CDC's advisory committee to recommend a third dose during outbreaks
   in January 2018. These are about protection fading in close-contact
   settings, not about falling coverage, and should not be framed as
   vaccine-decline stories. Sources are in the milestone files (Iowa 2006,
   Arkansas 2016, Hawaii 2018, the 2018 third-dose recommendation).

**Fixed: the mumps undercount.** The page's 1968 to 1992 mumps figures were
Project Tycho's provisional totals, which undercounted (1986 showed 2,676
against CDC's 7,790). They now come from CDC's final annual tables, read from
the scanned reports, for every year from 1968 to 1992. Each year passes the same
test as before: every state present, states adding to the printed regional
rows, regions adding to the printed U.S. total. 91 state cells were read from
the page image where the scan's text layer was damaged; they are listed in
`data/raw/bridge/checks_image_cells.csv`, and two I checked against the page
(Hawaii 1986, New England 1980) match. Two 1971 cells are misprinted on the page
("-99" for DC, "8.784" for Ohio); Eric accepted the readings 99 and 8,784 on
October 6, 2026, and their flags say so. For 1968 to 1973, when upstate New
York did not report mumps, New York shows New York City's count, labeled as
City only. The page's national sums now equal CDC's printed totals in every
year from 1968 to 1992, including 2,982 for 1985, 7,790 for 1986 and 12,848
for 1987.

---

## Suggested next steps

1. Pick the lead story. In my view the strongest are the 1987 mumps resurgence
   (CDC tied it to vaccination gaps at the time) and Mohave County / southwest
   Utah (largest county decline, large outbreak).
2. Find contemporary sources for the gaps: Mohave County 2025, Idaho whooping
   cough 2024, Lancaster and Collier 2026. This needs more web searches than
   this session has left.
4. Check the Wisconsin county reporting change before using those counties.
