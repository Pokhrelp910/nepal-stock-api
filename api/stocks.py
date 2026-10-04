from http.server import BaseHTTPRequestHandler
import urllib.request
import re
import json
from datetime import datetime

def fetch_stocks():
    url = "https://merolagani.com/LatestMarket.aspx"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=12) as resp:
        html = resp.read().decode("utf-8", errors="ignore")

    table_match = re.search(r"(<table[^>]*>.*?</table>)", html, re.DOTALL | re.IGNORECASE)
    if not table_match:
        raise Exception("Table not found")

    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", table_match.group(1), re.DOTALL | re.IGNORECASE)
    stocks = []

    for row in rows:
        m = re.search(r"title=['\"]([^'\"]+)['\"][^>]*>([^<]+)</a>", row)
        if m:
            full_title = m.group(1).strip()
            symbol = m.group(2).strip()
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

    return {
        "status": "success",
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source": "Merolagani / NEPSE",
        "total_stocks": len(stocks),
        "stocks": stocks
    }

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            data = fetch_stocks()
            body = json.dumps(data, ensure_ascii=False)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            # Edge CDN cache for 30 minutes, revalidate in background
            self.send_header('Cache-Control', 's-maxage=1800, stale-while-revalidate=86400')
            self.end_headers()
            self.wfile.write(body.encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            err_data = {"status": "error", "message": str(e)}
            self.wfile.write(json.dumps(err_data).encode('utf-8'))
