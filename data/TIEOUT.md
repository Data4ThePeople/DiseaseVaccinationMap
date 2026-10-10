# Tie-out

Built by `scripts/12_tieout.py`. Every line below was recomputed from a raw file.
**Result: all checks passed.**

## A. Packed data against the case table

20,131 state-years in the table, 20,131 filled cells on the page, 0 differ.

## B. National sum on the page against the U.S. row CDC printed

Only years where every state on the page comes from the final annual table. The printed U.S. row is read from the table itself, with footnote marks stripped.

| disease, year | CDC printed | page sum | |
|---|---|---|---|
| pertussis 1960 | 14809 | 14809 | ok |
| polio 1960 | 2525 | 2525 | ok |
| polio 1965 | 61 | 61 | ok |
| hepatitis_a 1970 | 56797 | 56797 | ok |
| measles 1970 | 47351 | 47351 | ok |
| polio 1970 | 31 | 31 | ok |
| hepatitis_a 1975 | 35855 | 35855 | ok |
| measles 1975 | 24374 | 24374 | ok |
| mumps 1975 | 59647 | 59647 | ok |
| pertussis 1975 | 1738 | 1738 | ok |
| polio 1975 | 8 | 8 | ok |
| hepatitis_a 1980 | 29087 | 29087 | ok |
| measles 1980 | 13506 | 13506 | ok |
| pertussis 1980 | 1730 | 1730 | ok |
| polio 1980 | 8 | 8 | ok |
| pertussis 1985 | 3589 | 3589 | ok |
| polio 1985 | 7 | 7 | ok |
| hepatitis_a 1990 | 31441 | 31441 | ok |
| pertussis 1990 | 4570 | 4570 | ok |
| polio 1990 | 7 | 7 | ok |
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

208 disease-years compared in all; the table lists every fifth year, 2019, 2023 and any mismatch.

Years where the table gives one or more states no figure (NN, not notifiable there), which show as no data, or where New York shows New York City only (mumps, 1968 to 1973, when upstate New York did not report). The page sum must equal the printed U.S. total, plus any printed part the map does not show:

| disease, year | CDC printed | page sum | part not mapped | |
|---|---|---|---|---|
| pertussis 1956 | 31732 | 31732 | 0 | ok |
| pertussis 1957 | 28295 | 28295 | 0 | ok |
| pertussis 1958 | 32148 | 32148 | 0 | ok |
| pertussis 1959 | 40005 | 40005 | 0 | ok |
| measles 1960 | 441703 | 441703 | 0 | ok |
| measles 1961 | 423919 | 423919 | 0 | ok |
| measles 1962 | 481530 | 481530 | 0 | ok |
| pertussis 1962 | 17749 | 17749 | 0 | ok |
| measles 1963 | 385156 | 385156 | 0 | ok |
| pertussis 1963 | 17135 | 17135 | 0 | ok |
| measles 1964 | 458083 | 458083 | 0 | ok |
| measles 1965 | 261904 | 261904 | 0 | ok |
| pertussis 1965 | 6799 | 6799 | 0 | ok |
| measles 1966 | 204136 | 204136 | 0 | ok |
| pertussis 1966 | 7717 | 7717 | 0 | ok |
| mumps 1968 | 152209 | 152209 | 0 | ok |
| mumps 1969 | 90918 | 90918 | 0 | ok |
| mumps 1970 | 104953 | 104953 | 0 | ok |
| mumps 1971 | 124939 | 124939 | 0 | ok |
| mumps 1972 | 74215 | 74215 | 0 | ok |
| mumps 1973 | 69612 | 69612 | 0 | ok |
| pertussis 1973 | 1759 | 1759 | 0 | ok |
| hepatitis_a 1974 | 40358 | 40358 | 0 | ok |
| mumps 1974 | 59128 | 59128 | 0 | ok |
| pertussis 1974 | 2402 | 2402 | 0 | ok |
| mumps 1977 | 21436 | 21436 | 0 | ok |
| pertussis 1977 | 2177 | 2177 | 0 | ok |
| mumps 1978 | 16817 | 16817 | 0 | ok |
| mumps 1979 | 14225 | 14225 | 0 | ok |
| mumps 1980 | 8576 | 8576 | 0 | ok |
| mumps 1981 | 4941 | 4941 | 0 | ok |
| mumps 1982 | 5270 | 5270 | 0 | ok |
| mumps 1983 | 3355 | 3355 | 0 | ok |
| mumps 1984 | 3021 | 3021 | 0 | ok |
| hepatitis_a 1985 | 23210 | 22592 | 618 | ok |
| mumps 1985 | 2982 | 2982 | 0 | ok |
| hepatitis_a 1986 | 23430 | 22910 | 520 | ok |
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
| measles CA 1948 | 49335 | 49335 | ok |
| measles TX 1934 | 29699 | 29699 | ok |
| polio NY 1952 | 2637 | 2637 | ok |
| polio MN 1946 | 2569 | 2569 | ok |
| pertussis PA 1947 | 9589 | 9589 | ok |
| measles IL 1950 | 18528 | 18528 | ok |
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

