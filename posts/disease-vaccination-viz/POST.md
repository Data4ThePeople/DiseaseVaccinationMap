---
title: "Infectious Disease and Vaccination, State by State: An Interactive Map, 1920 to 2026"
subtitle: A free, interactive map of reported cases of measles, whooping cough, hepatitis A, mumps and polio in every state and DC, from as early as 1920 through 2026, with kindergarten vaccination rates from the 2009-10 school year on.
slug: disease-vaccination-viz
date: 2026-11-12
updated: 2026-11-12
section: Visualization
author: Liam Aranda-Michel
author_url: https://www.data4thepeople.com/authors/liam-aranda-michel
hero: images/disease-vaccination-viz-hero-1680x1080.png
hero_alt: Tile map of the United States on a dark background, one square per state, each split corner to corner. Top-left half: share of kindergartners with the measles vaccine, 2025-26 (green 95% or more, amber 90 to 94.9%, red under 90%). Bottom-right half: 2026 measles cases per 100,000 residents through November 7 (red over 1, amber 0.1 to 1, green under 0.1). Text: Measles and vaccination, state by state. 5,073 cases. 39 of 49 states below 95%. Data 4 The People.
meta_title: "Measles Cases and Vaccination by State: Map, 1920-2026"
description: "Free interactive map of measles, whooping cough, mumps, hepatitis A and polio cases in every state, 1920 to 2026, with kindergarten vaccination rates."
keywords: measles cases by state 2026, measles map, measles cases by year, kindergarten vaccination rates by state, MMR vaccination rate by state, measles outbreak 2026, whooping cough cases by state, history of measles in the United States
schema_type: dataset
dataset_name: Reported cases of measles, whooping cough, hepatitis A, mumps and polio, and kindergarten vaccination coverage, U.S. states and DC, 1920 to 2026
dataset_description: "Reported cases by state and year from the U.S. Public Health Service yearly tables (1920 to 1955), CDC's annual notifiable disease tables (1956 to 2023) and CDC's weekly NNDSS tables (2024 to 2026, with 2026 through November 7 and provisional), with Project Tycho for Alaska and Hawaii before statehood; rates per 100,000 residents from Census Bureau population; kindergarten vaccination coverage from CDC SchoolVaxView (2009-10 school year on); toddler coverage from the National Immunization Survey; county MMR coverage and county measles cases from Johns Hopkins University. Values not published by the source are left blank."
temporal: 1920/2026
spatial: United States
measured: Reported cases|count; Cases per 100,000 residents|rate; Kindergartners with the required vaccine doses|percent; Toddler vaccination coverage|percent; County kindergarten MMR coverage|percent; County measles cases|count
sources: https://www.cdc.gov/nndss/|https://data.cdc.gov/NNDSS/x9gk-5huc|https://www.cdc.gov/schoolvaxview/|https://www.cdc.gov/nis/|https://www.tycho.pitt.edu/|https://github.com/enshengdong/MMR_data|https://github.com/CSSEGISandData/measles_data
distribution: text/html|https://data4thepeople.github.io/DiseaseVaccinationMap/;text/csv|https://github.com/Data4ThePeople/DiseaseVaccinationMap/tree/main/data
measurement_technique: Published state counts joined by disease, state and year with no imputation. Counts before 1993 were read from scanned government tables and kept only when the states add to the printed regional and U.S. totals. Rates are cases per 100,000 residents from Census Bureau population; 2026 rates use 2025 population.
credit: Data 4 The People, from CDC, the U.S. Public Health Service, Project Tycho, the Census Bureau and Johns Hopkins University
license: https://www.data4thepeople.com/terms-of-use
app_url: https://data4thepeople.github.io/DiseaseVaccinationMap/
app_name: "Infectious Disease and Vaccination, State by State: interactive map, 1920 to 2026"
app_category: EducationalApplication
app_description: Free interactive map of reported cases of measles, whooping cough, hepatitis A, mumps and polio in every state and DC from as early as 1920 through 2026, with kindergarten vaccination rates from the 2009-10 school year on.
app_features: All 50 states and DC, 1920 to 2026|One disease at a time: measles, whooping cough, hepatitis A, mumps or polio|Each state split into vaccination and case rate|Play through the years|Cases each year for the U.S. and each state|State pages with county vaccination and 2025-2026 county measles cases|Ranking and table of every state|Headlines from public health records on the timeline
drop_cap: false
heading_spacer: 20px
caption_spacer: 20px
dividers: false
---

