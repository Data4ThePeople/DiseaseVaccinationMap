# Annual state case counts from CDC annual tables: notes

Built by `scripts/02b_fetch_annual_summaries.py`. Every row in
`annual_state_cases.csv` comes from a file saved in `src/`; the row names the
file, the URL it was downloaded from, and the table, page and printed column
header it was read from. No number was typed in by hand and nothing was taken
from memory.

Rebuild without downloading: `.venv/bin/python scripts/02b_fetch_annual_summaries.py --no-download`

## Files in this folder

| File | What it is |
|---|---|
| `annual_state_cases.csv` | The deliverable. 50 states + DC, one row per year, state and disease. |
| `annual_area_cases_all.csv` | Every area row as printed: US total, the nine divisions, New York City and the rest of New York separately, territories. Includes the cell text exactly as printed. |
| `checks_state_sum_vs_us.csv` | Sum of the 51 areas against the table's own United States row, per disease and year. |
| `checks_html_vs_pdf.csv` | 2007 to 2015: the HTML edition of each issue parsed separately and compared cell by cell with the PDF. |
| `checks_owid_measles.csv` | Measles compared with the Our World in Data transcription. Cross-check only, never a source. |
| `checks_scans_1980_1992.csv` | Which scanned years passed the strict test and why the others failed. |
| `checks_column_map.csv` | The printed column header and US total cell that was read for each disease and year. |
| `checks_marks.csv` | Mark definitions as printed in each source, with the page. |
| `checks_finality.csv` | The sentence in each source that says the data are final and gives the cutoff date. |

## Coverage

| Years | Diseases | Source |
|---|---|---|
| 1984, 1988, 1990, 1991, 1992 | measles (total, indigenous, imported) | scanned annual summaries, CDC Stacks |
| 1985, 1990, 1991, 1992 | pertussis | scanned annual summaries, CDC Stacks |
| 1993 to 2015 | all seven diseases | MMWR Summary of Notifiable Diseases, Table 2, issue PDF |
| 2016 to 2023 | all seven diseases | NNDSS Annual Tables, Table 2 parts |

Not obtained: measles for 1980 to 1983, 1985 to 1987 and 1989; pertussis for
1980 to 1984 and 1986 to 1989. See "Scanned years" below. Mumps, rubella,
hepatitis A, diphtheria and polio were not attempted before 1993.

## Results of the checks

- State sum against the printed United States row: 298 disease-years checked,
  all equal. 25 of those are trivial (diseases with no US cases, taken from a
  footnote, see below), 273 are real sums.
- HTML against PDF, 2007 to 2015: 66 disease-years, no cell differs.
- Our World in Data, measles: 766 state-years compared (1984 to 2015), 763 the
  same, 3 different. In all three the number here is what the CDC table prints
  and it is consistent with the printed US total:
  - 1994 New York: 43 here (rest of state 28, New York City 15), OWID 87.
  - 1997 New York: 16 here (rest of state 5, New York City 11), OWID 32.
  - 2010 Nevada: 1 here (imported 1, indigenous dash), OWID 0.

## Rules used for every source

- **New York.** Every table prints New York City and the rest of New York as
  two rows. The `New York` row here is the sum of the two. Both parts are kept
  in `annual_area_cases_all.csv`.
- **Measles total.** From 2008 the tables print a Total column. Before 2008
  they print only Indigenous and Imported, so `measles` is computed as the
  sum of the two and flagged `sum` (or `sum-` when both parts were dashes).
  `measles_indigenous` and `measles_imported` are kept in every year.
- **`flag` column.**
  - empty: a plain number.
  - `-`: the cell is a dash. Every source defines the dash as "No reported
    cases", so `cases` is 0 and the flag is kept so the dash can be told
    apart from a printed 0.
  - `N`, `NN`: not notifiable / not reportable in that state. `cases` blank.
  - `U`, `NA`: unavailable / data not available. `cases` blank.
  - `blank`: nothing is printed in the cell. `cases` blank.
  - `fn0`: the disease has no column in Table 2 that year because the issue
    states that no cases were reported in the United States. `cases` is 0 for
    every state and `source_table` quotes the sentence.
  - `sum`, `sum-`: computed total, see above.
  - `*`, `†` and similar after a number: the footnote symbol printed on the
    cell.
