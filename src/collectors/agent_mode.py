from __future__ import annotations
import os, re, json
from typing import Dict, List
from datetime import datetime, timezone

def _read_file(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""

def _fmt(t, **kw):
    o=t
    for k,v in kw.items(): o=o.replace("{"+k+"}", str(v))
    return o

def _fence(text, label):
    import re
    m=re.search(rf"```{label}\s*(.*?)\s*```", text, flags=re.DOTALL|re.IGNORECASE)
    return m.group(1).strip() if m else ""

def _jsonl(block):
    rows=[]
    for ln in block.splitlines():
        ln=ln.strip()
        if not ln: continue
        try: rows.append(json.loads(ln))
        except: pass
    return rows

def _iso(ts):
    if not ts: return ""
    try:
        if isinstance(ts,str):
            if ts.endswith("Z"): return ts
            dt=datetime.fromisoformat(ts.replace("Z","+00:00"))
        elif isinstance(ts,(int,float)):
            dt=datetime.fromtimestamp(ts, tz=timezone.utc)
        else: return ""
        return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except: return ""

def _row(obj, city_fb):
    cites = obj.get("citations") or []
    cite_txt = " | ".join([c for c in cites if isinstance(c,str)])[:500]
    return {
        "full_name_or_handle": obj.get("full_name_or_handle",""),
        "platform": obj.get("platform","agent_mode"),
        "post_title_or_snippet": obj.get("post_title_or_snippet",""),
        "post_url": obj.get("post_url",""),
        "posted_at": _iso(obj.get("posted_at")),
        "location_text": obj.get("location_text") or city_fb,
        "service_types": obj.get("service_types",""),
        "availability": obj.get("availability",""),
        "rate_info": obj.get("rate_info",""),
        "contact_method": obj.get("contact_method",""),
        "intent_signal": obj.get("intent_signal",""),
        "quality_notes": (obj.get("quality_notes","") + (f" | cites: {cite_txt}" if cite_txt else "")),
        "source_screenshot_path": "",
        "match_score": 0,
    }

def collect(config: Dict, run_ts, logger):
    try:
        from azure.identity import DefaultAzureCredential
        from azure.ai.projects import AIProjectClient
        from azure.ai.agents import AgentsClient
        try:
            from azure.ai.agents.models import BingGroundingTool, BingCustomSearchTool
        except Exception:
            BingGroundingTool=None; BingCustomSearchTool=None
    except Exception as e:
        logger.error("Azure Agents SDK not available: %s", e); return []

    agent_cfg=(config.get("sources",{}) or {}).get("agent_mode",{})
    if not agent_cfg.get("enabled", False): return []

    ep=os.getenv("AZURE_AI_FOUNDRY_PROJECT_ENDPOINT","")
    model=os.getenv("AZURE_AI_MODEL_DEPLOYMENT","")
    bing=os.getenv("BING_CONNECTION_NAME","")
    bingc=os.getenv("BING_CUSTOM_CONNECTION_NAME","")
    if not ep or not model:
        logger.error("Missing AZURE_AI_FOUNDRY_PROJECT_ENDPOINT or AZURE_AI_MODEL_DEPLOYMENT"); return []

    sys_t=_read_file("configs/agent_system_prompt.md") or "You are a compliant sourcing agent."
    run_t=_read_file("configs/agent_run_prompt.txt") or "Return CANDIDATES_JSONL only."

    sys_p=_fmt(sys_t, PRIMARY_CITY=config.get("primary_city","San Antonio, TX"), NEARBY_CITIES=", ".join(config.get("nearby_cities",[])), RADIUS_MI=config.get("radius_mi",35))
    run_p=_fmt(run_t, PRIMARY_CITY=config.get("primary_city","San Antonio, TX"), NEARBY_CITIES=", ".join(config.get("nearby_cities",[])), RADIUS_MI=config.get("radius_mi",35), MAX_ITEMS=agent_cfg.get("max_items",50))

    cred=DefaultAzureCredential()
    project=AIProjectClient(endpoint=ep, credential=cred)
    agents=AgentsClient(project)
    tools=[]
    try:
        if bing and BingGroundingTool: tools+=BingGroundingTool(connection_id=bing).definitions
        if bingc and BingCustomSearchTool: tools+=BingCustomSearchTool(connection_id=bingc).definitions
    except Exception as e:
        logger.warning("Could not attach Bing tools: %s", e)

    agent=agents.create_agent(name="cleaner-sourcing-agent", model=model, instructions=sys_p, tools=tools)
    thread=agents.threads.create()
    agents.messages.create(thread_id=thread.id, role="user", content=run_p)
    run=agents.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)

    msgs=agents.messages.list(thread_id=thread.id).data
    text=""
    for m in msgs[::-1]:
        if m.role=='assistant' and m.content:
            if isinstance(m.content, list):
                text=" ".join([getattr(p,'text','') or getattr(p,'content','') or '' for p in m.content])
            else: text=str(m.content)
            break
    if not text: logger.warning('Agent returned no content.'); return []

    block=_fence(text,'CANDIDATES_JSONL'); audit=_fence(text,'AUDIT')
    if audit: logger.info('Agent AUDIT:\n%s', audit)
    cand=_jsonl(block)
    rows=[]; city_fb=config.get('primary_city','San Antonio, TX')
    for obj in cand: rows.append(_row(obj, city_fb))
    return rows[:agent_cfg.get('max_items',50)]
