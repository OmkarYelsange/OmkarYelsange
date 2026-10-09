# OmkarYelsange animated GitHub profile — setup

This repository is intended to be the special profile repository named exactly:

`OmkarYelsange`

## 1. Copy the files

Replace the contents of your `OmkarYelsange/OmkarYelsange` repository with the files in this package.

## 2. Generate your portrait

Put a clear headshot in the repository root as:

`source-photo.png`

Install the one-time portrait dependencies:

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r scripts/requirements-portrait.txt
```

Then run:

```bash
python scripts/prep_photo.py source-photo.png source-prepped.png
python scripts/make_ascii_svg.py source-prepped.png omkar-ascii.svg
```

The resulting `omkar-ascii.svg` is the animated terminal-style ASCII portrait.

## 3. Generate contribution graphics locally

For the heatmap/stats dependencies:

```bash
pip install -r scripts/requirements.txt
```

Then:

```bash
$env:GH_PROFILE_USER="OmkarYelsange"   # Windows PowerShell
python scripts/fetch_contributions.py
python scripts/generate_streak_svg.py OmkarYelsange contrib-heatmap.svg
python scripts/render_stats_svg.py
```

On Linux/macOS, use:

```bash
export GH_PROFILE_USER="OmkarYelsange"
```

## 4. GitHub Actions

The workflow at `.github/workflows/update-profile-art.yml` automatically refreshes:

- `data/contributions.json`
- `contrib-heatmap.svg`
- `stats.svg`

It runs on pushes to `main`, manually from Actions, and once per day.

Make sure the repository is public and Actions has permission to write repository contents. The workflow declares `contents: write`.

## 5. Push

```bash
git add .
git commit -m "feat: add animated terminal GitHub profile"
git push origin main
```

Then open the **Actions** tab and run **Update profile art** once manually. After that, the scheduled job keeps the contribution graphics current.

## 6. What you should edit later

Most personalization is already done. The only file you are expected to edit regularly is `README.md` when you add projects, certifications, or new links.

For a new portrait, replace `source-photo.png`, regenerate `source-prepped.png`, and regenerate `omkar-ascii.svg` locally. `source-photo.png` and `source-prepped.png` are ignored by Git so your original photo is not committed accidentally.
