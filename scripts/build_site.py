#!/usr/bin/env python3
"""Download and validate current senator portraits, then build the static site."""
from __future__ import annotations
import json, re, sys, unicodedata, urllib.request
from pathlib import Path
from urllib.parse import urljoin, urlparse

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PHOTO_DIR = DIST / "photos"
SNAPSHOT = "2026-10-28"
DATA_URLS = [
    "https://unitedstates.github.io/congress-legislators/legislators-current.json",
    "https://raw.githubusercontent.com/unitedstates/congress-legislators/gh-pages/legislators-current.json",
]
ARCHIVE = "https://unitedstates.github.io/images/congress/"
UA = "SenatorFaceMemoryTrainer/1.0 (educational study tool)"

def norm(value):
    value = unicodedata.normalize("NFKD", str(value or ""))
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()

def fetch(url, accept="*/*", timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        if response.status != 200:
            raise RuntimeError("HTTP " + str(response.status))
        return response.read(), response.headers.get("Content-Type", "").split(";")[0].lower()

def load_members():
    errors = []
    for url in DATA_URLS:
        try:
            raw, _ = fetch(url, "application/json", 45)
            data = json.loads(raw.decode("utf-8"))
            if isinstance(data, list) and len(data) > 100:
                print("Loaded congressional member index from " + url)
                return data
            errors.append(url + ": unexpected data format")
        except Exception as exc:
            errors.append(url + ": " + str(exc))
    raise RuntimeError("Could not load congress-legislators dataset: " + " | ".join(errors))

def current_senate_terms(members):
    active = []
    for member in members:
        terms = [t for t in member.get("terms", [])
                 if t.get("type") == "sen"
                 and t.get("start", "0000") <= SNAPSHOT
                 and (not t.get("end") or t["end"] >= SNAPSHOT)]
        if terms:
            active.append((member, sorted(terms, key=lambda t: t.get("start", ""))[-1]))
    return active

def match_member(senator, active):
    wanted = norm(senator["name"])
    wanted_last = wanted.split()[-1]
    state = senator["abbr"]
    # Match on both state and surname first, to distinguish the two senators from one state.
    matches = [(m, t) for m, t in active
               if t.get("state") == state
               and norm(m.get("name", {}).get("last", "")).split()[-1:] == [wanted_last]]
    if len(matches) == 1:
        return matches[0]
    official = [(m, t) for m, t in active
                if t.get("state") == state
                and norm(m.get("name", {}).get("official_full", "")) == wanted]
    if len(official) == 1:
        return official[0]
    # The dataset may include legal middle names or multi-part surnames.
    broad = [(m, t) for m, t in active
             if t.get("state") == state
             and (wanted in norm(m.get("name", {}).get("official_full", ""))
                  or norm(m.get("name", {}).get("official_full", "")) in wanted)]
    if len(broad) == 1:
        return broad[0]
    raise RuntimeError("Could not uniquely match " + senator["name"] + " (" + state + "); candidates: " + str(len(matches)) + "/" + str(len(official)) + "/" + str(len(broad)))

def image_extension(data, content_type):
    if data.startswith(b"\xff\xd8\xff"): return "jpg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"): return "png"
    if data[:6] in (b"GIF87a", b"GIF89a"): return "gif"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP": return "webp"
    guessed = {"image/jpeg":"jpg", "image/png":"png", "image/gif":"gif", "image/webp":"webp"}.get(content_type)
    if guessed: return guessed
    raise RuntimeError("The response was not a recognized image file")

