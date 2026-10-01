"""Vaccination coverage by state and year from the two current CDC files.

Two series, never joined into one line (see DATASETS.md):
  toddler   NIS-Child survey estimate by birth year, coverage by age 24 months
            (hepatitis A: 2+ doses by 35 months). Has a 95% interval and sample size.
  kinder    each state's own kindergarten count or survey, by school year. `year` is
            the calendar year the school year ends in (2009-10 -> 2010).

Output: data/vaccination.csv
"""
import pandas as pd

from common import DATA, NAME_TO_ABBR, RAW

TODDLER = {  # (Vaccine, Dose, age) -> vaccine key
    ("≥1 Dose MMR", "", "24 Months"): "mmr",
    ("DTaP", "≥4 Doses", "24 Months"): "dtap",
    ("Polio", "≥3 Doses", "24 Months"): "polio",
    ("Hep A", "≥2 Doses", "35 Months"): "hepa",
    ("Hep B", "≥3 Doses", "24 Months"): "hepb",
}
KINDER = {"MMR": "mmr", "DTP, DTaP, or DT": "dtap", "Polio": "polio", "Hepatitis B": "hepb"}


def st(name):
    return "US" if name == "United States" else NAME_TO_ABBR.get(name.upper())


def toddler():
    c = pd.read_csv(RAW / "cdc" / "fhky-rtsk.csv", dtype=str).fillna("")
    c = c[(c["Dimension Type"] == "Age") & c["Birth Year/Birth Cohort"].str.fullmatch(r"\d{4}")]
    c["vaccine"] = [TODDLER.get(k) for k in zip(c.Vaccine, c.Dose, c.Dimension)]
    c["st"] = c.Geography.map(st)
    c = c[c.vaccine.notna() & c.st.notna()]
    ci = c["95% CI (%)"].str.extract(r"([\d.]+) to ([\d.]+)")
    return pd.DataFrame({
        "series": "toddler", "vaccine": c.vaccine, "st": c.st, "year": c["Birth Year/Birth Cohort"].astype(int),
        "label": "born " + c["Birth Year/Birth Cohort"], "estimate": pd.to_numeric(c["Estimate (%)"], errors="coerce"),
        "lo": pd.to_numeric(ci[0], errors="coerce"), "hi": pd.to_numeric(ci[1], errors="coerce"),
        "n": pd.to_numeric(c["Sample Size"], errors="coerce"), "method": "survey", "pct_surveyed": pd.NA, "flag": "",
    })


def kinder():
    k = pd.read_csv(RAW / "cdc" / "ijqb-a7ye.csv", dtype=str).fillna("")
    k["vaccine"] = k["Vaccine/Exemption"].map(KINDER)
    k["st"] = k.Geography.map(st)
    k = k[k.vaccine.notna() & k.st.notna()]
    est = pd.to_numeric(k["Estimate (%)"], errors="coerce")  # NReq, NR and blanks become empty
    return pd.DataFrame({
        "series": "kinder", "vaccine": k.vaccine, "st": k.st, "year": k["School Year"].str[:4].astype(int) + 1,
        "label": k["School Year"] + " school year", "estimate": est, "lo": pd.NA, "hi": pd.NA,
        "n": pd.to_numeric(k["Population Size"], errors="coerce"), "method": k["Survey Type"].str.strip(),
        "pct_surveyed": pd.to_numeric(k["Percent Surveyed"], errors="coerce"),
        "flag": k["Estimate (%)"].where(est.isna(), ""),
    })


if __name__ == "__main__":
    out = pd.concat([toddler(), kinder()], ignore_index=True)
    assert not out.duplicated(["series", "vaccine", "st", "year"]).any(), "duplicate series-vaccine-state-year"
    assert out.estimate.dropna().between(0, 100).all()
    out = out.sort_values(["series", "vaccine", "st", "year"])
    out.to_csv(DATA / "vaccination.csv", index=False)
    print(out.groupby(["series", "vaccine"]).agg(first=("year", "min"), last=("year", "max"), states=("st", "nunique"),
                                                 rows=("estimate", "size"), with_value=("estimate", "count")))
