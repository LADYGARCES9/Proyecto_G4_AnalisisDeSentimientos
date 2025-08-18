#  Proyecto G4 - Análisis de Sentimientos en Reseñas de Amazon

Este proyecto es una **Plataforma de Análisis de Sentimientos en Tiempo Real para e-commerce**, desarrollada por el grupo **G4**.

Nuestro objetivo es permitir a las empresas monitorear automáticamente reseñas de productos y menciones en redes sociales, identificando rápidamente **problemas** y **oportunidades de mejora**.

Utilizamos técnicas avanzadas de **Procesamiento de Lenguaje Natural (NLP)** para analizar texto, detectar urgencias, clasificar sentimientos y generar respuestas automáticas.

---

##  Características Principales

- **Análisis de Sentimientos:** Clasificación en positivo, negativo o neutro.
- **ABSA (Aspect-Based Sentiment Analysis):** Evaluación por aspectos (precio, calidad, envío...).
- **Detección de Urgencia:** Clasificación automática de nivel de urgencia.
- **Generación Automática de Respuestas:** IA generativa para sugerir respuestas a clientes.
- **Procesamiento en Tiempo Real:** Flujo continuo desde APIs o scraping.

---

##  Instalación

### 1. Clona este repositorio

```bash
git clone https://github.com/tu_usuario/Proyecto_G4_AnalisisDeSentimientos.git
cd Proyecto_G4_AnalisisDeSentimientos
```

### 2. Crea y activa un entorno virtual

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instala las dependencias

Dependiendo del módulo que vayas a ejecutar, instala sus requerimientos:

```bash
# Para la API
pip install -r api/requirements.txt

# Para el Dashboard
pip install -r dashboard/requirements.txt

# Para el modelo ABSA
pip install -r src/dockers/absa/requirements.txt

# Para el baseline
pip install -r src/dockers/baseline/requirements.txt
```

---

##  Cómo Ejecutar el Proyecto

###  API (FastAPI)

```bash
cd api
uvicorn app:app --reload
```

Abre en tu navegador: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

###  Dashboard

```bash
cd dashboard
python app_dashboard.py
```

---

## Cómo Ejecutar los Tests

```bash
python run_tests.py
```

Esto ejecuta las pruebas en `tests/` y muestra un resumen de resultados.

---

## Estructura del Proyecto

```bash
├── README.md
├── .gitignore
├── api/                    # API FastAPI
│   ├── src/utils/          # Funciones auxiliares
├── dashboard/              # Interfaz Dash
│   ├── src/                # Funciones auxiliares
├── data/
│   ├── raw/                # Datos originales
│   ├── processed/          # Datos limpios
│   └── external/           # Fuentes externas
├── docs/                   # Documentación y PDFs
│   ├── images/             # Diagramas, capturas del dashboard, visualizaciones
│   ├── reports/            # Reportes generados en PDF o HTML
├── models/
│   ├── trained_models/     # Modelos entrenados
│   └── model_configs/      # Configs JSON
├── notebooks/
│   ├── exploratory/        # EDA
│   ├── modeling/           # Modelado
│   └── evaluation/         # Evaluación
├── src/
│   ├── docker/             # Dockerfiles y contenerización
│   └── utils/              # Funciones auxiliares
├── tests/                  # Unit tests
```

---

## Colaboradores del Proyecto

- David Francisco Alvarez Alvarez  
- Marcelo Xavier Castillo Valverde  
- Alejandro Sebastian Castro Nasevilla  
- Lady Anahi Garces Velasco  
- Daniela Estefania Pezantez Chimbo  
- María Mercedes Vera Letamendi

---

## Licencia

Este proyecto está bajo la licencia **UEES**.
