import pandas as pd
import re
import unicodedata
import base64
from io import BytesIO

ALIASES = {
    "ELGEYO": "ELGEYO-MARAKWET",
    "MURANGA": "MURANG'A",
    "TAITA TAVETA": "TAITA-TAVETA",
    "THARAKA NITHI": "THARAKA-NITHI",
    "HOMA BAY": "HOMA BAY",
    "UASIN-GISHU": "UASIN GISHU",
    "TRANS-NZOIA": "TRANS NZOIA",
    "TANA RIVER": "TANA RIVER",
    "NAIROBI CITY": "NAIROBI",
}

def to_key(x):
    if pd.isna(x): return ""
    u = str(x).strip().upper()
    return ALIASES.get(u, u)

def get_first_present(d: dict, keys: list[str], default=None):
    for k in keys:
        if k in d and d[k]:
            return d[k]
    return default
def slugify(s: str) -> str:
    s = str(s)
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
    s = re.sub(r"[''`]", "", s)
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
    return s


def pick_index(options, value, default_index=0):
    try:
        return options.index(value) if value in options else default_index
    except Exception:
        return default_index
    


def base64_to_image(img_base64: str) -> BytesIO:
    """Convert base64 string to BytesIO for Streamlit image display."""
    return BytesIO(base64.b64decode(img_base64))

def parse_json_payload(payload: dict):
    """Split JSON payload into text/image instructions and product info."""
    output_type = payload.get("output_type")
    image_prompt = payload.get("image_instructions")
    text_prompt = payload.get("text_instructions")
    
    product_info = {k: v for k, v in payload.items() if k not in {"output_type", "image_instructions", "text_instructions"}}
    return output_type, image_prompt, text_prompt, product_info    