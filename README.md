# Plagiarism Checker Website

A web app where a user uploads a document and gets back matches for similar content found around the Internet.

Project brief: [Plagiarism checker website (DevProjects)](https://www.codementor.io/projects/web/plagiarism-checker-website-atx32nf0oa)

## Goal

Publishing companies often check manuscripts by hand: someone searches Google for phrases from the text to find existing work. This project automates that check.

## How it works

1. The user uploads a document on a web page.
2. The back-end reads the document text.
3. It extracts random phrases of about 5-10 words each.
4. It runs a Google search for each phrase.
5. It scrapes the top five results for each phrase and cleans the content (removes headers and so on, keeps the main text).
6. It compares the uploaded text with each scraped page: a word counts as copied when it sits in a run of 8 words that also appears in the page. Similarity is the share of the document found (containment), per page and across all pages.
7. It returns:
   - a similarity percentage,
   - the similar parts of the text, each with a link to the original URL.

## Requirements checklist

- [x] Web page where the user can upload a document
- [x] Extract random phrases from the document
- [x] Run a Google search for the phrases
- [x] Scrape the top five results per phrase
- [x] Clean the scraped content (main text only)
- [x] Compare the uploaded content with each result (any metric, or make it customisable)
- [x] Return a similarity percentage
- [x] Return the similar parts with links to the source URLs
- [x] Extra: download the results as a PDF report

## Stack

- Python with Flask (JSON API)
- ScrapingBee Google Search API for the search step; result pages fetched with plain `urllib`
- BeautifulSoup to clean the HTML
- fpdf2 for the PDF report
- Astro + Svelte (in `web/`) with Bootstrap for the front end

## API

| Endpoint | Body | Returns |
|---|---|---|
| `POST /api/check` | form field `document` (.txt, UTF-8, max 2 MB) | JSON: `similarity`, `matches` (url, similarity, passages), `results` (phrases and their result links) |
| `POST /api/report` | the JSON from `/api/check` | `report.pdf` |

## Setup

Flask API with [uv](https://docs.astral.sh/uv/), front end with [bun](https://bun.sh/).

```bash
uv sync
(cd web && bun install)
echo 'SCRAPINGBEE_API_KEY=...' > .env
```

Development, two terminals, then open http://localhost:4321 (`/api` is proxied to Flask):

```bash
uv run --env-file .env plagiarism-checker
cd web && bun run dev
```

Production-style: `cd web && bun run build`, then run Flask alone; it serves `web/dist` at http://localhost:5000.

Tests (mocked, never call the network): `uv run pytest`

## Status

All checklist items are done.

Known limits:

- English text only; `.txt` uploads only.
- Exact 8-word matches, so reworded text is missed.
- Sites that block bots cannot be fetched, which can lower the score.
- Each check uses 5 ScrapingBee searches.

## License

[MIT](LICENSE)
