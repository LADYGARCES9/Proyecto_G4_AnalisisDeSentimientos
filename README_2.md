**Proyecto G4 - Análisis de Sentimientos en Reseñas de Amazon**

Este proyecto es una **Plataforma de Análisis de Sentimientos en Tiempo Real para e-commerce**, desarrollada por el grupo G4.  
Nuestro objetivo es permitir a las empresas monitorear automáticamente reseñas de productos y menciones en redes sociales, identificando rápidamente problemas y oportunidades.

Utilizamos técnicas avanzadas de **Procesamiento del Lenguaje Natural (NLP)** para analizar texto, detectar urgencias, clasificar sentimientos y generar respuestas automáticas.

---

**Características Principales**

- **Análisis de Sentimientos:** Clasificación en positivo, negativo o neutro.
- **ABSA (Aspect-Based Sentiment Analysis):** Evaluación por aspectos (precio, calidad, envío...).
- **Detección de Urgencia:** Clasificación automática de nivel de urgencia.
- **Generación Automática de Respuestas:** IA generativa para sugerir respuestas a clientes.
- **Procesamiento en Tiempo Real:** Flujo continuo desde APIs o scraping.

---

**Instalación**

1. Clona este repositorio:

   ```bash
   git clone https://github.com/tu_usuario/Proyecto_G4_AnalisisDeSentimientos.git
   cd Proyecto_G4_AnalisisDeSentimientos
   ```

2. Crea y activa un entorno virtual:

   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. Instala dependencias:

   ```bash
   pip install -r requirements.txt
   ```

---

**Cómo Ejecutar el Proyecto**

***API (FastAPI)***

```bash
cd api
uvicorn app:app --reload
```

Abre en tu navegador:  
**http://127.0.0.1:8000/docs**

***Dashboard (Dash)***

```bash
cd dashboard
python app_dashboard.py
```

---

**Cómo Ejecutar los Tests**

```bash
python run_tests.py
```

Esto ejecuta las pruebas en `tests/` y muestra un resumen de resultados.

---

**Estructura del Proyecto**

```
├── README.md
├── requirements.txt
├── run_tests.py
├── data/
│   ├── raw/                # Datos originales
│   ├── processed/          # Datos limpios
│   └── external/           # Fuentes externas
├── src/
│   ├── data/               # Limpieza y transformación
│   ├── models/             # Entrenamiento y predicción
│   ├── utils/              # Funciones auxiliares
│   └── visualization/      # Gráficas y reportes
├── models/
│   ├── trained_models/     # Modelos entrenados
│   └── model_configs/      # Configs JSON
├── notebooks/
│   ├── exploratory/        # EDA
│   ├── modeling/           # Modelado
│   └── evaluation/         # Evaluación
├── api/                    # API FastAPI
├── dashboard/              # Interfaz Dash
├── tests/                  # Unit tests
├── docs/                   # Documentación y PDFs
└── docker/                 # Dockerfiles y contenerización
```

---

**Colaboradores del Proyecto**

- David Francisco Alvarez Alvarez  
- Marcelo Xavier Castillo Valverde  
- Alejandro Sebastian Castro Nasevilla  
- Lady Anahi Garces Velasco  
- Daniela Estefania Pezantez Chimbo  
- María Mercedes Vera Letamendi

---

**Mejoras Futuras**

- [ ] Autenticación de usuarios en la API
- [ ] Despliegue en la nube (Render / Heroku)
- [ ] Incluir más aspectos en ABSA
- [ ] Añadir pruebas automatizadas para la API
- [ ] Mejorar la documentación técnica

---

**Licencia**

Este proyecto está bajo la licencia MIT.