- **Cells left blank (31 in all).** NN: mumps in New Mexico 1993 to 1999 and
  Oregon 1993 to 2001, rubella in Mississippi 1994 to 1998, paralytic polio in
  Wisconsin 1997 and 1998. N: mumps in Oregon 2003 and 2005, measles total in
  DC 2011. U: hepatitis A in DC 2007, 2008, 2014, 2015. blank: rubella in
  Tennessee 2015.

## Mark definitions by period (as printed, pages in `checks_marks.csv`)

| Years | Marks |
|---|---|
| 1984 to 2001 | `-` No reported cases; `NA` Data not available; `NN` Report of disease is not required in that jurisdiction (not notifiable). Printed once per issue under "Explanation of symbols used in tables". |
| 2002 to 2007 | `-` No reported cases; `N` Not notifiable; `U` Unavailable. Printed under each Table 2 page and in the front list. |
| 2008 to 2015 | `-` No reported cases; `N` Not reportable; `U` Unavailable (2014 and 2015 front list: "Data not available"). |
| 2016 | `-` No reported cases; `N` Not Reportable; `U` Unavailable. |
| 2017 to 2023 | `-` No reported cases, the reporting jurisdiction did not submit any cases to CDC; `N` Not reportable by law, statute, or regulation in the reporting jurisdiction; `U` Unavailable. |

In the 1985 and 1988 scans the legend line "No reported cases ....." is
present but the symbol after the dotted leader is not legible in the OCR text
layer. It is read as the dash, as in the 1984 and 1990 to 1992 legends where
the symbol is legible. This is an inference.

## Definition changes noticed

- **Measles "imported".** Through 1994 the footnote says imported "includes
  both out-of-state and international importations" (1994: 142 out-of-state
  and 75 international). From 1995 it says imported cases "include only those
  imported from other countries". The indigenous and imported columns are not
  comparable across 1994/1995. The total is not affected. From 2019 the
  footnote reads: imported if acquired outside the United States, indigenous
  if acquired within the United States or if it is not known where.
- **Measles columns.** Indigenous and Imported only, 1984 to 2007. Total,
  Indigenous, Imported from 2008. Total, Imported, Indigenous from 2019.
- **Hepatitis A column header.** "Hepatitis A" 1993 and 1994; "Hepatitis: A"
  1995 to 2000; "Hepatitis, acute: A" 2001; "Hepatitis, acute viral: A" 2002
  to 2004; "Hepatitis, viral, acute: A" 2005 to 2013; "Hepatitis A, acute"
  2014 and 2015; "Hepatitis, A, acute" 2016 to 2019; "Hepatitis, Viral
  Disease, Hepatitis A" 2020 to 2022; "Hepatitis A, acute" 2023. No table in
  any year splits hepatitis A into confirmed and probable. The 2019 table
  notes say a revised case definition for acute hepatitis A took effect in
  January 2019.
- **Diphtheria and paralytic polio.** Printed as Table 2 columns only in years
  with at least one US case. In the other years the issue says no cases were
  reported and the rows here are `fn0`. From 2016 both have a column every
  year.
- **Residence, 2019 onward.** The US row is "U.S. Residents, excluding U.S.
  Territories". From 2020 the tables add "Non-U.S. Residents" and a "Total"
  row that includes territories and non-residents. The check uses the US
  residents row, not "Total".
- **1993 paralytic polio.** The US cell is "3†": ten suspected cases, three
  confirmed as of August 12, 1994, count subject to change. 1994 is "-†":
  two suspected cases pending review.

## Year by year

Cutoff is the date in the source's own statement (`checks_finality.csv`).

### Scanned annual summaries (CDC Stacks, PDF with OCR text layer)

Each issue says the data are "compiled in final form in this summary". No
cutoff date is stated.

| Year | Stacks record | File | Page | Used |
|---|---|---|---|---|
| 1984 | https://stacks.cdc.gov/view/cdc/35267 | stacks_35267_DS1.pdf | 16 | measles |
| 1985 | https://stacks.cdc.gov/view/cdc/35429 | stacks_35429_DS1.pdf | 12 | pertussis |
| 1988 | https://stacks.cdc.gov/view/cdc/35958 | stacks_35958_DS1.pdf | 15 | measles |
| 1990 | https://stacks.cdc.gov/view/cdc/35905 | stacks_35905_DS1.pdf | 19 | measles, pertussis |
| 1991 | https://stacks.cdc.gov/view/cdc/36010 | stacks_36010_DS1.pdf | 21 | measles, pertussis |
| 1992 | https://stacks.cdc.gov/view/cdc/36063 | stacks_36063_DS1.pdf | 23 | measles, pertussis |

