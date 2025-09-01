from src.pipeline import run_pipeline
from src.utils.logging_utils import build_logger
from src.utils.paths import OUTPUT_DIR, LOGS_DIR, ensure_dirs
from src.persistence import persist_results
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, timezone
import yaml, json

def main():
    load_dotenv()
    ensure_dirs()
    logger = build_logger(LOGS_DIR / "pipeline.log")
    with open('configs/config.yaml','r') as f:
        config = yaml.safe_load(f)
    run_ts = datetime.now(timezone.utc)
    df, stats = run_pipeline(config, run_ts, logger)
    out_csv = OUTPUT_DIR / 'cleaners.csv'
    out_md = OUTPUT_DIR / 'messages.md'
    df.to_csv(out_csv, index=False)
    from src.utils.outreach import write_messages_markdown
    write_messages_markdown(df, out_md)
    run_id = persist_results(df, stats, run_ts, logger)
    logger.info('RUN SUMMARY %s', json.dumps({'run_ts': run_ts.isoformat(), 'stats': stats}, indent=2))

if __name__ == '__main__':
    main()
