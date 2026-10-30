import re, unicodedata
def norm(t):
    t = unicodedata.normalize('NFC', t).lower()
    t = re.sub(r"[’‘'`\"“”„]", "", t)   # quotes/apostrophes vanish
    t = re.sub(r"[^\w\s]|_", " ", t, flags=re.UNICODE)            # other punctuation -> space
    return re.sub(r"\s+", " ", t).strip()
