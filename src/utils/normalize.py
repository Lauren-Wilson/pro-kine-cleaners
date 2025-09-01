import re, phonenumbers

def normalize_phone(raw:str)->str:
  if not raw: return ''
  try:
    num=phonenumbers.parse(raw,'US')
    if phonenumbers.is_valid_number(num):
      return phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.E164)
  except Exception: pass
  digits=re.sub(r'\D','',raw); return f'+1{digits}' if len(digits)==10 else ''

def normalize_email(raw:str)->str:
  if not raw: return ''
  raw=raw.strip().lower();
  import re
  return raw if re.match(r'^[a-z0-9_.+-]+@[a-z0-9-]+\.[a-z0-9-.]+$', raw) else ''

def clean_handle(raw:str)->str:
  return (raw or '').strip().lower()
