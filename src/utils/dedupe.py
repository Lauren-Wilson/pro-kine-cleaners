import pandas as pd

def dedupe(df:pd.DataFrame)->pd.DataFrame:
  df=df.copy(); df['key_contact']=df['contact_method'].fillna(''); df['key_secondary']=(df['post_url'].fillna('')+'|'+df['full_name_or_handle'].fillna('')+'|'+df['location_text'].fillna(''))
  df['posted_at']=pd.to_datetime(df['posted_at'], errors='coerce', utc=True)
  def keep_latest(g):
    g=g.sort_values(by=['posted_at'], ascending=False, na_position='last'); b=g.iloc[0].copy()
    for col in df.columns:
      if col in ['key_contact','key_secondary','match_score']: continue
      if pd.isna(b[col]) or b[col] in ('', None):
        for _, r in g.iterrows():
          v=r[col]
          if isinstance(v,str) and v.strip(): b[col]=v; break
    return b
  wc=df[df['key_contact'].astype(bool)]; woc=df[~df.index.isin(wc.index)]
  d1=(wc.groupby('key_contact', as_index=False).apply(keep_latest).reset_index(drop=True))
  d2=(woc.groupby('key_secondary', as_index=False).apply(keep_latest).reset_index(drop=True))
  out=pd.concat([d1,d2], ignore_index=True)
  return out.drop(columns=['key_contact','key_secondary'], errors='ignore')