def download_portrait(member, term):
    bioguide = member.get("id", {}).get("bioguide")
    if not bioguide: raise RuntimeError("No Bioguide ID in congressional dataset")
    errors = []
    for size in ("225x275", "450x550", "original"):
        url = ARCHIVE + size + "/" + bioguide + ".jpg"
        try:
            data, content_type = fetch(url, "image/jpeg,image/*,*/*;q=0.8", 25)
            if len(data) < 2500: raise RuntimeError("image file too small (" + str(len(data)) + " bytes)")
            ext = image_extension(data, content_type)
            path = PHOTO_DIR / (bioguide + "." + ext)
            path.write_bytes(data)
            return {"bioguide": bioguide, "photo": "photos/" + path.name,
                    "source_url": url, "bytes": len(data)}
        except Exception as exc:
            errors.append(size + ": " + str(exc))
    # If the public archive lacks a photo, try the image declared by the member's official Senate website.
    official = (term.get("url") or "").strip()
    if official.startswith("https://") and ".senate.gov" in urlparse(official).netloc:
        try:
            page_bytes, _ = fetch(official, "text/html", 25)
            page = page_bytes.decode("utf-8", "ignore")
            pats = [
                r'<meta[^>]+(?:property|name)=["\'](?:og:image|twitter:image)["\'][^>]+content=["\']([^"\']+)',
                r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:property|name)=["\'](?:og:image|twitter:image)["\']'
            ]
            image_url = ""
            for pattern in pats:
                match = re.search(pattern, page, re.I)
                if match:
                    image_url = urljoin(official, match.group(1))
                    break
            if image_url.startswith("https://"):
                data, content_type = fetch(image_url, "image/jpeg,image/*,*/*;q=0.8", 25)
                if len(data) < 2500: raise RuntimeError("official image file too small")
                ext = image_extension(data, content_type)
                path = PHOTO_DIR / (bioguide + "." + ext)
                path.write_bytes(data)
                return {"bioguide": bioguide, "photo": "photos/" + path.name,
                        "source_url": image_url, "bytes": len(data), "fallback": "official Senate site"}
        except Exception as exc:
            errors.append("official website fallback: " + str(exc))
    raise RuntimeError(bioguide + ": image download failed: " + " | ".join(errors))

def main():
    roster_path = ROOT / "roster.json"
    roster = json.loads(roster_path.read_text(encoding="utf-8"))
    if not isinstance(roster, list) or len(roster) != 100:
        raise RuntimeError("Expected exactly 100 senators in roster.json")
    if len({(s["name"], s["abbr"]) for s in roster}) != 100:
        raise RuntimeError("Duplicate senator entries in roster.json")

    DIST.mkdir(exist_ok=True)
    if PHOTO_DIR.exists():
        for file in PHOTO_DIR.iterdir():
            if file.is_file(): file.unlink()
    PHOTO_DIR.mkdir(exist_ok=True)
    active = current_senate_terms(load_members())
    built_roster, manifest, failures = [], [], []
    for number, senator in enumerate(roster, 1):
        try:
            member, term = match_member(senator, active)
            photo = download_portrait(member, term)
            built_roster.append({**senator, "id": norm(senator["name"]).replace(" ", "-"), "bioguide": photo["bioguide"], "photo": photo["photo"]})
            manifest.append({**senator, **photo})
            print("[{0:03}/100] OK {1} ({2}) — {3}, {4:,} bytes".format(number, senator["name"], senator["abbr"], photo["bioguide"], photo["bytes"]))
        except Exception as exc:
            failures.append(senator["name"] + " (" + senator["abbr"] + "): " + str(exc))
            print("[{0:03}/100] FAIL {1}".format(number, failures[-1]), file=sys.stderr)

    (DIST / "photo-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    if failures:
        raise RuntimeError("Refusing to publish a broken photo set. Failed senators:\n - " + "\n - ".join(failures))
    if len(built_roster) != 100 or len({s["bioguide"] for s in built_roster}) != 100 or len(list(PHOTO_DIR.iterdir())) != 100:
        raise RuntimeError("Portrait validation failed: expected 100 unique mapped senators and 100 image files")

    (DIST / "roster.json").write_text(json.dumps(built_roster, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    (DIST / "index.html").write_text((ROOT / "index.html").read_text(encoding="utf-8"), encoding="utf-8")
    print("BUILD SUCCESS: exactly 100 senator portraits downloaded, validated, and bundled in dist/photos.")
    
if __name__ == "__main__":
    main()
