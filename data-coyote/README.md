# Data Coyote 🐺📊
Fetch, clean, and publish Santa Fe crime & tourism data for Tableau + GitHub Pages.

## Quick Start (local)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env
notepad .env   # set FBI_API_KEY, (optional) FBI_API_URL_BASE, TOURISM_DATA_URL
python .\main.py
```
Outputs:
- `data/processed/crime_latest.csv`
- `data/processed/tourism_latest.csv`

## Environment
- `FBI_API_KEY` (required for live FBI data)
- `FBI_API_URL_BASE` (optional; ends with `api_key=`), otherwise ORI auto-lookup is used
- `TOURISM_DATA_URL` (optional; direct CSV/JSON export; blank uses sample)

## GitHub Actions
- Nightly refresh (`.github/workflows/data-coyote-nightly.yml`)
- GitHub Pages publish (`.github/workflows/gh-pages.yml`)

## Tableau
Open `tableau/Data Coyote Starter.twb` and point to `data/processed/*.csv` or connect directly to Google Sheets if enabled.
