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
| `checks_scans_1980_1992.csv` | Which scanned years passed the strict test and why the others failed. Despite the name it now covers 1968 to 1992 (mumps from 1968, measles and pertussis from 1980). |
| `checks_image_cells.csv` | Every cell read by eye from a rendered page image: year, disease, area, PDF page, what the OCR text layer had, what the image shows. For spot-checking. |
| `checks_column_map.csv` | The printed column header and US total cell that was read for each disease and year. |
| `checks_marks.csv` | Mark definitions as printed in each source, with the page. |
| `checks_finality.csv` | The sentence in each source that says the data are final and gives the cutoff date. |

## Coverage

| Years | Diseases | Source |
|---|---|---|
| 1968 to 1970, 1972 to 1992 | mumps | scanned annual summaries, CDC Stacks |
| 1984, 1988, 1990, 1991, 1992 | measles (total, indigenous, imported) | scanned annual summaries, CDC Stacks |
| 1985, 1990, 1991, 1992 | pertussis | scanned annual summaries, CDC Stacks |
| 1993 to 2015 | all seven diseases | MMWR Summary of Notifiable Diseases, Table 2, issue PDF |
| 2016 to 2023 | all seven diseases | NNDSS Annual Tables, Table 2 parts |

Not obtained: mumps for 1971 (see "Mumps from the scans" below); measles for
1980 to 1983, 1985 to 1987 and 1989; pertussis for 1980 to 1984 and 1986 to
1989 (see "Scanned years"). Rubella, hepatitis A, diphtheria and polio were
not attempted before 1993; measles and pertussis were not attempted before
1980.

## Results of the checks

- State sum against the printed United States row: 322 disease-years checked,
  all pass. 25 of those are trivial (diseases with no US cases, taken from a
  footnote, see below). For mumps in 1968, 1969, 1970, 1972 and 1973 the 51
  state rows fall short of the US row by exactly the New York City count:
  upstate New York is printed NN in those years, so the New York row is left
  blank (see the New York rule below) while the US total includes the city's
  cases. Every scanned year kept also passes the stricter division test
  described under "Scanned years".
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
  in `annual_area_cases_all.csv`. When one part is not a number (mumps
  1968 to 1973: upstate New York is NN), `cases` is blank and the flag says
  which part is missing and what the other part was, e.g.
  `upstate:NN;other part=3890` (the New York City count).
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
  - `read from page image`: scanned years only. The OCR text layer was
    damaged for this cell and the value was read by eye from the page
    rendered with PyMuPDF. `read from page image: -` and
    `read from page image: NN` are a dash (0) and NN read the same way. For
    New York, `read from page image (upstate part)` or `(NYC part)` says
    which half was read from the image. The page is in `source_table` and
    every such cell is listed in `checks_image_cells.csv`.
  - `NR`: printed once (North Carolina mumps, 1974). The 1974 issue does not
    define it. `cases` blank.
- **Cells left blank (31 in all).** NN: mumps in New Mexico 1993 to 1999 and
  Oregon 1993 to 2001, rubella in Mississippi 1994 to 1998, paralytic polio in
  Wisconsin 1997 and 1998. N: mumps in Oregon 2003 and 2005, measles total in
  DC 2011. U: hepatitis A in DC 2007, 2008, 2014, 2015. blank: rubella in
  Tennessee 2015.

## Mark definitions by period (as printed, pages in `checks_marks.csv`)

| Years | Marks |
|---|---|
| 1968, 1969, 1971 to 1974 | `...` Data not available; `-` Quantity zero; `NN` Report of disease not required by State Health Department. Read from the legend on the page image (p.2 of each issue). |
| 1970 | No legend found in the scan. The 1970 mumps column contains only numbers and NN. |
| 1975, 1976 | `NA` Data not available; `-` Quantity zero; `NN` not notifiable. Page image, p.2. |
| 1977 to 1983 | `NA` Data not available; `-` No reported cases; `NN` not notifiable. 1977 to 1981 read from the page image (1977 p.2, 1978 p.10, 1979 p.7, 1980 p.12, 1981 p.15). |
| 1984 to 2001 | `-` No reported cases; `NA` Data not available; `NN` Report of disease is not required in that jurisdiction (not notifiable). Printed once per issue under "Explanation of symbols used in tables". |
| 2002 to 2007 | `-` No reported cases; `N` Not notifiable; `U` Unavailable. Printed under each Table 2 page and in the front list. |
| 2008 to 2015 | `-` No reported cases; `N` Not reportable; `U` Unavailable (2014 and 2015 front list: "Data not available"). |
| 2016 | `-` No reported cases; `N` Not Reportable; `U` Unavailable. |
| 2017 to 2023 | `-` No reported cases, the reporting jurisdiction did not submit any cases to CDC; `N` Not reportable by law, statute, or regulation in the reporting jurisdiction; `U` Unavailable. |

In the 1985, 1986, 1988 and 1989 scans the symbol after "No reported cases
....." is not legible in the OCR text layer. It was checked on the page
image: it is the dash in all four (1985 p.6, 1986 p.6, 1988 p.7, 1989 p.6).
This replaces the inference made in the first pass. Both "Quantity zero" and
"No reported cases" are taken to define the dash as 0.

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

From 1978 the issues say the data are "compiled in final form in this
summary"; 1977 says it "carries final figures". No cutoff date is stated in
any scanned issue. **The 1973 to 1977 and 1979 issues say they include
provisional data from California** "in order not to delay the publication".
No finality statement was found in the OCR text of 1968 to 1972. File name
is `stacks_<record>_DS1.pdf`; URL `https://stacks.cdc.gov/view/cdc/<record>`.

