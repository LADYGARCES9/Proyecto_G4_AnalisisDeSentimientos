"""
metrics_aggregator.py

Agrega métricas desde data/evaluation/**/metrics.json y genera un resumen en
docs/reports/metrics_summary.csv

- Usable como módulo:
    from src.utils.metrics_aggregator import get_metrics_summary, save_metrics_summary
    df = get_metrics_summary()
    out_path = save_metrics_summary(df)

- Usable como script:
    python -m src.utils.metrics_aggregator
o, si tu entorno no reconoce el paquete:
    python src/utils/metrics_aggregator.py
"""

from __future__ import annotations
from pathlib import Path
import json
import pandas as pd
from typing import List, Dict, Any, Optional

# --- Import robusto de rutas (funciona dentro/fuera de paquete) ---
try:
    # cuando se ejecuta como paquete: python -m src.utils.metrics_aggregator
    from src.utils.config_rutas import reports_dir as _reports_dir
    from src.utils.config_rutas import get_project_dir as _get_project_dir
except Exception:
    # cuando se ejecuta como script directo
    import sys
    THIS = Path(__file__).resolve()
    sys.path.append(str(THIS.parents[1]))  # añade .../src al sys.path
    try:
        from utils.config_rutas import reports_dir as _reports_dir
        from utils.config_rutas import get_project_dir as _get_project_dir
    except Exception:
        # fallback: deducir proyecto por dos niveles arriba de src/
        _get_project_dir = lambda: Path(__file__).resolve().parents[3]
        _reports_dir = _get_project_dir() / "docs" / "reports"

# Directorios base
PROJECT_DIR: Path = Path(_get_project_dir()).resolve()
EVAL_DIR: Path = (PROJECT_DIR / "data" / "evaluation").resolve()
REPORTS_DIR: Path = Path(_reports_dir).resolve()
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def _safe_json_read(path: Path) -> Optional[Dict[str, Any]]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _collect_metrics_json(eval_dir: Path) -> List[Path]:
    """Encuentra todos los metrics.json dentro de data/evaluation/**/"""
    return list(eval_dir.rglob("metrics.json"))


def _flatten_dict(d: Dict[str, Any], parent_key: str = "", sep: str = ".") -> Dict[str, Any]:
    """Aplana dicts anidados para que entren bien en CSV."""
    items = []
    for k, v in (d or {}).items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(_flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def get_metrics_summary(eval_dir: Path = EVAL_DIR) -> pd.DataFrame:
    """
    Lee todos los metrics.json y devuelve un DataFrame consolidado.
    Columnas básicas:
      - run_path: ruta relativa a data/evaluation
      - run_name: primer componente de la ruta (p.ej., '02_baseline' o similar si lo usas)
      - ... columnas derivadas de metrics.json (aplanadas)
    """
    rows: List[Dict[str, Any]] = []
    json_paths = _collect_metrics_json(eval_dir)

    for p in json_paths:
        rel = str(p.parent.relative_to(eval_dir)) if p.parent.is_relative_to(eval_dir) else str(p.parent)
        data = _safe_json_read(p)
        if data is None:
            rows.append({"run_path": rel, "error": f"No se pudo leer {p}"})
            continue

        flat = _flatten_dict(data)
        row: Dict[str, Any] = {"run_path": rel}
        # run_name: primer segmento de la ruta (útil si llevas subcarpetas por notebook)
        try:
            row["run_name"] = rel.split("/", 1)[0]
        except Exception:
            row["run_name"] = rel

        # Campos comunes que suelen existir
        # (si no existen, no pasa nada; el aplanado ya tomó lo que haya)
        for k in ["accuracy", "macro_f1", "f1", "precision", "recall"]:
            if k in data and isinstance(data[k], (int, float)):
                row[k] = float(data[k])

        # Mezcla todo lo aplanado
        for k, v in flat.items():
            # Evita sobreescrituras tontas: si ya existe clave simple, respeta
            if k not in row:
                row[k] = v

        rows.append(row)

    df = pd.DataFrame(rows)
    # Ordena columnas: primero identificadores y métricas clave
    key_cols = [c for c in ["run_path", "run_name", "accuracy", "macro_f1", "precision", "recall"] if c in df.columns]
    other_cols = [c for c in df.columns if c not in key_cols]
    df = df[key_cols + other_cols]
    return df


def save_metrics_summary(df: pd.DataFrame, out_name: str = "metrics_summary.csv") -> Path:
    """Guarda el DataFrame en docs/reports/<out_name> y devuelve la ruta."""
    out = REPORTS_DIR / out_name
    df.to_csv(out, index=False)
    return out


def main() -> None:
    print(f"[i] Proyecto: {PROJECT_DIR}")
    print(f"[i] Buscando métricas en: {EVAL_DIR}")
    df = get_metrics_summary(EVAL_DIR)
    if df.empty:
        print("[!] No se encontraron metrics.json en data/evaluation/**/")
    else:
        out = save_metrics_summary(df)
        print(f"[✓] Resumen generado: {out}")
        # Vista previa corta
        with pd.option_context("display.max_columns", 20):
            print(df.head(10))


if __name__ == "__main__":
    main()
