from pathlib import Path

def format_short_dm(row):
  name=(row.get('full_name_or_handle') or 'there').split()[0]; intent=row.get('intent_signal') or 'taking on new clients'; services=row.get('service_types') or 'standard/deep/move-out cleans'; loc=row.get('location_text') or 'San Antonio'
  msg=f"Hi {name}! Saw you’re {intent} in {loc}. We run a local cleaning business focused on {services}. If you’re seeking new clients, we’d love to partner on referrals. No pressure — totally opt-in. Would you like to chat?"
  return msg[:450]

def format_email(row):
  loc=row.get('location_text') or 'San Antonio'; services=row.get('service_types') or 'standard, deep, and move-out cleans'; subject=f'San Antonio: Cleaner referrals ({services})'
  body=(f"Hi {row.get('full_name_or_handle') or 'there'},\n\n" f"I came across your public post indicating you’re {row.get('intent_signal') or 'accepting new clients'} in {loc}. " f"We’re a local cleaning company that often has overflow demand and we partner with independent cleaners. " f"Based on your listing (services: {services}), we’d love to explore sending clients your way — only if you’re currently seeking new clients.\n\n" f"If you’re open to a quick chat, I can share details (areas served, rates, and scheduling fit). " f"If not, no worries at all — thanks for your time!\n\n" f"Best,\nYour Name\nYour Business Name | San Antonio, TX\n")
  return subject, body

def write_messages_markdown(df, out_path:Path):
  with open(out_path,'w',encoding='utf-8') as f:
    for _,row in df.iterrows():
      subject, body = format_email(row)
      f.write(f"## {row.get('full_name_or_handle') or row.get('post_url')}\n\n**Platform:** {row.get('platform')}\n\n**Short DM:** {format_short_dm(row)}\n\n**Email Subject:** {subject}\n\n**Email Body:**\n\n{body}\n\n---\n\n")