The Stacks catalog titles for records 35267 and 35429 give the wrong year
("Annual Summary 1985", "for 1986"). The documents themselves are the 1984 and
1985 summaries (cover and table titles).

### MMWR Summary of Notifiable Diseases, Table 2 (issue PDF, text layer)

URL pattern `https://www.cdc.gov/mmwr/PDF/wk/<file>` through 2013,
`https://www.cdc.gov/mmwr/volumes/<vol>/wr/pdfs/<file>` for 2014 and 2015.

| Year | File | PDF pages read | Final totals as of |
|---|---|---|---|
| 1993 | mm4253.pdf | 24 to 27 | "compiled in final form", no date |
| 1994 | mm4353.pdf | 23 to 26 | July 7, 1995 |
| 1995 | mm4453.pdf | 17 to 19 | July 26, 1996 |
| 1996 | mm4553.pdf | 18 to 21 | July 25, 1997 |
| 1997 | mm4654.pdf | 22 to 25 | July 25, 1998 |
| 1998 | mm4753.pdf | 25, 27 to 30 | August 13, 1999 |
| 1999 | mm4853.pdf | 23, 25 to 27 | August 15, 2000 |
| 2000 | mm4953.pdf | 29, 31 to 33 | August 24, 2001 |
| 2001 | mm5053.pdf | 31, 33 to 35 | June 21, 2002 |
| 2002 | mm5153.pdf | 21, 24 to 26 | June 30, 2003 |
| 2003 | mm5254.pdf | 21, 24 to 26 | June 30, 2004 |
| 2004 | mm5353.pdf | 26 to 28 | December 2, 2005 |
| 2005 | mm5453.pdf | 27 to 30 | June 30, 2006 |
| 2006 | mm5553.pdf | 29 to 32 | June 30, 2007 |
| 2007 | mm5653.pdf | 31 to 34 | June 30, 2008 |
| 2008 | mm5754.pdf | 28 to 31 | June 30, 2009 |
| 2009 | mm5853.pdf | 30 to 33 | June 30, 2010 |
| 2010 | mm5953.pdf | 33 to 37 | June 30, 2011 |
| 2011 | mm6053.pdf | 35 to 39 | June 30, 2012 |
| 2012 | mm6153.pdf | 32, 34, 36 to 38 | June 30, 2013 |
| 2013 | mm6253.pdf | 39, 41 to 43 | June 30, 2014 |
| 2014 | mm6354.pdf | 40, 44, 48, 50, 52 (each table runs onto the next page) | June 30, 2015 |
| 2015 | mm6453.pdf | 49, 53, 55, 57 (each table runs onto the next page) | June 30, 2016 |

All say "final totals ... unless otherwise noted". 1995 has no diphtheria
column: the issue says there were no reported cases of anthrax, diphtheria and
yellow fever in the United States during 1995. The HTML editions used for the
2007 to 2015 comparison are the `mm....a1.htm` files in `src/`. Before 2007
the HTML editions show Table 2 as images, so only the PDF could be read.

### NNDSS Annual Tables, Table 2 parts

| Year | Source | Table parts | Stated status |
|---|---|---|---|
| 2016 | Stacks text files, records 49381, 49383, 49385 to 49388 | 2e, 2g, 2i, 2j, 2k, 2l | data reported through June 30, 2017; tables accurate as of October 17, 2017; "finalized 2016 data" |
| 2017 | Internet Archive captures of the CDC WONDER text files, see below | 2e, 2g, 2i, 2j, 2k, 2l | "finalized 2017 data"; no date |
| 2018 | Stacks text files, records 82388, 82390, 82392 to 82395 | 2e, 2g, 2i, 2j, 2k, 2l | "finalized 2018 data"; no date |
| 2019 | Stacks text files, records 106480, 106482, 106485 to 106488 | 2f, 2h, 2k, 2l, 2m, 2n | "finalized 2019 data"; no date |
| 2020 | Stacks text files, records 175634, 175636, 175639 to 175642 | 2f, 2h, 2k, 2l, 2m, 2n | "finalized 2020 data"; no date |
| 2021 | Stacks text files, records 175661, 175663, 175666 to 175669 | 2f, 2h, 2k, 2l, 2m, 2n | "finalized 2021 data"; no date |
| 2022 | Stacks text files, records 175688, 175690, 175693 to 175696 | 2f, 2h, 2k, 2l, 2m, 2n | "finalized 2022 data"; no date |
| 2023 | Stacks PDFs, records 251104, 251106, 251109 to 251112 | 2g, 2i, 2l, 2m, 2n, 2o | "finalized 2023 data"; no date |

