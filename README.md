# Práctica 1 — Extractor y Análisis de Datos Bursátiles
Por Alonso Díaz Tapia

Master en IA aplicada a los mercados financieros 

Noviembre 2025

##  Descripción general

Este proyecto implementa un **sistema modular en Python** diseñado para **extraer, estandarizar y analizar información bursátil** desde múltiples fuentes de datos online.  
Además, permite construir una **cartera de inversión simulada** y realizar una **simulación Monte Carlo** basada en un modelo logarítmico (GBM), para proyectar su evolución futura bajo distintos escenarios de rentabilidad y volatilidad.

El propósito de esta práctica es fomentar el desarrollo de **buenas prácticas de programación**, como la **modularidad**, el **uso de clases y herencia**, la **abstracción de fuentes de datos** y la **reutilización del código**.

##  Estructura del proyecto

```
Practica-1/
├── src/
│   ├── sources/
│   │   ├── __init__.py
│   │   ├── base_source.py        # Clase base abstracta común para todas las fuentes
│   │   ├── yahoo_source.py       # Fuente de datos bursátiles (Yahoo Finance API)
│   │   ├── fred_source.py        # Fuente de datos macroeconómicos (FRED API)
│   │   └── ibkr_source.py        # Fuente de datos simulados (Interactive Brokers simulada)
│   ├── data_models.py            # Clases PricePoint y PriceSeries
│   ├── portfolio.py              # Clase Portfolio: Monte Carlo, report y gráficos
│   ├── manager.py                # DataManager: coordina fuentes y obtiene PriceSeries
│   └── utils_stats.py            # Funciones estadísticas auxiliares
│
├── main.py                       # Punto de entrada del programa
├── requirements.txt              # Dependencias del entorno Python
└── docs/
    └── arquitectura_fossflow.png # Diagrama de arquitectura del proyecto
```

## Diagrama de arquitectura
La siguiente imagen muestra la estructura general del proyecto, incluyendo herencias y dependencias entre clases:

![Arquitectura del proyecto](docs/arquitectura_fossflow.png)

## Arquitectura del sistema

El diseño sigue una arquitectura modular en capas:

| Capa | Componente | Función |
|------|-------------|----------|
| **Fuentes (Sources)** | `YahooSource`, `FREDSource`, `IBKRSource` | Obtienen datos desde APIs o simulaciones. |
| **Clase Base** | `BaseSource` | Define la interfaz común `get_price_history()`. |
| **Gestión** | `DataManager` | Coordina las fuentes y devuelve objetos `PriceSeries` estandarizados. |
| **Modelos de datos** | `PriceSeries` y `PricePoint` | Representan series temporales y observaciones diarias. |
| **Análisis** | `Portfolio` | Agrupa activos, simula evolución (Monte Carlo) y genera reportes visuales. |
| **Interfaz** | `main.py` | Punto de entrada que orquesta todo el flujo. |

##  Instalación y ejecución

### 1️. Clonar el repositorio
```bash
git clone https://github.com/usuario/Practica-1.git
cd Practica-1
```
### 2️. Instalar dependencias
```bash
pip install -r requirements.txt
```
### 3️. Ejecutar el programa principal
```bash
python main.py
```

## Fuentes de datos

### Yahoo Finance
- Descarga datos históricos de precios de acciones e índices.
- Formato original: DataFrame (pandas).
- Salida estandarizada: `PriceSeries`.

### FRED (Federal Reserve Economic Data)
- Obtiene series macroeconómicas (PIB, inflación, tasas, etc.).
- Requiere API Key gratuita.
- Compatible con `BaseSource` y formato `PriceSeries`.

### IBKRSource (Simulada)
- Emula el comportamiento de un broker real.
- No requiere conexión a Internet.
- Genera precios sintéticos con un crecimiento compuesto diario (~0.2%).
- Implementa un bucle temporal `while` que recorre cada fecha del rango solicitado.

---

## Construcción de la cartera

Las carteras se componen de varios activos (`PriceSeries`) ponderados por sus pesos relativos.  
Ejemplo de creación:

```python
portfolio = Portfolio({
    "AAPL": {"series": series_aapl, "weight": 0.25},
    "MSFT": {"series": series_msft, "weight": 0.25},
    "AMZN": {"series": series_amzn, "weight": 0.25},
    "GOOG": {"series": series_goog, "weight": 0.25}
})
```

El método `Portfolio.last_portfolio_value()` calcula el valor total actual de la cartera combinando los precios más recientes de cada activo.

---

## Simulación de Monte Carlo

### Descripción teórica

El método `monte_carlo()` implementa un **modelo logarítmico de crecimiento estocástico (Geometric Brownian Motion)**.  
Cada trayectoria se construye mediante la fórmula:

\$
V_{t+1} = V_t 	imes e^{r_t}, \quad r_t = \mu + \sigma z_t
\$

donde:
- \( \mu \): rentabilidad media diaria esperada.
- \( \sigma \): volatilidad diaria.
- \( z_t \): variable aleatoria N(0,1).

### ⚙️ Implementación

- **Entrada:** días a simular, número de trayectorias, valor inicial.  
- **Salida:** lista de trayectorias simuladas.  
- **Modelo:** log-based (precios siempre positivos).  

### 🧮 Ejemplo de uso
```python
paths = portfolio.monte_carlo(days=60, n_paths=500)
```

Cada trayectoria se almacena como una lista de valores `[v0, v1, ..., vT]`.

---

## 📈 Reporte e interpretación de resultados

### Método `.report()`
Genera un informe en formato **Markdown**, mostrando:
- Rentabilidad media y volatilidad diaria.
- Resultados de la simulación (p5, p50, p95).
- Advertencias si hay datos insuficientes.

Ejemplo de salida:
```
## Informe de la cartera
- Activos: 10
- Rentabilidad diaria esperada: 0.12%
- Desviación típica: 1.45%
- Rentabilidad anualizada: 9.2%
### Resultados Monte Carlo
- Percentil 5%: 92.1
- Mediana (p50): 103.8
- Percentil 95%: 117.6
```

### Método `.plots_report()`
Visualiza los resultados del Monte Carlo, mostrando:
- Trayectorias simuladas.
- Línea media de evolución esperada.

Ejemplo:
```python
portfolio.plots_report(days=30, n_paths=200)
```

---

## Características adicionales

- Limpieza automática de datos en `PriceSeries`.
- Cálculo de estadísticas básicas al instanciar las clases.
- Estándar unificado de salida (`PriceSeries` → `PricePoint`).
- Completamente reproducible y “plug-and-play”.

---

## Buenas prácticas aplicadas

- Estructura modular y jerárquica (arquitectura limpia).
- Uso de `DataClasses` para objetos inmutables y claros.
- Herencia controlada (`BaseSource` como plantilla común).
- Nombres descriptivos y tipado estricto (`List[PriceSeries]`, `Optional[float]`).

---

## Uso de GitHub

El desarrollo se ha gestionado íntegramente en GitHub:
- Control de versiones mediante commits progresivos.
- Subida modular de notebooks y scripts.
- Integración de `requirements.txt` y `docs/`.
- Entorno replicable para evaluación académica.