# Infectious Disease and Vaccination, State by State: An Interactive Map, 1920 to 2026

<iframe src="https://data4thepeople.github.io/DiseaseVaccinationMap/?v=20261111c#embed=1" width="100%" height="1440" loading="lazy" style="border:0" title="Infectious disease and vaccination, state by state: interactive map, 1920 to 2026"></iframe>

::: spacer 40px

::: blurb
**[Open the full visualization](https://data4thepeople.github.io/DiseaseVaccinationMap/)** **for the title and the full notes.**
:::

::: spacer

## Purpose

::: spacer 5px

What are we doing as a society?

I mean really, pause and think about it. Our attention spans are commodified and mined by algorithms that boil us down into profit-generating, zombified consumers who would rather scroll an Instagram feed than engage with other humans. Misinformation and disinformation gum up every social media platform (or wherever you source those "articles" you tell people you read), making it hard to tell how much of what we see is real and how much is engineered. One casualty of all this is our willingness to vaccinate our children.

In 1998, Andrew Wakefield published a paper that suggested a link between the MMR vaccine and developmental regression in children. The journal retracted it in 2010, and the same year he was struck off the U.K. medical register. However, his claim outlived the paper. Self-styled truth-tellers have since flooded the internet with every wild reason you can think of to keep a child from modern, evidence-based medicine (essential oils, anyone?).

Over the same years, diseases we had all but eliminated have returned. The share of U.S. kindergartners with the measles vaccine fell from 95.2% in the 2019-20 school year to 92.4% in 2025-26. In 2026, through November 7, states reported 5,073 measles cases, the most in any year since 1991. In 2022, New York reported a case of paralytic polio.

Here, we introduce an open-source tool to track this. The map shows reported cases of measles, whooping cough, hepatitis A, mumps and polio in every state and DC, from as early as 1920 through 2026, and from the 2009-10 school year on, the share of kindergartners with each vaccine. You can pick one disease at a time, move through the years, and open any state to see its counties and its own history. The map uses each publisher's numbers as published and leaves a blank where a source has no number; we do not fill in or estimate any missing value. It is free to use and needs no sign-in, and the data and code are on [GitHub](https://github.com/Data4ThePeople/DiseaseVaccinationMap).

::: blurb Read this first
These are reported cases, not all cases. Many people who got sick were never counted, and the rules for what to report changed many times over the century. The green, amber and red levels for case rates were set for this map and are not official levels; the same levels are used for every disease. Kindergarten vaccination measures one age group in one school year. It is not a measure of immunity in the whole population. 2026 is not over: it runs through November 7, its counts are provisional, and its rates use 2025 population.
:::

## Using the visualization

::: spacer 5px

**1. Pick a disease.** The buttons above the map choose measles, whooping cough, hepatitis A, mumps or polio. The map shows one disease at a time.

**2. Pick a year.** Drag the slider, or click Play to move through the years. The map opens on 2010, the first year with state vaccination figures. Every year from 1920 to 2026 is on the slider.

**3. Hover over or tap a state.** A box shows that state's cases, its rate per 100,000 residents, its vaccination figures and where each number comes from.

**4. Click a state.** The state view shows its counties, a chart of its cases each year, its vaccination trend, and facts about the state that year: population, income, poverty, schooling, health insurance, jobs and which party held the governor's office and the legislature.

**5. Rank the states.** The list under the map ranks every state by vaccination or by case rate for the year shown. A table with every number is under it.

### How to read it

- **Each state is split corner to corner.** The key at the top of the map shows how.
- **The top-left half is vaccination.** It shows the share of kindergartners with the vaccine for the disease you picked: green for 95% or more, amber for 90% to under 95%, red for under 90%. The percentage is printed under the state's letters.
- **The bottom-right half is cases.** It shows reported cases per 100,000 residents that year: red for more than 1, amber for 0.1 to 1, green for under 0.1. The case count is printed in the top-right corner.
- **White means no figure.** A white half is a missing number, not a zero. Before the 2009-10 school year there are no state kindergarten figures, so the top-left half is white in every state.
- **Each gray figure is one reported case per 2,000 residents.** A faded figure marks a count that is incomplete or provisional.
- **Hepatitis A has no kindergarten figure.** CDC's state kindergarten figures do not include the hepatitis A vaccine, so for hepatitis A the top-left half stays white. Toddler figures are in the vaccination chart beside the map.
- **The bar chart beside the map shows reported cases each year** for the disease you picked, for the U.S. or, on a state's page, for that state. It uses a log scale, so the large counts of the 1940s and the small counts of recent years both show. Click a bar to move to that year.

### What it shows right now

In 2026, through November 7, states reported 5,073 measles cases, or 1.48 per 100,000 residents. That is 150% more than in all of 2025 (2,026 cases) and the most in any year since 1991. The 2026 count is provisional. Fourteen states were above 1 case per 100,000 residents, led by Utah (15.03), South Carolina (12.32) and Pennsylvania (11.30).

In the 2025-26 school year, in 39 of the 49 states with a figure, fewer than 95% of kindergartners had the measles vaccine (MMR), and in 18, fewer than 90%. Idaho was lowest, at 75.2%. The national figure was 92.4%, down from 95.2% in the 2019-20 school year.

Measles reached its highest point on the map in 1941, when the states counted 894,134 cases.

## What this page is

::: spacer 5px

Every chart we publish should be something you can check, question and rebuild yourself. This page gives a short summary of how we built this one. The full documentation, with every source, definition, footnote and check, is in the public repository: [DATASETS.md](https://github.com/Data4ThePeople/DiseaseVaccinationMap/blob/main/DATASETS.md).

## The data sources

::: spacer 5px

**Yearly tables of notifiable diseases, U.S. Public Health Service.** Reported cases of measles, polio and whooping cough by state, 1920 to 1955 (whooping cough from 1922).

**Summary of Notifiable Diseases and annual tables, CDC.** Yearly counts by state from 1956 to 2023: measles, whooping cough and paralytic polio from 1956, hepatitis A from 1966, mumps from 1968. Paralytic polio counts are as first printed; CDC later revised some yearly totals.

**National Notifiable Diseases Surveillance System weekly tables, CDC.** Counts for 2024 (as counted a year later), 2025 and 2026. The 2025 and 2026 counts are provisional, and 2026 runs through November 7.

**Project Tycho, University of Pittsburgh.** Weekly reports for Alaska through 1958 and Hawaii through 1959, before they became states.

**SchoolVaxView, CDC.** The share of kindergartners in each state with the required doses of each vaccine, from the 2009-10 school year on.

**National Immunization Survey, CDC.** Toddler vaccination by state from 1995, shown in the vaccination charts. National surveys before 1995 come from the U.S. Immunization Survey and the National Health Interview Survey.

**County vaccination and measles cases, Johns Hopkins University.** County kindergarten MMR rates compiled from state reports (Dong and others, JAMA, 2025), and county measles cases from 2025 on from the Johns Hopkins measles tracking team.

**Population, income and state facts.** Census Bureau and Bureau of Economic Analysis. Party control from Klarner's State Partisan Balance Data through 2011 and Ballotpedia from 2012.

## How we built it, in short

::: spacer 5px

- **We use each publisher's numbers as published.** Nothing is filled in. When a source published no number, the map shows it as blank.
- **Cases.** Before 1993 the counts come from scanned government reports, read from the page, except Alaska and Hawaii before statehood, which come from Project Tycho's copies of the weekly reports. We kept a year only when its states add up to the table's printed regional totals and those add up to its printed U.S. total. From 1993 on they come from CDC's tables and files.
- **Rates.** Cases per 100,000 residents, using Census Bureau population for each state and year. There is no 2026 estimate yet, so 2026 rates use 2025 population.
- **Vaccination.** Each state's kindergarten figure as reported to CDC. CDC marks some figures as lower bounds, and the map shows those as "at least."
- **Footnotes.** Where a source table says a count includes another disease, such as rubella in some measles counts, the state's hover box says so.
- **We check the numbers.** A script recomputes the numbers on the map from the source files and compares them. Separate checks, written from scratch without our code, pulled the data again and compared their results with the map. Neither check found a number that differed from the map.

## Updating

::: spacer 5px

We plan to update the map every week. CDC posts new case counts each week, and the Johns Hopkins measles tracker updates its county counts every Friday. Each week we plan to pull both, rebuild the map, and check every number against the source files before the update goes live. Until a year is over, its counts are provisional and will keep changing; the date each count runs through is shown on the map.

Kindergarten vaccination figures come out once a year. We will add each new school year when CDC publishes it.

## Honest notes and limitations

::: spacer 5px

These are the main limits. The full list is in [DATASETS.md](https://github.com/Data4ThePeople/DiseaseVaccinationMap/blob/main/DATASETS.md) and under "Show notes and disclaimers" at the bottom of the map.

- **Reported cases undercount real cases.** Reporting rules changed many times, and some states in the 1920s were not yet reporting every disease.
- **What was counted changed.** Polio counts all reported polio before 1956 and paralytic polio only from 1956. Hepatitis A before 1974 includes hepatitis of unspecified type, and CDC changed its definition in 2019.
- **The 2025 and 2026 counts are provisional.** Final counts are usually higher. 2026 is not over, so its rates run lower than a full year would, and a state near a line between two colors may show one step lower.
- **States measure kindergarten vaccination in different ways.** Some count every school and some survey a sample, and some changed their method over these years. Compare a state with itself over time more than with another state.
- **County figures have their own limits.** County vaccination figures were compiled by Johns Hopkins from state reports, and some states count grades other than kindergarten. They run through the 2024-25 school year, so the 2026 county map shows the latest year available. County measles counts start in 2025.
- **Kindergarten figures start with the 2009-10 school year,** and no state reported one for 2010-11.
- **Some printed numbers were hard to read.** A few numbers in the scanned reports could not be read with certainty. They are listed under "Show notes and disclaimers" at the bottom of the map.

## Reproduce it yourself

::: spacer 5px

The code, the data and the full method are at [github.com/Data4ThePeople/DiseaseVaccinationMap](https://github.com/Data4ThePeople/DiseaseVaccinationMap). Every step is in the scripts, in order. If you get a different number from us, tell us, and we will look.

::: divider

## Common questions

::: spacer 5px

### How many measles cases have there been in the U.S. in 2026?

States reported 5,073 measles cases to CDC in 2026 through November 7, or 1.48 per 100,000 residents. That is the most in any year since 1991. The count is provisional, and final counts are usually higher.

### Which states have the highest measles rates in 2026?

Through November 7, Utah (15.03 cases per 100,000 residents), South Carolina (12.32) and Pennsylvania (11.30).

### What share of kindergartners have the measles vaccine?

In the 2025-26 school year, 92.4% of kindergartners in the U.S. had the measles vaccine (MMR). In 39 of the 49 states with a figure, the share was below 95%.

### Which state has the lowest kindergarten measles vaccination rate?

In the 2025-26 school year, Idaho, at 75.2%.

### Why is 95% the line between green and amber?

95% is the national Healthy People 2030 target for kindergartners with the measles vaccine. The map uses the same level for the whooping cough and polio vaccines so the colors can be compared.

### Why is the top-left half of every state white before 2010?

CDC's state kindergarten figures start with the 2009-10 school year. Before that there is no state figure to show.

### Why is there no vaccination color for hepatitis A?

CDC's state kindergarten figures do not include the hepatitis A vaccine. Toddler figures for it are in the vaccination chart beside the map.

### Where does the data come from?

Case counts come from the U.S. Public Health Service's yearly tables (1920 to 1955), CDC's yearly and weekly tables (1956 to 2026) and Project Tycho. Vaccination figures come from CDC's SchoolVaxView and National Immunization Survey.

### Is the map free to use?

Yes. It is free to use and needs no sign-in.
