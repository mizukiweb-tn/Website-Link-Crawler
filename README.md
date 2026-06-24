# Snipper — Python Web Crawler

A lightweight multithreaded web crawler that recursively collects internal links within a specified domain.  
Built as a personal tool for auditing site structure and extracting URL maps.

---

## Features

- **BFS crawling** — Breadth-first traversal for accurate depth control
- **Internal link extraction** — Stays within the same domain and base path
- **URL normalization** — Strips fragments and deduplicates URLs consistently
- **Thread-safe visited tracking** — Lock-protected shared state across workers
- **Configurable thread pool** — Single shared executor, no redundant pool creation
- **`robots.txt` compliance** — Respects crawl permissions before each request
- **Rate limiting** — Configurable delay between requests to avoid server overload
- **Timeout handling** — Prevents hanging on unresponsive servers

---

## Requirements

- Python 3.10+
- See [`requirements.txt`](requirements.txt)

---

## Installation

```bash
git clone https://github.com/MizukiWeb/snipper.git
cd snipper
pip install -r requirements.txt
```

---

## Usage

Edit the configuration block at the bottom of `snipper.py`:

```python
if __name__ == "__main__":
    start_url = "https://example.com/"
    max_depth = 3
```

Then run:

```bash
python snipper.py
```

The crawler will print each visited URL to stdout and return the full list on completion.

---

## Configuration

| Variable | Default | Description |
|---|---|---|
| `REQUEST_TIMEOUT` | `10` | Seconds before a request times out |
| `REQUEST_DELAY` | `0.5` | Seconds to wait between requests |
| `MAX_WORKERS` | `5` | Number of concurrent threads |
| `USER_AGENT` | `MyPortfolioCrawler/1.0` | User-agent header sent with each request |

---

## Disclaimer

This tool is intended for use on websites you own or have explicit permission to crawl.  
Always verify compliance with a site's Terms of Service before use.

---

## License

This project is licensed under a custom restrictive license.  
See [`license.txt`](license.txt) for details.
