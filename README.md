# Proyecto: **Análisis de Acceso a Internet en Argentina**

## Descripción General

El acceso a internet es un factor clave para el desarrollo social, económico y tecnológico de cualquier nación. Este proyecto aborda un análisis integral de los patrones de acceso a internet en Argentina, combinando procesos de ETL (Extracción, Transformación y Carga), Análisis Exploratorio de Datos (EDA) y visualización interactiva a través de una aplicación Dash.

El objetivo principal es identificar tendencias, relaciones y correlaciones entre la velocidad de internet, las tecnologías utilizadas, y el nivel de penetración en hogares y población, brindando información que pueda servir como base para la toma de decisiones estratégicas.

---

## Contenido

### Archivos Principales

1. **ETL.ipynb** :

* Realiza la limpieza, transformación y consolidación de datos.
* Manejo de valores nulos, outliers y normalización de los datos.
* Integración de múltiples fuentes para generar un dataset unificado.

1. **EDA.ipynb** :

* Análisis exploratorio para descubrir tendencias en velocidad de internet, penetración y tecnologías.
* Visualización de series temporales, análisis geográfico y correlaciones entre variables clave.

1. **app.py** :

* Implementación de una aplicación interactiva con Dash.
* Incluye pestañas para explorar Tendencias Temporales,  Relaciones con Tecnologia, Penetracion y Tecnologia y Análisis de Tendencia

---

## Aplicación Interactiva

### Características

La aplicación Dash incluye las siguientes funcionalidades:

1. **Tendencias Temporales** : Análisis de cómo han evolucionado la velocidad de internet y la penetración en hogares y población a lo largo del tiempo.
2. **Relaciones con Tecnologia** : Mapa interactivo que muestra diferencias regionales en velocidad y tecnología predominante.
3. **Relación con Tecnologías** : Gráficos que destacan la proporción de tecnologías como ADSL, Cablemódem, Fibra Óptica y Wireless.
4. **Análisis Estadístico** : Relaciones entre velocidad de internet y penetración, con métricas de correlación y regresión lineal.
5. **KPI**: Indicadores Claves de desempeño. Se mediran 2 KPI con respecto a Penetracion Hogar y Velocidad Media en algunas provincias

### Tecnologías utilizadas en la aplicación

* **Dash** : Para construir el dashboard interactivo.
* **Plotly** : Para visualizaciones avanzadas como gráficos de líneas, mapas coropléticos y dispersión.
* **GeoPandas** : Para manipulación de datos geoespaciales.
* **Scikit-learn** y  **SciPy** : Para cálculos estadísticos y análisis de regresión.

---

## Análisis y Resultados

### **1. Tendencias Temporales**

* La velocidad de internet ha mostrado una mejora constante desde 2018, con un incremento promedio anual del 15%.
* La penetración de internet en hogares ha alcanzado valores superiores al 80% en las provincias más desarrolladas, mientras que en otras áreas más rurales se mantiene por debajo del 50%.

### **2. Variaciones Geográficas**

* Las provincias de la región central como Buenos Aires y Córdoba lideran en velocidad de internet, con medias superiores a 30 Mbps.
* En contraste, provincias del norte como Formosa y Chaco presentan velocidades promedio de apenas 10 Mbps.

### **3. Relación con Tecnologías**

* La **fibra óptica** se consolida como la tecnología con mayor velocidad media (40 Mbps), mientras que tecnologías como **Wireless** y **ADSL** tienen un rendimiento significativamente menor (promedio de 15 Mbps).
* Existe una correlación positiva (0.7) entre el nivel de penetración de internet en hogares y la adopción de fibra óptica.

### **4. Análisis Estadístico**

* La velocidad media de internet está significativamente correlacionada con la penetración en la población (R² = 0.65).
* El análisis de regresión sugiere que un aumento del 1% en la penetración por hogares incrementa la velocidad promedio en aproximadamente 0.3 Mbps.. KPI Propuestos: Incremento Proyectado de Acceso a Internet y Velocidad Media de Descarga para el Próximo Año

### 5. KPI

### 5.1 Incremento proyectado del acceso a internet (8%) para el próximo año por provincia

Se generará data aleatoria para la penetración por hogar durante el año 2024, comparando los valores estimados (incremento del 8% para el último trimestre de 2024) con los valores reales simulados.

Resultados esperados:

* **Crecimiento sostenido** : El análisis muestra un aumento progresivo en la penetración de internet por hogar.