| Year | Stacks record | Table page (PDF) | Used | Table |
|---|---|---|---|---|
| 1968 | 1717 | 10 | mumps | Table 6, notifiable diseases by division and state |
| 1969 | 838 | 10 | mumps | Table 6 |
| 1970 | 951 | 10 | mumps | Table 6 |
| 1971 | 1829 | 10 | none | Table 6 (mumps left out, see below) |
| 1972 | 1895 | 10 | mumps | Table 6 |
| 1973 | 1849 | 10 | mumps | Table 5 |
| 1974 | 1743 | 10 | mumps | Table 5 |
| 1975 | 1041 | 10 | mumps | Table 5 |
| 1976 | 1130 | 11 | mumps | Table 5 |
| 1977 | 10894 | 12 | mumps | Table 5 |
| 1978 | 10895 | 21 | mumps | Notifiable diseases by division and state |
| 1979 | 1577 | 13 | mumps | same |
| 1980 | 1484 | 19 | mumps | same |
| 1981 | 1307 | 79 | mumps | "MUMPS - Reported cases, by area and age", Total column (the 1981 issue has no mumps column in the general by-state table) |
| 1982 | 35066 | 16 | mumps | by division and area |
| 1983 | 35188 | 21 | mumps | same |
| 1984 | 35267 | 16 | measles, mumps | same |
| 1985 | 35429 | 12 | pertussis, mumps | same |
| 1986 | 35496 | 12 | mumps | same |
| 1987 | 35629 | 12 | mumps | same |
| 1988 | 35958 | 15 | measles, mumps | same |
| 1989 | 35853 | 13 | mumps | same |
| 1990 | 35905 | 19 | measles, pertussis, mumps | same |
| 1991 | 36010 | 21 | measles, pertussis, mumps | same |
| 1992 | 36063 | 23 | measles, pertussis, mumps | same |

Stacks catalog titles that give the wrong year: 35267 ("Annual Summary
1985") is the 1984 summary, 35429 ("for 1986") is 1985, and 1717 ("Summary
1967, For Release December 1968") is the 1968 summary; the table pages name
the year in each case. The 1977 and 1978 summaries (10894, 10895) are in the
Stacks MMWR collection (cdc:101), not the NNDSS collection.

### Mumps from the scans, 1968 to 1992

Mumps became nationally notifiable in 1968. Each year kept passes the strict
test: every state cell is a number or a defined mark, the states of each of
the nine divisions add to the printed division row, and the divisions add to
the printed US row. The table page of each year names the year it covers.

Where the OCR text layer was damaged, the cell was read by eye from the page
rendered with PyMuPDF (300 dpi, 600 dpi for single cells). Those cells carry
the flag `read from page image`. 103 cells were read this way, counting
division rows (83 of the 1,224 state rows kept carry the flag, including 3
New York rows where one half was read). By year: 1968 1, 1970 1, 1972 1,
1979 19, 1980 6, 1981 15, 1982 9, 1983 17, 1984 1, 1986 14, 1987 15, 1989 4.
In 1981 the OCR layer had a wrong but readable value (Louisiana 76, image
6), which the Mountain/West South Central division check caught.
1969, 1973 to 1978, 1985 and 1988 and 1990 to 1992 needed no image reading.
Row labels the OCR layer garbled ("N. M.", "R.l.", "III.") are matched by
label only, never by number.

US totals as printed (thousands separators as printed): 1968 152,209;
1969 90,918; 1970 104,953; 1972 74,215; 1973 69,612; 1974 59,128; 1975
59,647; 1976 38,492; 1977 21,436; 1978 16,817; 1979 14,225; 1980 8,576; 1981
4,941; 1982 5,270; 1983 3,355; 1984 3,021; 1985 2,982; 1986 7,790; 1987
12,848; 1988 4,866; 1989 5,712; 1990 5,292; 1991 4,264; 1992 2,572.

**1971 is left out.** With the OCR damage read from the image, every cell is
legible, but two cells are printed in a way that can only be turned into a
count by deciding what the printer meant:
- District of Columbia is printed `-99` (checked at 600 dpi, p.10).
- Ohio is printed `8.784`, with a point where a comma belongs.

The year would pass the division test exactly if these were taken as 99 and
8,784. Doing that would be choosing a reading because it makes the sums
work, which the rules do not allow, so 1971 is not in the file. The other
damaged 1971 cells read cleanly from the image (Illinois 5,585, New Jersey
1,819, Virginia 1,073, Georgia dash, East South Central 8,933, Arkansas
157, Oregon 1,772).

Other notes:
- New York 1968 to 1973: upstate New York is NN, so the New York row is
  blank and its flag carries the New York City count.
- Mumps NN (not notifiable, `cases` blank) in the scanned years: Pennsylvania
  1968; North Carolina 1968 to 1970 and 1973; Arizona 1973, 1974, 1977;
  Oklahoma 1978 to 1986; New Mexico 1980 to 1992; Florida 1982, 1983;
  Oregon 1982 to 1992; Mississippi 1985 to 1988; Rhode Island 1988. These
  states' blanks are real gaps in reporting, not zeros.
- 1974: North Carolina is printed `NR`, which the issue does not define;
  `cases` blank.
- 1970: no symbol legend was found in the scan; the mumps column has only
  numbers and NN, so no mark needed a definition.

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
