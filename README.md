# MyWeekDayBirth — Pinterest Auto-Poster

Posts 15 pins/day automatically to Pinterest, 3 sessions × 5 pins.

## Setup (one-time)

1. Go to github.com → New repository → name it `myweekdaybirth-pinterest`
2. Set visibility to **Private**
3. Upload all files from this folder
4. Go to Settings → Secrets and variables → Actions → New repository secret
   - Name: `PINTEREST_TOKEN`
   - Value: your Pinterest access token (pina_...)
5. Go to Actions tab → Enable workflows

The automation starts immediately and runs at 7h, 13h, 19h (Swiss time) every day.

## Files

- `pinterest_poster.py` — main script, posts pins via Pinterest API v5
- `poster_state.json` — tracks rotation index and daily count (auto-created)
- `.github/workflows/post_pins.yml` — GitHub Actions schedule

## Monitoring

Go to github.com/[your-username]/myweekdaybirth-pinterest/actions to see each run's logs.
