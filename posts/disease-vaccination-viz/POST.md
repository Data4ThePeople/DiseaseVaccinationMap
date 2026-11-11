---
title: "Infectious Disease and Vaccination, State by State: An Interactive Map, 1920 to 2025"
subtitle: A free, interactive map of reported cases of measles, whooping cough, hepatitis A, mumps and polio in every state and DC from 1920 to 2025, with kindergarten vaccination rates from the 2009-10 school year on.
slug: disease-vaccination-viz
date: 2026-11-12
updated: 2026-11-12
section: Visualization
author: Liam Aranda-Michel
author_url: https://www.data4thepeople.com/authors/liam-aranda-michel
hero: images/disease-vaccination-viz-hero-1680x1080.png
hero_alt:
meta_title:
description:
keywords:
schema_type: dataset
drop_cap: false
heading_spacer: 20px
caption_spacer: 20px
dividers: false
---

# Infectious Disease and Vaccination, State by State: An Interactive Map, 1920 to 2025

<iframe src="https://data4thepeople.github.io/DiseaseVaccinationMap/?v=20261111a#embed=1" width="100%" height="1440" loading="lazy" style="border:0" title="Infectious disease and vaccination, state by state: interactive map, 1920 to 2025"></iframe>

::: spacer 40px

::: blurb
**[Open the full visualization](https://data4thepeople.github.io/DiseaseVaccinationMap/)** **for the title and the full notes.**
:::

::: spacer

## Purpose

::: spacer 5px

Measles, whooping cough, hepatitis A, mumps and polio all have vaccines. This map shows how often each one was reported in every state and DC, year by year, from 1920 to 2025. From the 2009-10 school year on, it also shows the share of kindergartners in each state with the vaccine for that disease. The goal is to put more than 100 years of public health records in one place so you can see the numbers for yourself. It is not meant to argue for or against any policy.

You can pick one disease at a time, move through the years, and open any state to see its own history, its counties and its vaccination trend. The map uses each publisher's numbers as published. Where a source has no number for a state and year, the map leaves it blank. We do not fill in or estimate any missing value. The map is free to use and needs no sign-in. The underlying data and code are free to download on [GitHub](https://github.com/Data4ThePeople/DiseaseVaccinationMap).

::: blurb Read this first
These are reported cases, not all cases. Many people who got sick were never counted, and the rules for what to report changed many times over the century. The green, amber and red levels for case rates were set for this map and are not official levels; the same levels are used for every disease. Kindergarten vaccination measures one age group in one school year. It is not a measure of immunity in the whole population.
:::

## Using the visualization

::: spacer 5px

**1. Pick a disease.** The buttons above the map choose measles, whooping cough, hepatitis A, mumps or polio. The map shows one disease at a time.

**2. Pick a year.** Drag the slider, or click Play to move through the years. The map opens on 2010, the first year with state vaccination figures. Every year back to 1920 is on the slider.

**3. Hover over or tap a state.** A box shows that state's cases, its rate per 100,000 residents, its vaccination figures and where each number comes from.

**4. Click a state.** The state view shows its counties, its vaccination trend with cases under each year, and facts about the state that year: population, income, poverty, schooling, health insurance, jobs and which party held the governor's office and the legislature.

**5. Rank the states.** The list under the map ranks every state by vaccination or by case rate for the year shown. A table with every number is under it.

### How to read it

- **Each state is split corner to corner.** The key at the top of the map shows how.
- **The top-left half is vaccination.** It shows the share of kindergartners with the vaccine for the disease you picked: green for 95% or more, amber for 90% to under 95%, red for under 90%. The percentage is printed under the state's letters.
- **The bottom-right half is cases.** It shows reported cases per 100,000 residents that year: red for more than 1, amber for 0.1 to 1, green for under 0.1. The case count is printed in the top-right corner.
- **White means no figure.** A white half is a missing number, not a zero. Before the 2009-10 school year there are no state kindergarten figures, so the top-left half is white in every state.
- **Each gray figure is one reported case per 2,000 residents.** A faded figure marks a count that is incomplete or provisional.
- **Hepatitis A has no kindergarten figure.** CDC's state kindergarten figures do not include the hepatitis A vaccine, so for hepatitis A the top-left half stays white. Toddler figures are in the vaccination chart beside the map.

### What it shows right now

In 2025, states reported 2,026 measles cases, or 0.59 per 100,000 residents. That is up 629% from 278 cases in 2024. The 2025 count is provisional, and final counts are usually higher. Nine states were above 1 case per 100,000 residents in 2025, led by Utah (5.03), New Mexico (4.66) and North Dakota (4.50). In 2024, one state was above 1: Minnesota (1.19).

In the 2024-25 school year, 39 of the 49 states with a figure were below 95% of kindergartners with the measles vaccine (MMR), and 15 were below 90%. Idaho was lowest, at 78.5%. The national figure was 92.5%.

Measles reached its highest point on the map in 1941, when the states counted 894,134 cases.

## What this page is

::: spacer 5px

Every chart we publish should be something you can check, question and rebuild yourself. This page gives a short summary of how we built this one. The full documentation, with every source, definition, footnote and check, is in the public repository: [DATASETS.md](https://github.com/Data4ThePeople/DiseaseVaccinationMap/blob/main/DATASETS.md).

## The data sources

::: spacer 5px

**Yearly tables of notifiable diseases, U.S. Public Health Service.** Reported cases of measles, polio and whooping cough by state, 1920 to 1955 (whooping cough from 1922).

**Summary of Notifiable Diseases and annual tables, CDC.** Final yearly counts by state from 1956 to 2023: measles, whooping cough and paralytic polio from 1956, hepatitis A from 1966, mumps from 1968.

**National Notifiable Diseases Surveillance System weekly tables, CDC.** Counts for 2024 and 2025. The 2025 counts are provisional.

**Project Tycho, University of Pittsburgh.** Weekly reports for Alaska through 1958 and Hawaii through 1959, before they became states.

**SchoolVaxView, CDC.** The share of kindergartners in each state with the required doses of each vaccine, from the 2009-10 school year on.

**National Immunization Survey, CDC.** Toddler vaccination by state from 1995, shown in the vaccination charts. National surveys before 1995 come from the U.S. Immunization Survey and the National Health Interview Survey.

**County vaccination and measles cases, Johns Hopkins University.** County kindergarten MMR rates compiled from state reports (Dong and others, JAMA, 2025), and county measles cases from 2025 on from the Johns Hopkins measles tracking team.

**Population, income and state facts.** Census Bureau and Bureau of Economic Analysis. Party control from Klarner's State Partisan Balance Data through 2011 and Ballotpedia from 2012.

## How we built it, in short

::: spacer 5px

- **We use each publisher's numbers as published.** Nothing is filled in. When a source published no number, the map shows it as blank.
- **Cases.** Before 1993 the counts come from scanned government reports, read from the page. We kept a year only when its states add up to the table's printed regional totals and those add up to its printed U.S. total. From 1993 on they come from CDC's tables and files.
- **Rates.** Cases per 100,000 residents, using Census Bureau population for each state and year.
- **Vaccination.** Each state's kindergarten figure as reported to CDC. CDC marks some figures as lower bounds, and the map shows those as "at least."
- **Footnotes.** Where a source table says a count includes another disease, such as rubella in some measles counts, the state's hover box says so.
- **We check the numbers.** A script recomputes the numbers on the map from the source files and compares them. Separate checks, written from scratch without our code, pulled the data again and compared their results with the map.

## Updating

::: spacer 5px

We plan to add each new year when CDC publishes its counts and kindergarten figures.

## Honest notes and limitations

::: spacer 5px

These are the main limits. The full list is in [DATASETS.md](https://github.com/Data4ThePeople/DiseaseVaccinationMap/blob/main/DATASETS.md) and in the notes under the map.

- **Reported cases undercount real cases.** Reporting rules changed many times, and some states in the 1920s were not yet reporting every disease.
- **What was counted changed.** Polio counts all reported polio before 1956 and paralytic polio only from 1956. Hepatitis A before 1974 includes hepatitis of unspecified type, and CDC changed its definition in 2019.
- **The 2025 counts are provisional.** Final counts are usually higher.
- **States measure kindergarten vaccination in different ways.** Some count every school and some survey a sample, and some changed their method over these years. Compare a state with itself over time more than with another state.
- **Kindergarten figures start with the 2009-10 school year,** and no state reported one for 2010-11.
- **Some printed numbers were hard to read.** A few numbers in the scanned reports could not be read with certainty. The notes under the map list them.

## Reproduce it yourself

::: spacer 5px

The code, the data and the full method are at [github.com/Data4ThePeople/DiseaseVaccinationMap](https://github.com/Data4ThePeople/DiseaseVaccinationMap). Every step is in the scripts, in order. If you get a different number from us, tell us, and we will look.

::: divider

## Common questions

::: spacer 5px

### How many measles cases were there in the U.S. in 2025?

States reported 2,026 measles cases to CDC in 2025, or 0.59 per 100,000 residents. The count is provisional, and final counts are usually higher.

### Which states had the highest measles rates in 2025?

Utah (5.03 cases per 100,000 residents), New Mexico (4.66) and North Dakota (4.50).

### What share of kindergartners have the measles vaccine?

In the 2024-25 school year, 92.5% of kindergartners in the U.S. had the measles vaccine (MMR). In 39 of the 49 states with a figure, the share was below 95%.

### Which state has the lowest kindergarten measles vaccination rate?

In the 2024-25 school year, Idaho, at 78.5%.

### Why is 95% the line between green and amber?

95% is the national Healthy People 2030 target for kindergartners with the measles vaccine. The map uses the same level for the whooping cough and polio vaccines so the colors can be compared.

### Why is the top-left half of every state white before 2010?

CDC's state kindergarten figures start with the 2009-10 school year. Before that there is no state figure to show.

### Why is there no vaccination color for hepatitis A?

CDC's state kindergarten figures do not include the hepatitis A vaccine. Toddler figures for it are in the vaccination chart beside the map.

### Where does the data come from?

Case counts come from the U.S. Public Health Service's yearly tables (1920 to 1955), CDC's yearly and weekly tables (1956 to 2025) and Project Tycho. Vaccination figures come from CDC's SchoolVaxView and National Immunization Survey.

### Is the map free to use?

Yes. It is free to use and needs no sign-in.
