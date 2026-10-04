# Nepal Stock Market (NEPSE) Daily API

A free, lightweight daily NEPSE listed stocks and LTP price API.

## Features
- Fetches all listed NEPSE symbols, company names, LTP (Closing prices), and % change.
- Dynamic: Automatically detects and includes new IPOs and scrips.
- Cached via Vercel Edge CDN and GitHub raw/jsDelivr CDN.
- Fast, zero maintenance, and completely free.

## Endpoints
- `GET /api/stocks` (Vercel)
- Or via jsDelivr CDN / GitHub Raw: `stocks.json`
