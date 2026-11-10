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
6. It compares the uploaded text with each scraped page, using a text similarity metric.
7. It returns:
   - a similarity percentage,
   - the similar parts of the text, each with a link to the original URL.

## Requirements checklist

- [ ] Web page where the user can upload a document
- [ ] Extract random phrases from the document
- [ ] Run a Google search for the phrases
- [ ] Scrape the top five results per phrase
- [ ] Clean the scraped content (main text only)
- [ ] Compare the uploaded content with each result (any metric, or make it customisable)
- [ ] Return a similarity percentage
- [ ] Return the similar parts with links to the source URLs
- [ ] Extra: download the results as a PDF report

## Suggested stack

- Python with Flask
- ScrapingBee (or a similar service) to scrape Google results
- BeautifulSoup to clean the HTML
- Bootstrap for the front end

## Setup

This project uses [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

## Status

Project skeleton only. Nothing is implemented yet.

## License

[MIT](LICENSE)
