# Tie-out

Built by `scripts/12_tieout.py`. Every line below was recomputed from a raw file.
**Result: all checks passed.**

## A. Packed data against the case table

17,678 state-years in the table, 17,678 filled cells on the page, 0 differ.

## B. National sum on the page against the U.S. row CDC printed

Only years where every state on the page comes from the final annual table. The printed U.S. row is read from the table itself, with footnote marks stripped.

| disease, year | CDC printed | page sum | |
|---|---|---|---|
| mumps 1975 | 59647 | 59647 | ok |
| pertussis 1985 | 3589 | 3589 | ok |
| pertussis 1990 | 4570 | 4570 | ok |
| hepatitis_a 1995 | 31582 | 31582 | ok |
| pertussis 1995 | 5137 | 5137 | ok |
| polio 1995 | 2 | 2 | ok |
| hepatitis_a 2000 | 13397 | 13397 | ok |
| pertussis 2000 | 7867 | 7867 | ok |
| hepatitis_a 2005 | 4488 | 4488 | ok |
| pertussis 2005 | 25616 | 25616 | ok |
| polio 2005 | 1 | 1 | ok |
| hepatitis_a 2010 | 1670 | 1670 | ok |
| measles 2010 | 63 | 63 | ok |
| mumps 2010 | 2612 | 2612 | ok |
| pertussis 2010 | 27550 | 27550 | ok |
| measles 2015 | 188 | 188 | ok |
| mumps 2015 | 1329 | 1329 | ok |
| pertussis 2015 | 20762 | 20762 | ok |
| hepatitis_a 2019 | 18846 | 18846 | ok |
| measles 2019 | 1275 | 1275 | ok |
| mumps 2019 | 3780 | 3780 | ok |
| pertussis 2019 | 18617 | 18617 | ok |
| polio 2019 | 0 | 0 | ok |
| hepatitis_a 2020 | 9946 | 9946 | ok |
| measles 2020 | 12 | 12 | ok |
| mumps 2020 | 694 | 694 | ok |
| pertussis 2020 | 6124 | 6124 | ok |
| polio 2020 | 0 | 0 | ok |
| hepatitis_a 2023 | 1643 | 1643 | ok |
| measles 2023 | 64 | 64 | ok |
| mumps 2023 | 433 | 433 | ok |
| pertussis 2023 | 7063 | 7063 | ok |
| polio 2023 | 0 | 0 | ok |

114 disease-years compared in all; the table lists every fifth year, 2019, 2023 and any mismatch.

Years where the table gives one or more states no figure (NN, not notifiable there). Those states show as no data. In 1968 to 1973 upstate New York did not report mumps but the table prints New York City's count, which is in the U.S. total and not on the map; the page sum falls short by exactly that part:

| disease, year | CDC printed | page sum | part not mapped | |
|---|---|---|---|---|
| mumps 1968 | 152209 | 148319 | 3890 | ok |
| mumps 1969 | 90918 | 86940 | 3978 | ok |
| mumps 1970 | 104953 | 101729 | 3224 | ok |
| mumps 1972 | 74215 | 71658 | 2557 | ok |
| mumps 1973 | 69612 | 64695 | 4917 | ok |
| mumps 1974 | 59128 | 59128 | 0 | ok |
| mumps 1977 | 21436 | 21436 | 0 | ok |
| mumps 1978 | 16817 | 16817 | 0 | ok |
| mumps 1979 | 14225 | 14225 | 0 | ok |
| mumps 1980 | 8576 | 8576 | 0 | ok |
| mumps 1981 | 4941 | 4941 | 0 | ok |
| mumps 1982 | 5270 | 5270 | 0 | ok |
| mumps 1983 | 3355 | 3355 | 0 | ok |
| mumps 1984 | 3021 | 3021 | 0 | ok |
| mumps 1985 | 2982 | 2982 | 0 | ok |
| mumps 1986 | 7790 | 7790 | 0 | ok |
| mumps 1987 | 12848 | 12848 | 0 | ok |
| mumps 1988 | 4866 | 4866 | 0 | ok |
| mumps 1989 | 5712 | 5712 | 0 | ok |
| mumps 1990 | 5292 | 5292 | 0 | ok |
| mumps 1991 | 4264 | 4264 | 0 | ok |
| mumps 1992 | 2572 | 2572 | 0 | ok |
| mumps 1993 | 1692 | 1692 | 0 | ok |
| mumps 1994 | 1537 | 1537 | 0 | ok |
| mumps 1995 | 906 | 906 | 0 | ok |
| mumps 1996 | 751 | 751 | 0 | ok |
| mumps 1997 | 683 | 683 | 0 | ok |
| polio 1997 | 3 | 3 | 0 | ok |
| mumps 1998 | 666 | 666 | 0 | ok |
| polio 1998 | 1 | 1 | 0 | ok |
| mumps 1999 | 387 | 387 | 0 | ok |
| mumps 2000 | 338 | 338 | 0 | ok |
| mumps 2001 | 266 | 266 | 0 | ok |
| mumps 2003 | 231 | 231 | 0 | ok |
| mumps 2005 | 314 | 314 | 0 | ok |
| hepatitis_a 2007 | 2979 | 2979 | 0 | ok |
| hepatitis_a 2008 | 2585 | 2585 | 0 | ok |
| measles 2011 | 220 | 220 | 0 | ok |
| hepatitis_a 2014 | 1239 | 1239 | 0 | ok |
| hepatitis_a 2015 | 1390 | 1390 | 0 | ok |

## C. Project Tycho years, re-read from the zip

| disease, state, year | from zip | page | |
|---|---|---|---|
| measles OH 1941 | 81859 | 81859 | ok |
| measles CA 1958 | 35074 | 35074 | ok |
| measles TX 1934 | 29699 | 29699 | ok |
| polio NY 1952 | 2637 | 2637 | ok |
| polio MN 1946 | 2569 | 2569 | ok |
| pertussis PA 1947 | 9589 | 9589 | ok |
| hepatitis_a CA 1971 | 9623 | 9623 | ok |
| pertussis OH 1950 | 7334 | 7334 | ok |

## D. CDC weekly years, re-read from the weekly file

| disease, state, year | from file | page | |
|---|---|---|---|
| pertussis OH 2024 | 1708 | 1708 | ok |
| measles TX 2025 | 803 | 803 | ok |
| pertussis NY 2024 | 2871 | 2871 | ok |
| mumps CA 2025 | 53 | 53 | ok |

## E. Population and rate

| state, year | BEA population | page population | |
|---|---|---|---|
| OH 1941 | 6958000 | 6958000 | ok |
| CA 1958 | 14880000 | 14880000 | ok |
| TX 2025 | 31709821 | 31709821 | ok |
| AK 1950 | 135000 | 135000 | ok |
| NY 1990 | 18020784 | 18020784 | ok |

Rates are computed in the browser as cases / population x 100,000 from these two numbers; nothing is stored.

## F. Vaccination points against publisher files

| point | publisher | page | |
|---|---|---|---|
| kindergarten MMR, Ohio 2024-25 | 88.3 | 88.3 | ok |
| toddler MMR, Texas born 2020 (shown at 2022) | 89.4 | 89.4 | ok |
| survey DTP 4+, California 2003 | 84.0 | 84.0 | ok |
| national polio 3+, 1964 | 87.6 | 87.6 | ok |

