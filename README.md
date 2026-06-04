# West Africa Daily Briefs

Daily research briefs covering West African business, markets, and investment opportunities. Published every morning at 2:14am UTC.

## Topics

| Day | Topic | Category |
|-----|-------|----------|
| Monday | Local App & Digital Product Ideas | `tech` |
| Tuesday | Crypto & Digital Assets | `crypto` |
| Wednesday | Agribusiness & Commodities | `agribusiness` |
| Thursday | Renewable Energy & Power | `energy` |
| Friday | IPOs & Stock Market Watch | `stocks` |
| Saturday | Governance, Elections, Regulation & Trade | `governance` |
| Sunday | Import/Export Trade Trends (alternating) | `trade` |

## Structure

```
briefs/           # Daily research briefs (Markdown)
  YYYY/
    MM/
      YYYY-MM-DD-<topic-slug>.md
newsletters/      # Weekly compiled newsletters
  YYYY/
    YYYY-W<week>.md
scripts/          # Automation scripts
  newsletter.py   # Weekly newsletter generator
  publish.sh      # Push briefs to GitHub
site/             # Future public site
  data/           # JSON data feeds
  public/         # Static site files
```

## Data Format

Each daily brief is a Markdown file with YAML frontmatter containing metadata for the site and newsletter.

## License

MIT
