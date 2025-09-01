from __future__ import annotations
import pandas as pd
from src.collectors.craigslist import collect as collect_craigslist
from src.collectors.agent_mode import collect as collect_agent
from src.utils.scoring import compute_match_score
from src.utils.dedupe import dedupe

COLUMNS = ["full_name_or_handle","platform","post_title_or_snippet","post_url","posted_at","location_text","service_types","availability","rate_info","contact_method","intent_signal","quality_notes","source_screenshot_path","match_score"]

def run_pipeline(config, run_ts, logger):
    rows = []
    stats = {"sources":{}, "items_found":0, "items_kept":0, "duplicates_dropped":0}
    if config.get('sources',{}).get('craigslist',{}).get('enabled'):
        cl = collect_craigslist(config, run_ts, logger); rows += cl; stats['sources']['craigslist']=len(cl)
    if config.get('sources',{}).get('agent_mode',{}).get('enabled'):
        ag = collect_agent(config, run_ts, logger); rows += ag; stats['sources']['agent_mode']=len(ag)
    stats['items_found']=len(rows)
    df = pd.DataFrame(rows, columns=COLUMNS).fillna('')
    df['posted_at']=pd.to_datetime(df['posted_at'], errors='coerce', utc=True).dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    df['match_score']=df.apply(lambda r: compute_match_score(r, {'intent_signals':config.get('intent_signals',[]),'primary_city':config.get('primary_city'),'nearby_cities':config.get('nearby_cities',[]),'rate_floor':config.get('rate_floor',18)}, run_ts), axis=1)
    before=len(df); df=dedupe(df); stats['duplicates_dropped']=before-len(df)
    df=df.sort_values(by=['match_score','posted_at'], ascending=[False, False]).reset_index(drop=True)
    stats['items_kept']=len(df); return df, stats
