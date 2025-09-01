from datetime import datetime, timezone, timedelta; import re
INTENT_BONUS=35; RECENT_BONUS=20; PROXIMITY_BONUS=15; AVAIL_BONUS=10; RATE_BONUS=10; PROOF_BONUS=10; VAGUE_PENALTY=-10; SPAM_PENALTY=-20

def compute_match_score(row,cfg,run_ts):
  s=0; intent=(row.get('intent_signal') or '').lower(); intents=[x.lower() for x in (cfg.get('intent_signals') or [])]
  if any(p in intent for p in intents): s+=INTENT_BONUS
  try:
    posted=datetime.fromisoformat(str(row.get('posted_at')).replace('Z','+00:00'))
    if (run_ts-posted)<=timedelta(days=14): s+=RECENT_BONUS
  except Exception: pass
  loc=(row.get('location_text') or '').lower(); primary=(cfg.get('primary_city') or '').lower(); nearby=[c.lower() for c in (cfg.get('nearby_cities') or [])]
  if any(c in loc for c in [primary,*nearby]): s+=PROXIMITY_BONUS
  if (row.get('availability') or '').strip(): s+=AVAIL_BONUS
  m=re.search(r"\$?\s*([0-9]+(\.[0-9]+)?)", (row.get('rate_info') or '').lower());
  if m:
    try:
      if float(m.group(1))>=float(cfg.get('rate_floor',18)): s+=RATE_BONUS
    except Exception: pass
  q=(row.get('quality_notes') or '').lower();
  if any(k in q for k in ['years','experience','insured','bonded','references','reviews','supplies','business page']): s+=PROOF_BONUS
  if not (row.get('service_types') or '').strip() and not (row.get('availability') or '').strip(): s+=VAGUE_PENALTY
  if any(k in (row.get('post_title_or_snippet') or '').lower() for k in ['crypto','loan','xxx','adult']): s+=SPAM_PENALTY
  return max(0,min(100,s))
