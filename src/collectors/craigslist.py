from __future__ import annotations
import feedparser
from datetime import datetime, timezone
from urllib.parse import urlencode
from src.utils.compliance import is_allowed

def _build_feed_url(subdomain: str, query: str) -> str:
    params = {"format":"rss", "query":query}
    return f"https://{subdomain}.craigslist.org/search/hss?{urlencode(params)}"

def collect(config, run_ts, logger):
    cfg = config.get("sources",{}).get("craigslist",{})
    cities_map = cfg.get("cities_map", {})
    intent_signals = config.get("intent_signals", [])
    max_items = int(cfg.get("max_items_per_run", 150))
    targets = [config.get("primary_city")] + config.get("nearby_cities", [])
    rows = []
    for city in targets:
        sub = cities_map.get(city, None)
        if not sub:
            logger.warning("No Craigslist subdomain mapped for city '%s' — skipping", city)
            continue
        for phrase in intent_signals:
            url = _build_feed_url(sub, phrase)
            if not url.startswith("https://") or not is_allowed(url):
                logger.info("Disallowed by robots or invalid: %s", url)
                continue
            feed = feedparser.parse(url)
            for entry in feed.entries[:max_items]:
                post_url = entry.link
                if not is_allowed(post_url):
                    continue
                title = getattr(entry, "title", "")
                published = getattr(entry, "published", None)
                posted_at = None
                if published and hasattr(entry, "published_parsed") and entry.published_parsed:
                    try:
                        posted_at = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc).isoformat()
                    except Exception:
                        posted_at = datetime.now(timezone.utc).isoformat()
                snippet = getattr(entry, "summary", "")
                location_text = getattr(entry, "cr_location", "") if hasattr(entry, "cr_location") else city
                rows.append({
                    "full_name_or_handle": "",
                    "platform": "craigslist",
                    "post_title_or_snippet": f"{title} — {snippet}",
                    "post_url": post_url,
                    "posted_at": posted_at,
                    "location_text": location_text,
                    "service_types": "",
                    "availability": "",
                    "rate_info": "",
                    "contact_method": "",
                    "intent_signal": phrase,
                    "quality_notes": "",
                    "source_screenshot_path": "",
                    "match_score": 0,
                })
    return rows