- **2017 is not on Stacks.** The Stacks record pages for the 2017 Table 2
  parts (104462 and 104464 to 104478) redirect to the 2018 records, and their
  files return 404. The 2017 files here are Internet Archive captures of the
  CDC originals at
  `wonder.cdc.gov/nndss/static/2017/annual/2017-table2X.txt`, taken between
  December 31, 2024 and January 10, 2025 (the capture timestamp is in each
  file name and URL). The data rows of each capture are identical to the
  first capture of the same file from December 6, 2018. These are CDC's
  files, but they were fetched from a third-party archive, not from a CDC
  server.
- **2023 is PDF only.** Stacks has no text file for the 2023 tables, so the
  PDFs are parsed. Labels wrap over two or three lines and each table
  continues on a second page.
- Stacks text files are named `..._DS2.txt` or `..._DS3.txt` depending on the
  record; the script tries both.
- The NNDSS tables on data.cdc.gov are the weekly provisional tables and were
  not used.

## Scanned years, 1980 to 1992

The scans on CDC Stacks carry an OCR text layer. No OCR was run here and no
cell was corrected or read by eye. A disease-year is used only if all of the
following hold: every state cell reads as a number or a defined mark; the
states of each of the nine divisions add up to the printed division row; the
divisions add up to the printed United States row. For measles both the
indigenous and the imported column have to pass.

| Year | Disease | Why it was not used |
|---|---|---|
| 1980 | measles | US total read as "13.5062" |
| 1980 | pertussis | six rows not found in the OCR layer |
| 1981 | measles | column not found in the OCR layer |
| 1981 | pertussis | Mountain division row not readable |
| 1982 | measles | East South Central row not readable |
| 1982 | pertussis | South Atlantic row not readable |
| 1983 | measles | West South Central: states add to 40 (indigenous) and 27 (imported), printed 45 and 35 |
| 1983 | pertussis | New England: states add to 55, printed 75 |
| 1984 | pertussis | US total read as "2.276" |
| 1985 | measles | indigenous: East South Central row not readable (imported passed) |
| 1986 | measles | column not found in the OCR layer |
| 1986 | pertussis | Pacific row not readable |
| 1987 | measles | indigenous: West North Central adds to 191, printed 210; imported: Middle Atlantic row not readable |
| 1987 | pertussis | Middle Atlantic row not readable |
| 1988 | pertussis | Mountain: states add to 1,041, printed 1,043 |
| 1989 | measles | six state cells empty in the OCR layer (Maine, South Dakota, Idaho, Wyoming indigenous; Oklahoma, Wyoming imported) |
| 1989 | pertussis | one state cell empty in the OCR layer (Wyoming) |

Several of these are one cell away from passing (1984 pertussis, 1985 measles,
1988 pertussis, 1989). They could be recovered by reading those cells from the
page image, which was not done. The PDFs for all thirteen years are in `src/`.

## Other things to know

- **DC measles 2011.** The table prints "N" in the Total column and dashes in
  the Indigenous and Imported columns. Kept as printed: total blank with flag
  `N`, the two parts 0 with flag `-`.
- **Tennessee rubella 2015.** The cell is empty in both the PDF and the HTML.
- **Requests.** Stacks asks for a 10 second crawl delay in robots.txt and the
  script keeps to it. Stacks search (`/gsearch`) is disallowed and was not
  used; record numbers came from the collection browse pages.
- `src/mmwr_nd_index.html` and `src/nndss_tables_landing.html` are the two CDC
  index pages the source list was taken from.
