"""Vaccination coverage by state and year from the two current CDC files.

Four series, never joined into one line (see DATASETS.md):
  national  U.S. only, before 1995: U.S. Immunization Survey (children 1 to 4, parent recall,
            1959 to 1985) and National Health Interview Survey (1991 to 1994). No state figures exist.
  survey    NIS state estimates by survey year, 1995 to 2017, children 19 to 35 months.
  toddler   NIS-Child estimate by birth year, coverage by age 24 months (hepatitis A: 2+ doses by
            35 months). Only children born 2016 on are used, and `year` is the year they reach that
            age, so the line picks up after the survey-year series ends instead of lying on top of it.
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
    born = c["Birth Year/Birth Cohort"].astype(int)
    c, born = c[born >= 2016], born[born >= 2016]
    ci = c["95% CI (%)"].str.extract(r"([\d.]+) to ([\d.]+)")
    months = c.vaccine.map(lambda v: 35 if v == "hepa" else 24)
    return pd.DataFrame({
        "series": "toddler", "vaccine": c.vaccine, "st": c.st, "year": born + months.map({24: 2, 35: 3}),
        "label": "born " + c["Birth Year/Birth Cohort"] + ", by age " + months.astype(str) + " months", "estimate": pd.to_numeric(c["Estimate (%)"], errors="coerce"),
        "lo": pd.to_numeric(ci[0], errors="coerce"), "hi": pd.to_numeric(ci[1], errors="coerce"),
        "n": pd.to_numeric(c["Sample Size"], errors="coerce"), "method": "survey", "pct_surveyed": pd.NA, "flag": "",
    })


KMARK = {"\u2021": "d", "\u00a7": "s", "\u00b6": "p", "\u2020": "m", "\u2021\u2021": "k", "**": "e", "*": "a", "\ufffd": "u"}


def marks(f):
    toks = [t.strip() for t in f.split(".")]
    return "".join(sorted({KMARK[t] for t in toks if t in KMARK}))


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
        # CDC marks some estimates in the Footnotes column, as "≥" for 2009-10 to 2019-20 and ">=" from
        # 2020-21: the state counted a child only if up to date on all required vaccines, so the figure
        # is a lower bound ("at least") and the true share may be higher. Kept as a flag so the page can say so.
        "flag": k["Estimate (%)"].where(est.isna(), k.Footnotes.str.contains(">=|\u2265").map({True: ">=", False: ""})),
        # CDC's other footnote marks, as letters the page spells out (definitions from the dataset's own
        # "Footnotes For Kindergartner Vaccination Coverage"): d = doses counted regardless of recommended age and
        # interval, so the figure may be higher than valid doses; s = leaves out some special types of schools;
        # p = public schools only; m = coverage from a sample; k = kindergarten and 1st grade; e = may include
        # preschool; a = percent surveyed may be under the 100% shown; u = a mark that is unreadable in CDC's file
        "notes": k.Footnotes.map(marks),
    })


def survey():
    n = pd.read_csv(RAW / "vax_history" / "nis_state_survey_year.csv")
    n["vaccine"] = n.vaccine.map({"mmr_1": "mmr", "dtp_4": "dtap", "polio_3": "polio", "hepa_2": "hepa"})
    n["st"] = n.state.map(st)
    n = n[n.vaccine.notna() & n.st.notna() & n.estimate.notna()]
    lo = n.ci_low.where(n.ci_low.notna(), n.estimate - n.ci_half_width)
    hi = n.ci_high.where(n.ci_high.notna(), n.estimate + n.ci_half_width)
    return pd.DataFrame({
        "series": "survey", "vaccine": n.vaccine, "st": n.st, "year": n.year, "label": n.year.astype(str) + " survey, ages 19 to 35 months",
        "estimate": n.estimate, "lo": lo.round(1), "hi": hi.clip(upper=100).round(1), "n": pd.NA, "method": "survey", "pct_surveyed": pd.NA,
        "flag": n.flag.fillna(""),
    })


def national():
    p = pd.read_csv(RAW / "vax_history" / "national_pre1995.csv")
    usis = p[(p.survey == "USIS") & (p.age_group == "1-4 years")]
    nhis = p[p.survey == "NHIS"]
    p = pd.concat([usis, nhis])
    # the early surveys counted 3+ DTP doses, not 4+; the label carries that
    p["vk"] = p.vaccine.map({"measles": "mmr", "measles_containing": "mmr", "dtp_3": "dtap", "polio_3": "polio"})
    p = p[p.vk.notna() & p.estimate.notna()]
    what = p.vaccine.map({"measles": "measles vaccine", "measles_containing": "measles-containing vaccine", "dtp_3": "3+ DTP doses", "polio_3": "3+ polio doses"})
    who = p.survey.map({"USIS": "U.S. Immunization Survey, ages 1 to 4, parent recall", "NHIS": "National Health Interview Survey, toddlers"})
    return pd.DataFrame({
        "series": "national", "vaccine": p.vk, "st": "US", "year": p.year, "label": what + ", " + who,
        "estimate": p.estimate, "lo": pd.NA, "hi": pd.NA, "n": pd.NA, "method": p.survey, "pct_surveyed": pd.NA, "flag": p.flag.fillna(""),
    })


if __name__ == "__main__":
    out = pd.concat([national(), survey(), toddler(), kinder()], ignore_index=True)
    assert not out.duplicated(["series", "vaccine", "st", "year"]).any(), "duplicate series-vaccine-state-year"
    assert out.estimate.dropna().between(0, 100).all()
    out = out.sort_values(["series", "vaccine", "st", "year"])
    out.to_csv(DATA / "vaccination.csv", index=False)
    print(out.groupby(["series", "vaccine"]).agg(first=("year", "min"), last=("year", "max"), states=("st", "nunique"),
                                                 rows=("estimate", "size"), with_value=("estimate", "count")))
