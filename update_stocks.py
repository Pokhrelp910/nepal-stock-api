"""
Nepal Stock Market (NEPSE) Daily Stock Price Updater
Fetches latest listed companies, symbols, and LTP prices, then saves to stocks.json
"""

import urllib.request
import re
import json
from datetime import datetime

def fetch_stocks_merolagani():
    url = "https://merolagani.com/LatestMarket.aspx"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode("utf-8", errors="ignore")

    table_match = re.search(r"(<table[^>]*>.*?</table>)", html, re.DOTALL | re.IGNORECASE)
    if not table_match:
        raise Exception("Table not found on Merolagani")

    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", table_match.group(1), re.DOTALL | re.IGNORECASE)
    stocks = []

    for row in rows:
        m = re.search(r"title=['\"]([^'\"]+)['\"][^>]*>([^<]+)</a>", row)
        if m:
            full_title = m.group(1).strip()
            symbol = m.group(2).strip()
            
            # Extract full company name if present in "SYMBOL (Full Name)"
            name = symbol
            name_match = re.search(r"\(([^)]+)\)", full_title)
            if name_match:
                name = name_match.group(1).strip()

            tds = re.findall(r"<td[^>]*>(.*?)</td>", row, re.DOTALL)
            if len(tds) >= 2:
                ltp_raw = re.sub(r"<[^>]+>", "", tds[1]).replace(",", "").strip()
                change_raw = re.sub(r"<[^>]+>", "", tds[2]).replace(",", "").strip() if len(tds) > 2 else "0"
                try:
                    ltp = float(ltp_raw)
                except ValueError:
                    ltp = 0.0
                try:
                    change = float(change_raw)
                except ValueError:
                    change = 0.0

                stocks.append({
                    "symbol": symbol,
                    "name": name,
                    "ltp": ltp,
                    "change": change
                })

    if not stocks:
        raise Exception("Failed to parse stock entries from Merolagani table")

    return {
        "status": "success",
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source": "Merolagani / NEPSE",
        "total_stocks": len(stocks),
        "stocks": stocks
    }

def main():
    print("Fetching latest stock prices from NEPSE / Merolagani...")
    data = fetch_stocks_merolagani()
    output_file = "stocks.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"SUCCESS: {output_file} updated successfully with {data['total_stocks']} stocks!")

if __name__ == "__main__":
    main()
