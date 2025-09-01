from pathlib import Path
BASE_DIR=Path(__file__).resolve().parents[2]
DATA_DIR=BASE_DIR/'data'
OUTPUT_DIR=DATA_DIR/'output'
LOGS_DIR=DATA_DIR/'logs'

def ensure_dirs():
  for d in [DATA_DIR, OUTPUT_DIR, LOGS_DIR]: d.mkdir(parents=True, exist_ok=True)
