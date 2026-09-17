# 🛒 Trackers — Terminal E-Commerce Price Tracker

> Track product prices from your terminal. Set target prices, monitor changes, and get notified when a deal hits.

[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](./CONTRIBUTING.md)

**Trackers** is a lightweight command-line tool that monitors product prices on e-commerce sites. Add product URLs, set target prices, and let it check for you — no browser, no dashboard, no accounts.

---

## ✨ Features

- 🛍️ **Track products by URL** — add any supported product page.
- 🎯 **Target price alerts** — get notified when a product hits your price.
- 📉 **Price change tracking** — see drops in green, increases in red.
- 🔁 **One-shot or scheduled checks** — run once or watch on an interval.
- 💾 **Persistent storage** — items saved in a local `tracked_items.json`.
- 🧩 **Modular tracker design** — add new sites with a single class.
- 🐍 **Pure Python** — small dependency footprint, easy to extend.

---

## 📦 Supported Sites

| Site    | Domains matched |
| ------- | --------------- |
| Amazon  | `amazon.*`, `amzn.in`, `amzn.to`, `amzn.eu`, `a.co` |

> Adding support for a new site takes ~30 lines. See [Adding a new store](#-adding-a-new-store).

---

## 🚀 Quick Start

```bash
git clone https://github.com/mohitsharma099999-tech/trackers.git
cd trackers

python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

python price_tracker.py add "https://www.amazon.in/dp/XXXXXXXXXX" 4999
python price_tracker.py list
python price_tracker.py check
```

> **Windows users:** replace `python3` with `python` and use `venv\Scripts\activate`.

---

## ▶️ Usage

The CLI takes a subcommand as its first argument:

```bash
python price_tracker.py <command> [args]
```

| Command | Description |
| ------- | ----------- |
| `add <url> [target_price]` | Add a product to track. Target price is optional. |
| `list` | Show all tracked products and their current prices. |
| `check` | Fetch current prices once and report changes. |
| `watch [minutes]` | Continuously check prices on an interval (default: 30). |
| `remove <index>` | Remove a product by its index from `list`. |

### Examples

```bash
# Add a product with a target price of ₹4999
python price_tracker.py add "https://amzn.in/d/017v5yTj" 4999

# Add a product without a target (just track it)
python price_tracker.py add "https://www.amazon.in/dp/B0CHX3QBCH"

# List everything you're tracking
python price_tracker.py list

# Run a single price check
python price_tracker.py check

# Check every 60 minutes
python price_tracker.py watch 60

# Remove the 2nd item in your list
python price_tracker.py remove 2
```

Press `Ctrl+C` to stop `watch`.

---

## 🖥️ Example Output

### `list`

```text
+---+-------------------------+----------+---------+---------+
| # | Product                 | Current  | Target  | Change  |
+===+=========================+==========+=========+=========+
| 1 | Sony WH-1000XM5         | $348.00  | $299.00 | -$12.00 |
| 2 | Kindle Paperwhite 16 GB | $139.99  | —       | +$5.00  |
+---+-------------------------+----------+---------+---------+
```

### `check`

```text
Checking prices...

1. Sony WH-1000XM5 Wireless Headphones
   ▼ $12.00 ($348.00)
2. Kindle Paperwhite (16 GB)
   ▲ $5.00 ($139.99)
```

### Target reached

```text
3. Anker 20,000mAh Power Bank
   ▼ $8.00 ($27.99)
   🎯 TARGET REACHED! Target: $29.99, Now: $27.99
```

---

## 🏗️ Project Structure

```text
trackers/
├── price_tracker.py         # CLI entry point, storage, commands
├── trackers/                # Site-specific scrapers
│   ├── __init__.py          # Tracker registry + get_tracker()
│   ├── base.py              # BaseTracker abstract class
│   └── amazon.py            # Amazon implementation
├── requirements.txt
├── tracked_items.json       # Auto-generated data store (gitignored)
├── .gitignore
├── LICENSE
└── README.md
```

---

## ⚙️ How It Works

```text
   product URL
        │
        ▼
 ┌──────────────┐    resolve short link (amzn.in → amazon.in/dp/…)
 │  get_tracker │──────────────────────────────────────────────────┐
 └──────┬───────┘                                                  │
        ▼                                                          ▼
 ┌──────────────┐    fetch HTML with a browser-like User-Agent
 │  fetch_page  │◄─────────────────────────────────────────────────┘
 └──────┬───────┘
        ▼
 ┌──────────────┐    parse price + title via CSS selectors
 │  get_price   │
 │  get_title   │
 └──────┬───────┘
        ▼
 ┌──────────────┐    compare with saved + target price
 │   compare    │
 └──────┬───────┘
        ▼
 ┌──────────────┐
 │  report /    │
 │  alert       │
 └──────────────┘
```

---

## 🔌 Adding a New Store

1. Create `trackers/yourstore.py`:

   ```python
   from .base import BaseTracker

   class YourStoreTracker(BaseTracker):
       def get_price(self, url):
           soup = self.fetch_page(url)
           el = soup.select_one("span.price")
           if not el:
               raise Exception("Price not found")
           return float(el.get_text(strip=True).replace("$", ""))

       def get_title(self, url):
           soup = self.fetch_page(url)
           el = soup.select_one("h1.product-title")
           return el.get_text(strip=True) if el else "Unknown Product"
   ```

2. Register it in `trackers/__init__.py`:

   ```python
   from .yourstore import YourStoreTracker

   def get_tracker(url):
       if "yourstore.com" in url.lower():
           return YourStoreTracker()
       if any(d in url.lower() for d in AMAZON_DOMAINS):
           return AmazonTracker()
       raise Exception(f"No tracker available for URL: {url}")
   ```

Done — the CLI will now pick it up automatically.

---

## 🛠️ Tech Stack

| Layer | Tool |
| ----- | ---- |
| Language | Python 3.8+ |
| HTTP | `requests` |
| HTML parsing | `beautifulsoup4` + `lxml` |
| CLI colors | `colorama` |
| Table output | `tabulate` |
| Storage | JSON file |

---

## ⚠️ Known Limitations

- **Amazon blocks scrapers.** You may see `Could not find price on page` or `503`. Workarounds:
  - Try `cloudscraper` in place of `requests`
  - Use Playwright/Selenium for JS-rendered pages
  - Route through a scraping API (ScraperAPI, Bright Data, ZenRows)
- **CSS selectors break** when sites redesign. The Amazon tracker has multiple fallbacks for this reason.
- **No notifications yet.** Currently prints to terminal only.

---

## 🔐 Responsible Usage

This project is for **personal price monitoring**.

- Respect each site's **Terms of Service** and **`robots.txt`**.
- Don't hammer servers — use `watch` with a sensible interval (30+ min).
- Don't bypass CAPTCHAs, logins, or anti-bot protections.
- Only track sites where automated access is permitted.

---

## 🗺️ Roadmap

- [ ] Telegram / Discord / email notifications
- [ ] SQLite backend with full price history
- [ ] Price history chart (`matplotlib` or terminal sparklines)
- [ ] Config file for per-item check intervals
- [ ] Additional store adapters (Flipkart, eBay, Newegg…)
- [ ] `cloudscraper` fallback for Amazon

---

## 🤝 Contributing

PRs are welcome.

```bash
git checkout -b feature/your-feature
git commit -m "feat: add your feature"
git push origin feature/your-feature
```

Then open a Pull Request. See [`CONTRIBUTING.md`](./CONTRIBUTING.md) for details.

---

## 📜 License

Licensed under the **MIT License**. See [`LICENSE`](./LICENSE).

---

## 👨‍💻 Author

**Mohit Sharma** — [@mohitsharma099999-tech](https://github.com/mohitsharma099999-tech)

---

## ⭐ Support

If this project saved you a few manual page refreshes:

- ⭐ Star the repo
- 🍴 Fork it
- 🐛 Open an issue
- 💡 Suggest a feature

> **Track prices. Automate monitoring. Buy when the price is right. 🛒⚡**
