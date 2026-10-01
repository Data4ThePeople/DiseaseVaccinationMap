# Tie-out

Built by `scripts/12_tieout.py`. Every line below was recomputed from a raw file.
**Result: all checks passed.**

## A. Packed data against the case table

17,628 state-years in the table, 17,628 filled cells on the page, 0 differ.

## B. National sum on the page against the U.S. row CDC printed

Only years where every state on the page comes from the final annual table. The printed U.S. row is read from the table itself, with footnote marks stripped.

| disease, year | CDC printed | page sum | |
|---|---|---|---|
| pertussis 1985 | 3589 | 3589 | ok |
| pertussis 1990 | 4570 | 4570 | ok |
| hepatitis_a 1995 | 31582 | 31582 | ok |
| mumps 1995 | 906 | 906 | ok |
| pertussis 1995 | 5137 | 5137 | ok |
| polio 1995 | 2 | 2 | ok |
| hepatitis_a 2000 | 13397 | 13397 | ok |
| mumps 2000 | 338 | 338 | ok |
| pertussis 2000 | 7867 | 7867 | ok |
| hepatitis_a 2005 | 4488 | 4488 | ok |
| mumps 2005 | 314 | 314 | ok |
| pertussis 2005 | 25616 | 25616 | ok |
| polio 2005 | 1 | 1 | ok |
| hepatitis_a 2010 | 1670 | 1670 | ok |
| measles 2010 | 63 | 63 | ok |
| mumps 2010 | 2612 | 2612 | ok |
| pertussis 2010 | 27550 | 27550 | ok |
| hepatitis_a 2015 | 1390 | 1390 | ok |
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

128 disease-years compared in all; the table lists every fifth year, 2019, 2023 and any mismatch.

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
| mumps WI 1968 | 15413 | 15413 | ok |

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

