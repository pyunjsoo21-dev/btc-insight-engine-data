import json, os, urllib.request, urllib.parse, datetime

BASE = "https://api.bybit.com"
SYMBOL = "BTCUSDT"
CATEGORY = "linear"

def get(path, params):
    url = BASE + path + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent":"BJ/1.2"})
    with urllib.request.urlopen(req, timeout=20) as r:
        data = json.loads(r.read().decode())
    if data.get("retCode") != 0:
        raise Exception(f"retCode {data.get('retCode')}: {data.get('retMsg')}")
    return data["result"]

def kline(interval):
    r = get("/v5/market/kline", {"category":CATEGORY,"symbol":SYMBOL,"interval":interval,"limit":1})
    c = r.get("list",[[]])[0]
    return {"interval":interval,"open":float(c[1]),"high":float(c[2]),"low":float(c[3]),"close":float(c[4])}

def main():
    t = get("/v5/market/tickers", {"category":CATEGORY,"symbol":SYMBOL})["list"][0]
    f = get("/v5/market/funding/history", {"category":CATEGORY,"symbol":SYMBOL,"limit":1})["list"][0]
    oi = get("/v5/market/open-interest", {"category":CATEGORY,"symbol":SYMBOL,"intervalTime":"1h","limit":1})["list"][0]
    data = {
        "time": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "last": float(t["lastPrice"]),
        "high24h": float(t["highPrice24h"]),
        "low24h": float(t["lowPrice24h"]),
        "change24h%": float(t["price24hPcnt"])*100,
        "kline": { "4h":kline("240"), "12h":kline("720"), "1d":kline("D") },
        "fundingRate": float(f["fundingRate"]),
        "openInterest": float(oi["openInterest"])
    }
    os.makedirs("data", exist_ok=True)
    with open("data/snapshot.json","w") as fp:
        json.dump(data, fp, indent=2)
    print("snapshot saved:", data["time"])

if __name__ == "__main__":
    main()
