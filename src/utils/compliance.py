import urllib.robotparser as urobot
from urllib.parse import urlparse
_UA='cleaner-finder-bot/0.1 (+compliance)'

def is_allowed(url:str)->bool:
  try:
    p=urlparse(url); robots=f"{p.scheme}://{p.netloc}/robots.txt"; rp=urobot.RobotFileParser(); rp.set_url(robots); rp.read(); return rp.can_fetch(_UA, url)
  except Exception:
    return False
