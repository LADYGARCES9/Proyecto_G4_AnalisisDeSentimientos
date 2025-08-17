
from pathlib import Path

#Ruta base del proyecto 
PROJECT = Path("/content/drive/MyDrive/Proyecto_Analisis_de_Sentimientos_G4")

#Carpetas 
data_dir      = PROJECT / "data"
raw_dir       = data_dir / "raw"
processed_dir = data_dir / "processed"
eval_dir      = data_dir / "evaluation"

models_root   = PROJECT / "models"
models_dir    = models_root / "trained_models"
configs_dir   = models_root / "model_configs"

docs_dir      = PROJECT / "docs"
images_dir    = docs_dir / "images"
reports_dir   = docs_dir / "reports"

notebooks_dir = PROJECT / "notebooks"
nb_model_dir  = notebooks_dir / "modeling"

# Crear si no existen
for d in [data_dir, raw_dir, processed_dir, eval_dir,
          models_root, models_dir, configs_dir,
          docs_dir, images_dir, reports_dir,
          notebooks_dir, nb_model_dir]:
    d.mkdir(parents=True, exist_ok=True)

# Helpers de carpeta, funciones auxiliares
def get_project_dir():   return PROJECT
def get_eval_dir():      return eval_dir
def get_models_dir():    return models_dir
def get_images_dir():    return images_dir
def get_reports_dir():   return reports_dir
def get_processed_dir(): return processed_dir
def get_raw_dir():       return raw_dir
