# Daily Digest

Mira-published daily reading digest.

- **Live site**: https://richardk1992-boop.github.io/daily-digest/
- **Auto-publish**: every morning at 06:00 Beijing time, Mira generates the digest, calls a `repository_dispatch` event on this repo, and GitHub Actions commits the HTML into `digests/` + redeploys Pages.

## Layout

```
digests/         one HTML file per day (YYYY-MM-DD.html)
.meta/           one JSON per day with vol / title metadata
index.html       auto-regenerated table of contents
scripts/         build_index.py (rebuilds index.html from digests + meta)
.github/         Actions workflow
```

## Manual trigger

If Mira's cron is down, you can publish a digest by hand:

```bash
# Drop your HTML into digests/YYYY-MM-DD.html, then:
python3 scripts/build_index.py
git add digests/ .meta/ index.html
git commit -m "digest: YYYY-MM-DD manual"
git push
```

GitHub Actions will pick up the push and redeploy Pages within ~60s.
