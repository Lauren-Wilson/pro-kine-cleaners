import logging
from logging.handlers import RotatingFileHandler

def build_logger(p):
  lg=logging.getLogger('cleaner_pipeline'); lg.setLevel(logging.INFO); lg.handlers=[]
  fh=RotatingFileHandler(p, maxBytes=2_000_000, backupCount=3); fh.setLevel(logging.INFO); fh.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
  ch=logging.StreamHandler(); ch.setLevel(logging.INFO); ch.setFormatter(logging.Formatter('%(levelname)s | %(message)s'))
  lg.addHandler(fh); lg.addHandler(ch); return lg