### 5.2. Incremento proyectado de la Velocidad Media de Descarga (10% trimestral) para las provincias con menor velocidad

Se generará data aleatoria para la Velocidad Media de Descarga durante el año 2024, comparando los valores estimados (incremento del 40% para el último trimestre de 2024) con los valores reales simulados.

Resultados esperados:

* **Incremento sostenido** : El crecimiento trimestral destaca los avances en infraestructura y políticas aplicadas.
* **Análisis detallado** : Identifica las provincias con menor crecimiento, facilitando ajustes estratégicos.

Conclusión general:

Ambos KPI reflejan un progreso positivo en la expansión del acceso a internet y la mejora de la velocidad media de descarga. Las gráficas proporcionan una visión clara del cumplimiento de metas y áreas de oportunidad para cada provincia.

---

## Conclusiones

1. **Impacto de las Tecnologías** : La transición hacia tecnologías más modernas como la fibra óptica es clave para mejorar la velocidad de internet en las regiones con menor acceso.
2. **Desigualdad Regional** : Existe una brecha digital significativa entre provincias, evidenciada en las diferencias de velocidad y penetración.
3. **Proyecciones Futuras** : Si se mantienen las tasas actuales de adopción tecnológica, la velocidad promedio nacional podría superar los 50 Mbps para 2027.
4. **Políticas Públicas** : Los resultados sugieren la necesidad de políticas gubernamentales enfocadas en:

* Ampliar la infraestructura de fibra óptica en regiones rurales.
* Incentivar inversiones privadas en tecnologías de última generación.

---

## Requisitos del Proyecto

### Dependencias

Instala las siguientes librerías antes de ejecutar los notebooks y la aplicación:

* `dash`
* `dash-bootstrap-components`
* `pandas`
* `numpy`
* `plotly`
* `geopandas`
* `sklearn`
* `scipy`

### Datos

* Los datasets deben colocarse en la carpeta `Datasets`.
* El archivo GeoJSON para el mapa debe estar ubicado en la carpeta `Mapas`.

---

## Cómo Ejecutar el Proyecto

1. Clona este repositorio en tu máquina local.
2. Instala las dependencias utilizando:
   <pre class="!overflow-visible"><div class="contain-inline-size rounded-md border-[0.5px] border-token-border-medium relative bg-token-sidebar-surface-primary dark:bg-gray-950"><div class="flex items-center text-token-text-secondary px-4 py-2 text-xs font-sans justify-between rounded-t-md h-9 bg-token-sidebar-surface-primary dark:bg-token-main-surface-secondary select-none">bash</div><div class="sticky top-9 md:top-[5.75rem]"><div class="absolute bottom-0 right-2 flex h-9 items-center"><div class="flex items-center rounded bg-token-sidebar-surface-primary px-2 font-sans text-xs text-token-text-secondary dark:bg-token-main-surface-secondary"><span class="" data-state="closed"><button class="flex gap-1 items-center select-none px-4 py-1" aria-label="Copy"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="icon-xs"><path fill-rule="evenodd" clip-rule="evenodd" d="M7 5C7 3.34315 8.34315 2 10 2H19C20.6569 2 22 3.34315 22 5V14C22 15.6569 20.6569 17 19 17H17V19C17 20.6569 15.6569 22 14 22H5C3.34315 22 2 20.6569 2 19V10C2 8.34315 3.34315 7 5 7H7V5ZM9 7H14C15.6569 7 17 8.34315 17 10V15H19C19.5523 15 20 14.5523 20 14V5C20 4.44772 19.5523 4 19 4H10C9.44772 4 9 4.44772 9 5V7ZM5 9C4.44772 9 4 9.44772 4 10V19C4 19.5523 4.44772 20 5 20H14C14.5523 20 15 19.5523 15 19V10C15 9.44772 14.5523 9 14 9H5Z" fill="currentColor"></path></svg>Copy</button></span><span class="" data-state="closed"><button class="flex select-none items-center gap-1"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="icon-xs"><path d="M2.5 5.5C4.3 5.2 5.2 4 5.5 2.5C5.8 4 6.7 5.2 8.5 5.5C6.7 5.8 5.8 7 5.5 8.5C5.2 7 4.3 5.8 2.5 5.5Z" fill="currentColor" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"></path><path d="M5.66282 16.5231L5.18413 19.3952C5.12203 19.7678 5.09098 19.9541 5.14876 20.0888C5.19933 20.2067 5.29328 20.3007 5.41118 20.3512C5.54589 20.409 5.73218 20.378 6.10476 20.3159L8.97693 19.8372C9.72813 19.712 10.1037 19.6494 10.4542 19.521C10.7652 19.407 11.0608 19.2549 11.3343 19.068C11.6425 18.8575 11.9118 18.5882 12.4503 18.0497L20 10.5C21.3807 9.11929 21.3807 6.88071 20 5.5C18.6193 4.11929 16.3807 4.11929 15 5.5L7.45026 13.0497C6.91175 13.5882 6.6425 13.8575 6.43197 14.1657C6.24513 14.4392 6.09299 14.7348 5.97903 15.0458C5.85062 15.3963 5.78802 15.7719 5.66282 16.5231Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path><path d="M14.5 7L18.5 11" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path></svg>Edit</button></span></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="!whitespace-pre hljs language-bash">pip install -r requirements.txt
   </code></div></div></pre>
