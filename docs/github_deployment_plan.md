# GitHub Deployment Plan

## Deployment Decision

Deploy the project with two public URLs:

- GitHub repository URL: source code, preprocessing scripts, documentation, report materials, and reproducibility notes.
- GitHub Pages URL: static web system served from the `web/` directory.

Use GitHub Actions to deploy `web/` directly to GitHub Pages. This is preferred because the actual application root is `web/index.html`, while GitHub Pages' simple branch settings mainly target the repository root or `/docs`.

## Submission Requirements Covered

The final exam requires all of the following:

- Full analysis code in a public GitHub repository.
- A deployed GitHub Pages system from the same repository.
- A PDF report submitted separately through LMS.
- README documentation for data sources, baseline years, preprocessing, and reproduction.
- Static GeoJSON/JSON data included for the deployed system.

## Repository Contents

Include:

- `README.md`
- `docs/`
- `report/`
- `scripts/`
- `config/`
- `tests/`
- `web/`
- `web/data/`
- `data_raw/README.md`
- `data_raw/source_inventory.csv`

Exclude by default:

- Large raw GIS files under `data_raw/`
- Intermediate generated outputs under `data_processed/`
- Python cache files such as `__pycache__/`
- Temporary directories such as `.tmp/`

## Important Data Note

The current `.gitignore` ignores `web/data/*`, but the deployed web app depends on those JSON and GeoJSON files through `fetch`.

Before committing, force-add the static deployment data:

```powershell
git add -f web/data
```

If `web/data` is not committed, the GitHub Pages site may load the HTML/CSS/JS but fail to render maps, charts, and comparison metrics.

## Git Initialization and First Commit

```powershell
git init
git branch -M main
git add README.md docs report scripts config tests web public .gitignore
git add -f web/data
git status
git commit -m "Initial project release"
```

`public/` can be included if it is used as a mirror of static data, but the GitHub Pages deployment target should remain `web/`.

## GitHub Repository Setup

Create a new GitHub repository, for example:

```text
office_district_comparison
```

Then connect and push:

```powershell
git remote add origin https://github.com/<username>/office_district_comparison.git
git push -u origin main
```

Use a public repository unless there is a specific reason to keep it private. A public repository is simpler for final exam evaluation.

## GitHub Pages Workflow

Create `.github/workflows/pages.yml`:

```yaml
name: Deploy GitHub Pages

on:
  push:
    branches: [main]

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: true

jobs:
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/configure-pages@v5
      - uses: actions/upload-pages-artifact@v3
        with:
          path: web
      - id: deployment
        uses: actions/deploy-pages@v4
```

Commit and push:

```powershell
git add .github/workflows/pages.yml
git commit -m "Add GitHub Pages deployment"
git push
```

In GitHub, confirm that `Settings > Pages` uses GitHub Actions as the source.

Expected Pages URL:

```text
https://<username>.github.io/office_district_comparison/
```

## README Checklist

Before final submission, update `README.md` with:

- GitHub Pages URL.
- Repository URL.
- Analysis target: Pangyo Techno Valley vs Cheongna International Business District.
- District boundary definitions and selection rationale.
- Data sources and baseline years.
- Preprocessing script order.
- Local web execution command.
- Explanation that `web/data` contains static deployment data.
- Link or path to the final report.
- AI usage note.

## Final Submission Checklist

Before submitting to LMS:

- GitHub repository is public and accessible in an incognito browser.
- GitHub Pages URL opens without local files.
- Browser console has no missing `web/data` fetch errors.
- Maps, isochrone layers, charts, and click interactions work on GitHub Pages.
- Report values match the deployed system values.
- README documents data sources, baseline years, and preprocessing.
- PDF report includes both the repository URL and GitHub Pages URL.
