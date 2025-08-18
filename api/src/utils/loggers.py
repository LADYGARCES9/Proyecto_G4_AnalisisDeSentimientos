from pathlib import Path
from datetime import datetime, timezone
import pandas as pd

def _utc_iso() -> str:
    """Devuelve timestamp UTC en ISO-8601 con 'Z'."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

def append_result(csv_path: Path, text: str, sentiment: str, urgency: str, aspects: str = ""):
    """Agrega 1 fila a results_log.csv con ts (UTC) y normaliza campos."""
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "ts": _utc_iso(),
        "text": text,
        "sentiment": str(sentiment).lower().strip(),
        "urgency": str(urgency).lower().strip(),
        "aspects": aspects or ""
    }
    df = pd.DataFrame([row])
    header = not csv_path.exists()
    df.to_csv(csv_path, mode="a", index=False, header=header, encoding="utf-8")

def append_alert(csv_path: Path, text: str, sentiment: str, urgency: str, reason: str = "", aspects: str = ""):
    """Agrega 1 fila a alerts_log.csv con ts (UTC) y normaliza campos."""
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "ts": _utc_iso(),
        "text": text,
        "sentiment": str(sentiment).lower().strip(),
        "urgency": str(urgency).lower().strip(),
        "reason": reason,
        "aspects": aspects or ""
    }
    df = pd.DataFrame([row])
    header = not csv_path.exists()
    df.to_csv(csv_path, mode="a", index=False, header=header, encoding="utf-8")
