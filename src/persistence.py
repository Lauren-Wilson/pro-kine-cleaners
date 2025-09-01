from __future__ import annotations
import uuid
from src.utils.db import get_conn, upsert_candidates, archive_stale_candidates, insert_run

def persist_results(df, stats, run_ts, logger, archive_after_days:int=30):
  run_id=str(uuid.uuid4()); con=get_conn()
  try:
    insert_run(con, run_id, run_ts.isoformat(), stats)
    upsert_candidates(con, df, run_id, run_ts.isoformat())
    archive_stale_candidates(con, cutoff_days=archive_after_days, as_of_ts=run_ts.isoformat())
    logger.info('Persisted run_id=%s', run_id); return run_id
  finally:
    con.close()
