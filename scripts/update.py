"""Scarica il calendario ufficiale (xlsx su Google Drive) e scrive data.json.
Gira da solo su GitHub Actions. Nessun dato personale (telefoni, email) viene copiato."""
import io, json, re, sys, urllib.request, datetime as dt
from zoneinfo import ZoneInfo

FILE_ID = "1HxbnxHDU9dUw3kheqOQOVoNASoB-FIl_"
URL = f"https://drive.google.com/uc?export=download&id={FILE_ID}"
TZ = ZoneInfo("Europe/Rome")
CITIES = ["Borgone di Susa", "Pianezza", "Caselette", "Brandizzo", "Torino"]

def roman(s):
    v = {"I": 1, "V": 5, "X": 10, "L": 50}
    n = 0
    for i, ch in enumerate(s):
        x = v[ch]
        n += -x if i + 1 < len(s) and v[s[i + 1]] > x else x
    return n

def clean(v):
    s = "" if v is None else str(v).strip()
    return "" if s in ("0", "0.0", "None", "-") else s

def num(v):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return 0

def to_date(v):
    if isinstance(v, dt.datetime):
        return v.date()
    if isinstance(v, dt.date):
        return v
    if isinstance(v, (int, float)) and 30000 < v < 80000:  # numero di serie Excel
        return (dt.datetime(1899, 12, 30) + dt.timedelta(days=float(v))).date()
    m = re.search(r"(\d{1,2})\s*[/\s.\-]\s*(\d{1,2})\s*[/\s.\-]\s*(\d{2,4})", str(v or ""))
    if not m:
        return None
    d, mo, y = map(int, m.groups())
    return dt.date(y + 2000 if y < 100 else y, mo, d)

def to_time(v):
    if isinstance(v, dt.time):
        return v
    if isinstance(v, dt.datetime):
        return v.time()
    if isinstance(v, (int, float)) and 0 <= v < 1:
        s = round(float(v) * 86400)
        return dt.time(s // 3600, (s % 3600) // 60)
    m = re.search(r"(\d{1,2})[.:](\d{2})", str(v or ""))
    return dt.time(int(m.group(1)), int(m.group(2))) if m else dt.time(21, 0)

def place(raw):
    raw = re.sub(r"\s+", " ", clean(raw).replace("–", " - ")).strip()
    raw = re.sub(r"\bVIa\b", "Via", raw)
    if not raw:
        return {"venue": "", "city": "", "q": ""}
    city = next((c for c in CITIES if c.lower() in raw.lower()), "Torino")
    addr = re.sub(r"\s*\(TO\)\s*$", "", raw)
    addr = re.sub(r"[\s,\-]*\bT[O0]\b\.?\s*$", "", addr).strip(" ,-")
    short = re.split(r"\s+-\s+|\s+(?=[Vv]ia\b)", addr)[0].strip(" ,-")
    short = re.sub(r"\s*" + re.escape(city) + r"\s*$", "", short, flags=re.I).strip(" ,-") or addr
    short = short[0].upper() + short[1:]
    q = addr if city.lower() in addr.lower() else f"{addr}, {city}"
    return {"venue": short, "city": city, "q": q}

def match(g, n, d, t, a, b, venue_raw, note, score, sets):
    when = dt.datetime.combine(d, t, tzinfo=TZ)
    sets = [list(s) for s in sets if s[0] or s[1]]
    m = {"g": g, "n": n, "t": when.isoformat(), "a": a, "b": b, **place(venue_raw)}
    if note:
        m["note"] = note[0].upper() + note[1:]
    if score and (score[0] or score[1]):
        m["score"] = list(score)
    if sets:
        m["sets"] = sets
    return m

def parse_sheet(ws):
    out, g = [], 0
    for row in ws.iter_rows(values_only=True):
        cells = list(row) + [None] * 30
        txt = [clean(c) for c in cells]
        for c in txt:
            m = re.match(r"^([IVXL]+)°\s*Giornata", c)
            if m:
                g = roman(m.group(1))
                break
        j = next((k for k, c in enumerate(txt[:6]) if re.fullmatch(r"\d{5,7}(\.0)?", c)), None)
        if j is None or not g:
            continue
        d, a, b = to_date(cells[j + 1]), clean(cells[j + 3]), clean(cells[j + 5])
        if not (d and a and b):
            continue
        sets = [(num(cells[j + 11 + 2 * k]), num(cells[j + 12 + 2 * k])) for k in range(5)]
        out.append(match(g, num(cells[j]), d, to_time(cells[j + 2]), a, b,
                         cells[j + 6], clean(cells[j + 7]),
                         (num(cells[j + 9]), num(cells[j + 10])), sets))
    return out

def main():
    import openpyxl
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    data = urllib.request.urlopen(req, timeout=60).read()
    if not data.startswith(b"PK"):
        sys.exit("Il file scaricato non è un Excel: controlla che su Drive sia condiviso con 'Chiunque abbia il link'.")
    wb = openpyxl.load_workbook(io.BytesIO(data), data_only=True)
    matches = next((m for m in (parse_sheet(ws) for ws in wb.worksheets) if len(m) >= 10), None)
    if not matches:
        sys.exit("Non ho trovato le partite nel file: forse è cambiato il formato.")
    matches.sort(key=lambda m: (m["t"], m["n"]))
    try:
        old = json.load(open("data.json", encoding="utf-8"))
        if old.get("matches") == matches:
            print("Nessuna novità.")
            return
    except (OSError, ValueError):
        pass
    out = {"updated": dt.datetime.now(TZ).isoformat(timespec="minutes"), "matches": matches}
    json.dump(out, open("data.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"Aggiornato: {len(matches)} partite.")

if __name__ == "__main__":
    main()
