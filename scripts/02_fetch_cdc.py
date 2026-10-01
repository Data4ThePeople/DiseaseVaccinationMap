"""Download the CDC files from data.cdc.gov: current weekly cases and the two vaccination datasets."""
from common import RAW, download

FILES = {
    "x9gk-5huc": "NNDSS Weekly Data (2022 on)",
    "fhky-rtsk": "Vaccination Coverage among Young Children (0-35 Months), NIS-Child",
    "ijqb-a7ye": "Vaccination Coverage and Exemptions among Kindergartners",
}

if __name__ == "__main__":
    for key, name in FILES.items():
        p = download(f"https://data.cdc.gov/api/views/{key}/rows.csv?accessType=DOWNLOAD", RAW / "cdc" / f"{key}.csv")
        print(p.name, p.stat().st_size, name)
