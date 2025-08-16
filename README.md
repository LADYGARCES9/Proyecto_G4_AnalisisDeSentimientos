**DESCRIPCIÓN DEL PROYECTO**

Este proyecto es una Plataforma de Análisis de Sentimientos en Tiempo Real para e-commerce. Nuestro objetivo principal es ayudar a las empresas a monitorear automáticamente las reseñas de productos y las menciones en redes sociales, identificando rápidamente problemas de calidad y oportunidades de mejora.

l sistema utiliza modelos de Procesamiento del Lenguaje Natural (NLP) para procesar grandes volúmenes de texto en tiempo real, permitiendo a las empresas actuar de manera proactiva en su servicio al cliente y estrategia de producto.

**CARATERÍSTICAS PRINCIPALES**

- Análisis de Sentimientos: Clasifica el texto en positivo, negativo o neutro.

- Análisis de Sentimientos Basado en Aspectos (ABSA): Identifica y evalúa el sentimiento sobre aspectos específicos del producto o servicio (ej. precio, calidad, envío).

- Detección de Urgencia: Clasifica los comentarios negativos o problemas según su nivel de urgencia para priorizar las acciones.

- Generación de Respuestas Automáticas: Utiliza modelos de IA generativa para sugerir o crear respuestas automáticas a los comentarios.

- Procesamiento en Tiempo Real: Capaz de procesar flujos de datos continuos desde diversas fuentes (APIs, web scraping).

**ESTRUCTURA DEL PROYECTO**
```
├── README.md
├── requirements.txt
├── setup.py
├── data/
│   ├── raw/                # Datos originales (Amazon Product Reviews)
│   ├── processed/          # Datos limpios y listos para el entrenamiento
│   └── external/           # Datos de terceros o scrapings
├── src/
│   ├── data/               # Scripts de procesamiento de datos y feature engineering
│   ├── models/             # Scripts para el entrenamiento y evaluación de modelos
│   ├── features/           # Funciones para la extracción de features
│   ├── visualization/      # Scripts para generar gráficos y reportes
│   └── utils/              # Funciones de utilidad
├── models/
│   ├── trained_models/     # Modelos pre-entrenados listos para su uso
│   └── model_configs/      # Archivos de configuración de los modelos
├── notebooks/
│   ├── exploratory/        # Análisis exploratorio de datos (EDA)
│   ├── modeling/           # Pruebas y experimentos de modelos
│   └── evaluation/         # Análisis del rendimiento de los modelos
├── api/
│   ├── app.py              # Aplicación principal de la API con FastAPI
│   ├── routes/             # Rutas de la API (endpoints)
│   └── schemas/            # Definiciones de datos para la API
├── dashboard/              # Código para el dashboard de visualización
├── tests/                  # Pruebas unitarias y de integración
├── docs/                   # Documentación adicional del proyecto
└── docker/                 # Archivos para la contenerización del proyecto
```