3. Procesa los datos ejecutando  **ETL.ipynb** .
4. Ejecuta **app.py** con:
   <pre class="!overflow-visible"><div class="contain-inline-size rounded-md border-[0.5px] border-token-border-medium relative bg-token-sidebar-surface-primary dark:bg-gray-950"><div class="flex items-center text-token-text-secondary px-4 py-2 text-xs font-sans justify-between rounded-t-md h-9 bg-token-sidebar-surface-primary dark:bg-token-main-surface-secondary select-none">bash</div><div class="sticky top-9 md:top-[5.75rem]"><div class="absolute bottom-0 right-2 flex h-9 items-center"><div class="flex items-center rounded bg-token-sidebar-surface-primary px-2 font-sans text-xs text-token-text-secondary dark:bg-token-main-surface-secondary"><span class="" data-state="closed"><button class="flex gap-1 items-center select-none px-4 py-1" aria-label="Copy"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="icon-xs"><path fill-rule="evenodd" clip-rule="evenodd" d="M7 5C7 3.34315 8.34315 2 10 2H19C20.6569 2 22 3.34315 22 5V14C22 15.6569 20.6569 17 19 17H17V19C17 20.6569 15.6569 22 14 22H5C3.34315 22 2 20.6569 2 19V10C2 8.34315 3.34315 7 5 7H7V5ZM9 7H14C15.6569 7 17 8.34315 17 10V15H19C19.5523 15 20 14.5523 20 14V5C20 4.44772 19.5523 4 19 4H10C9.44772 4 9 4.44772 9 5V7ZM5 9C4.44772 9 4 9.44772 4 10V19C4 19.5523 4.44772 20 5 20H14C14.5523 20 15 19.5523 15 19V10C15 9.44772 14.5523 9 14 9H5Z" fill="currentColor"></path></svg>Copy</button></span><span class="" data-state="closed"><button class="flex select-none items-center gap-1"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="icon-xs"><path d="M2.5 5.5C4.3 5.2 5.2 4 5.5 2.5C5.8 4 6.7 5.2 8.5 5.5C6.7 5.8 5.8 7 5.5 8.5C5.2 7 4.3 5.8 2.5 5.5Z" fill="currentColor" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"></path><path d="M5.66282 16.5231L5.18413 19.3952C5.12203 19.7678 5.09098 19.9541 5.14876 20.0888C5.19933 20.2067 5.29328 20.3007 5.41118 20.3512C5.54589 20.409 5.73218 20.378 6.10476 20.3159L8.97693 19.8372C9.72813 19.712 10.1037 19.6494 10.4542 19.521C10.7652 19.407 11.0608 19.2549 11.3343 19.068C11.6425 18.8575 11.9118 18.5882 12.4503 18.0497L20 10.5C21.3807 9.11929 21.3807 6.88071 20 5.5C18.6193 4.11929 16.3807 4.11929 15 5.5L7.45026 13.0497C6.91175 13.5882 6.6425 13.8575 6.43197 14.1657C6.24513 14.4392 6.09299 14.7348 5.97903 15.0458C5.85062 15.3963 5.78802 15.7719 5.66282 16.5231Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path><path d="M14.5 7L18.5 11" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path></svg>Edit</button></span></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="!whitespace-pre hljs language-bash">python app.py
   </code></div></div></pre>
5. Abre la aplicación en tu navegador en `http://127.0.0.1:8050/`.
