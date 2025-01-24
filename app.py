import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import geopandas as gpd
import plotly.graph_objects as go
import plotly.express as px
from scipy.stats import pearsonr
from sklearn.linear_model import LinearRegression
import numpy as np



# Cargar dataframes
vel_media_provincia = pd.read_csv('./Datasets/vel_media_provincia.csv', parse_dates=['Fecha'])
penetracion_hogar = pd.read_csv('./Datasets/penetracion_hogar.csv', parse_dates=['Fecha'])
penetracion_poblac = pd.read_csv('./Datasets/penetracion_poblac.csv', parse_dates=['Fecha'])
tecnologia_provincia = pd.read_csv('./Datasets/tecnologia_provincia.csv', parse_dates=['Fecha'])

# Cargar GeoJSON y procesar datos
geojson_path = './Mapas/map.geojson'
gdf = gpd.read_file(geojson_path)
gdf["Provincia"] = gdf["nombre"]
gdf = gdf.merge(vel_media_provincia, on="Provincia", how="left")


# Integrar y procesar datos para "Relación con Tecnologías"
data = pd.merge(tecnologia_provincia, vel_media_provincia, on=["Provincia", "Fecha"], how="inner")
tecnologias = ["ADSL", "Cablemodem", "Fibra óptica", "Wireless", "Otros"]
for tecnologia in tecnologias:
    data[f"prop_{tecnologia}"] = data[tecnologia] / data["Total"]
data["Tecnologia_Predominante"] = data[tecnologias].idxmax(axis=1)


vel_media_tecnologia = data.groupby(["Tecnologia_Predominante", data["Fecha"].dt.year])["Mbps (Media de bajada)"].mean().reset_index()
correlacion_tecnologias = data[["Mbps (Media de bajada)"] + [f"prop_{tecnologia}" for tecnologia in tecnologias]].corr()
correlacion_veloc_tecnologia = correlacion_tecnologias.loc["Mbps (Media de bajada)", [f"prop_{tecnologia}" for tecnologia in tecnologias]].sort_values()
tend_tecnol = data.groupby("Fecha")[tecnologias].sum()
tendencia = tend_tecnol.div(tend_tecnol.sum(axis=1), axis=0).reset_index()

data['Año'] = data['Fecha'].dt.year

# Merge de datasets para análisis estadístico
merged_data = pd.merge(penetracion_hogar, penetracion_poblac, on=["Provincia", "Fecha"], how="inner")
merged_data = pd.merge(merged_data, tecnologia_provincia, on=["Provincia", "Fecha"], how="inner")
merged_data = pd.merge(merged_data, vel_media_provincia, on=["Provincia", "Fecha"], how="inner")
merged_data.rename(columns={
    "Accesos por cada 100 hogares": "Penetración_hogar",
    "Accesos por cada 100 hab": "Penetración_población",
    "Mbps (Media de bajada)": "Velocidad_media"
}, inplace=True)

vel_media_provincia = vel_media_provincia.sort_values(by=['Provincia', 'Fecha'])
penetracion_hogar = penetracion_hogar.sort_values(by=['Provincia', 'Fecha'])
penetracion_poblac = penetracion_poblac.sort_values(by=['Provincia', 'Fecha'])


vel_media_provincia["Tasa_de_crecimiento_vel_media"] = vel_media_provincia.groupby("Provincia")["Mbps (Media de bajada)"].pct_change() * 100
penetracion_hogar["Tasa_de_crecimiento_penetracion_hogar"] = penetracion_hogar.groupby("Provincia")["Accesos por cada 100 hogares"].pct_change() * 100
penetracion_poblac["Tasa_de_crecimiento_penetracion_poblacion"] = penetracion_poblac.groupby("Provincia")["Accesos por cada 100 hab"].pct_change() * 100


crecimiento_vel_media = vel_media_provincia.groupby("Provincia")["Tasa_de_crecimiento_vel_media"].mean().reset_index()
crecimiento_penetracion_hogar = penetracion_hogar.groupby("Provincia")["Tasa_de_crecimiento_penetracion_hogar"].mean().reset_index()
crecimiento_penetracion_poblac = penetracion_poblac.groupby("Provincia")["Tasa_de_crecimiento_penetracion_poblacion"].mean().reset_index()

resumen_crecimiento = crecimiento_vel_media.merge(crecimiento_penetracion_hogar, on="Provincia").merge(crecimiento_penetracion_poblac, on="Provincia")


top_vel_media = resumen_crecimiento.nlargest(3, 'Tasa_de_crecimiento_vel_media')[['Provincia', 'Tasa_de_crecimiento_vel_media']]
top_penetracion_hogar = resumen_crecimiento.nlargest(3, 'Tasa_de_crecimiento_penetracion_hogar')[['Provincia', 'Tasa_de_crecimiento_penetracion_hogar']]
top_penetracion_poblac = resumen_crecimiento.nlargest(3, 'Tasa_de_crecimiento_penetracion_poblacion')[['Provincia', 'Tasa_de_crecimiento_penetracion_poblacion']]

top_crecimiento = {
    "Top_crecimeinto_velocidad (Mbps)": top_vel_media,
    "Top_crecimiento_penetracion_hogar (%)": top_penetracion_hogar,
    "Top_crecimiento_penetracion_poblacion (%)": top_penetracion_poblac
}

# Tomar los datos de penetracion hogar del ultimo trimestre 2023 y primero 2024
penetracion_hogar_T4_2023 = penetracion_hogar[(penetracion_hogar['Fecha'].dt.year == 2023)&(penetracion_hogar['Fecha'].dt.month == 10)].copy()
penetracion_hogar_T1_2024 = penetracion_hogar[(penetracion_hogar['Fecha'].dt.year == 2024)&(penetracion_hogar['Fecha'].dt.month == 1)].copy()

#Generacion de Data
Trimestres_2024 = ["2024-01-01", "2024-04-01", "2024-07-01", "2024-10-01"]
crecimiento_estimado = [2, 4, 6, 8]

datos_proyectados = []
for index, row in penetracion_hogar_T4_2023.iterrows():
    penetracion_hogar_2023 = row['Accesos por cada 100 hogares']
    for i, trimestre in enumerate(Trimestres_2024):
        penetracion_hogar_estimada = penetracion_hogar_2023 * (1 + crecimiento_estimado[i] / 100)
        penetracion_hogar_simulada = penetracion_hogar_estimada * (1 + np.random.uniform(-0.08, 0.08))  # Random variation of +/- 8%
        datos_proyectados.append({
            'Provincia': row['Provincia'],
            'Fecha': pd.to_datetime(trimestre),
            'Estimado': penetracion_hogar_estimada,
            'Simulado': penetracion_hogar_simulada
        })

penetracion_hogar_proyectado = pd.DataFrame(datos_proyectados)
penetracion_hogar_proyectado = penetracion_hogar_proyectado.sort_values(by=['Provincia', 'Fecha'], ascending=[True, False]).reset_index(drop=True)

penetracion_hogar_estimado = penetracion_hogar_proyectado[['Provincia', 'Fecha', 'Estimado']].copy()
penetracion_hogar_simulado = penetracion_hogar_proyectado[['Provincia', 'Fecha', 'Simulado']].copy()

penetracion_hogar_T4_2023.rename(columns={'Accesos por cada 100 hogares': 'Estimado'}, inplace=True)
penetracion_hogar_T4_2023 = penetracion_hogar_T4_2023.sort_values(by=['Provincia', 'Fecha'], ascending=[True, False]).reset_index(drop=True)

correccion = penetracion_hogar_simulado.copy()
correccion.loc[correccion['Fecha'] == '2024-01-01', 'Simulado'] = correccion.loc[correccion['Fecha'] == '2024-01-01', 'Provincia'].map(penetracion_hogar_T1_2024.set_index('Provincia')['Accesos por cada 100 hogares'])
penetracion_hogar_simulado = correccion


penetracion_hogar_proyectado['KPI'] = pd.DataFrame({
    'KPI': ((penetracion_hogar_simulado['Simulado'] - penetracion_hogar_estimado['Estimado']) / 
            penetracion_hogar_estimado['Estimado']) * 100
})

kpi_mean = penetracion_hogar_proyectado.groupby('Fecha')['KPI'].mean().reset_index()

penetracion_hogar_estimado_mean = penetracion_hogar_estimado.groupby('Fecha')['Estimado'].mean().reset_index()
penetracion_hogar_simulado_mean = penetracion_hogar_simulado.groupby('Fecha')['Simulado'].mean().reset_index()


penetracion_hogar_simulado_mean.rename(columns={'Simulado': 'Real'}, inplace=True)

ultimo_trimestre_2023 = vel_media_provincia[(vel_media_provincia['Fecha'].dt.year == 2023) &
                                            (vel_media_provincia['Fecha'].dt.month >= 10)]

# Ordenar por velocidad promedio en orden ascendente y tomar las dos provincias con menor velocidad
provincias_menor_velocidad = ultimo_trimestre_2023.nsmallest(2, 'Mbps (Media de bajada)')


#Generacion de Data
Trimestres_2024 = ["2024-01-01", "2024-04-01", "2024-07-01", "2024-10-01"]
crecimiento_estimado = [10, 20 , 30, 40]

datos_proyectados = []
for index, row in provincias_menor_velocidad.iterrows():
    velocida_media_2023 = row['Mbps (Media de bajada)']
    for i, trimestre in enumerate(Trimestres_2024):
        velocidad_media_estimada = velocida_media_2023 * (1 + crecimiento_estimado[i] / 100)
        velocidad_media_simulada = velocidad_media_estimada * (1 + np.random.uniform(-0.10, 0.10))  # Random variation of +/- 10%
        datos_proyectados.append({
            'Provincia': row['Provincia'],
            'Fecha': pd.to_datetime(trimestre),
            'Estimado': velocidad_media_estimada,
            'Simulado': velocidad_media_simulada
             })
        

velocidad_media_proyectado = pd.DataFrame(datos_proyectados)

velocidad_media_estimado = penetracion_hogar_proyectado[['Provincia', 'Fecha', 'Estimado']].copy()
velocidad_media_simulado = penetracion_hogar_proyectado[['Provincia', 'Fecha', 'Simulado']].copy()


velocidad_media_proyectado['KPI'] = pd.DataFrame({
    'KPI': ((velocidad_media_simulado['Simulado'] - velocidad_media_estimado['Estimado']) / 
            velocidad_media_estimado['Estimado']) * 100
})


kpi_mean_provincia = velocidad_media_proyectado.groupby(['Provincia', 'Fecha'])['KPI'].mean().reset_index()



def crear_grafico_kpi_penetracion(kpi_mean):
    fig = px.line(
        kpi_mean, 
        x="Fecha", 
        y="KPI", 
        title="Comportamiento del KPI en el Tiempo", 
        labels={"KPI": "KPI (%)", "Fecha": "Fecha"}
    )
    fig.add_hline(
        y=2, 
        line_dash="dash", 
        line_color="red", 
        annotation_text="Meta del KPI (2%)",
        annotation_position="top right"
    )
    fig.update_layout(
        height=400,
        title=dict(x=0.5, xanchor="center"),
        margin={"l": 20, "r": 20, "t": 40, "b": 20}
    )
    return fig

def crear_grafico_tendencia_penetracion(penetracion_hogar_estimado_mean, penetracion_hogar_simulado_mean):
    penetracion_hogar_estimado_mean = penetracion_hogar_estimado_mean.merge(penetracion_hogar_simulado_mean)

    fig = px.line(
        penetracion_hogar_estimado_mean,
        x="Fecha",
        y=["Estimado", "Real"],
        #labels={
        #    "value": "Accesos por cada 100 Hogares (Promedio Nacional)",  # Etiqueta del eje Y
        #    "variable": "Leyenda"  # Etiqueta del eje de la leyenda
        #},
        title="Tendencia de Estimados y Real de Penetración por Hogar",
    )
    fig.update_layout(
    height=400,
    title=dict(x=0.5, xanchor="center"),
    margin={"l": 20, "r": 20, "t": 40, "b": 20},
    showlegend=True,
    legend=dict(
        x=0.02,               # Posición horizontal
        y=0.98,               # Posición vertical
        bordercolor="black",  # Color del borde
        borderwidth=1         # Ancho del borde
    ),
    yaxis=dict(
        title="Accesos por cada 100 Hogares"  # Título del eje Y
    ),
    xaxis=dict(
        title="Fecha"  # Título del eje X
    )
)
    return fig

def crear_grafico_kpi_velocidad(kpi_mean_provincia):
    fig = px.line(
        kpi_mean_provincia,
        x="Fecha",
        y="KPI",
        color="Provincia",
        title="Tendencia del KPI por Provincia",
        labels={"KPI": "KPI (%)", "Fecha": "Fecha"}
    )
    fig.add_hline(
        y=0, 
        line_dash="dash", 
        line_color="red", 
        annotation_text="Referencia (0%)",
        annotation_position="bottom right"
    )
    fig.update_layout(
        height=400,
        title=dict(x=0.5, xanchor="center"),
        margin={"l": 20, "r": 20, "t": 40, "b": 20},
    )
    return fig

def crear_grafico_tendencia_velocidad(provincia_data):
    fig = px.line(
        provincia_data,
        x="Fecha",
        y=["Estimado", "Simulado"],
        labels={"value": "Velocidad Media (Mbps)", "variable": "Tendencia"},
        title=f"Tendencia de Velocidad Media Estimada y Real por Provincia ({provincia_data['Provincia'].iloc[0]})",
    )
    fig.update_layout(
        height=400,
        title=dict(x=0.5, xanchor="center"),
        margin={"l": 20, "r": 20, "t": 40, "b": 20},
    )
    return fig

# Crear el mapa interactivo
def crear_mapa_interactivo():
    fig_mapa = go.Figure()

    fig_mapa.add_trace(go.Choroplethmapbox(
        geojson=gdf.__geo_interface__,
        locations=gdf.index,
        z=gdf["Mbps (Media de bajada)"],
        colorscale='Blues',
        zmin=0,
        zmax=gdf["Mbps (Media de bajada)"].max(),
        marker_opacity=0.7,
        marker_line_width=0.5,
        marker_line_color='black',
        hoverinfo='text',
        text=gdf['Provincia'] + ': ' + gdf["Mbps (Media de bajada)"].astype(str) + ' Mbps',
        hovertemplate='<b>Provincia:</b> %{text}<extra></extra>'
    ))

    fig_mapa.update_layout(
        mapbox_style="carto-positron",
        mapbox_zoom=3,
        mapbox_center={"lat": -38.4161, "lon": -63.6167},
        title_text='Velocidad Media de Internet por Provincia',
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        height=None,  # Permite que se ajuste dinámicamente al contenedor
        width=None,
        hoverlabel=dict(
            bgcolor="white",  # Fondo blanco del hover
            font_size=12,
            font_family="Arial"
        ),
        coloraxis_colorbar=dict(
            title="Mbps",  # Título de la barra de colores
            tickvals=[0, gdf["Mbps (Media de bajada)"].max() / 2, gdf["Mbps (Media de bajada)"].max()],
            ticktext=["Bajo", "Medio", "Alto"]  # Etiquetas de los ticks
        )
    )
    return fig_mapa
# Crear gráficos iniciales
def crear_grafico_tendencia_inicial():
    promedio_nacional = vel_media_provincia.groupby("Fecha")["Mbps (Media de bajada)"].mean().reset_index()
    fig = px.line(
        promedio_nacional,
        x="Fecha",
        y="Mbps (Media de bajada)",
        title="Tendencia Nacional de Velocidad Media",
        labels={"Mbps (Media de bajada)": "Velocidad Media (Mbps)", "Fecha": "Fecha"}
    )
    return fig

def crear_grafico_crecimiento_inicial():
    vel_media_provincial = vel_media_provincia.pivot(index="Fecha", columns="Provincia", values="Mbps (Media de bajada)")
    vel_media_crecimiento = vel_media_provincial.pct_change().mean() * 100
    vel_media_crecimiento_sorted = vel_media_crecimiento.sort_values(ascending=False)
    fig = px.bar(
        vel_media_crecimiento_sorted,
        x=vel_media_crecimiento_sorted.index,
        y=vel_media_crecimiento_sorted.values,
        title="Crecimiento Promedio de Velocidad Media por Provincia (%)",
        labels={"x": "Provincia", "y": "Crecimiento Promedio (%)"}
    )
    return fig
# Crear gráficos iniciales para "Relación con Tecnologías"
def crear_grafico_velocidad_tecnologia(year):

    
    filtro = data[data['Año'] == year]
    vel_media_tecnologia_año = (
    filtro.groupby("Tecnologia_Predominante")["Mbps (Media de bajada)"].mean().sort_values(ascending=True).reset_index())
    vel_media_tecnologia_año.columns = ["Tecnologia_Predominante", "Velocidad_Media_Mbps"]
   

    fig = px.bar(
        vel_media_tecnologia_año,
        y="Tecnologia_Predominante",
        x="Velocidad_Media_Mbps",
        orientation="h",
        title=f"Velocidad Media por Tecnología Predominante ({year})",
        labels={"Mbps (Media de bajada)": "Velocidad Media (Mbps)", "Tecnologia_Predominante": "Tecnología"},
        color="Tecnologia_Predominante"
    )
    fig.update_layout(
        margin={"l": 10, "r": 10, "t": 60, "b": 0},  # Ajustar márgenes
        height=250,  
        width=800, 
        showlegend=False,
        title=dict(
            text=f"Velocidad Media por Tecnología Predominante ({year})",  # Título del gráfico
            x=0.5,  
            xanchor="center"),
)
    
    return fig

def crear_grafico_correlacion():
    fig = px.bar(
        correlacion_veloc_tecnologia,
        x=correlacion_veloc_tecnologia.values,
        y=correlacion_veloc_tecnologia.index,
        orientation="h",
        title="Correlación entre Tecnologías y Velocidad Media",
        labels={"x": "Coeficiente de Correlación", "index": "Tecnología"}
    )
    fig.update_layout(
        margin={"l": 20, "r": 20, "t": 40, "b": 20}, 
        height=250, 
        width=800,
        title=dict(
            text="Correlación entre Tecnologías y Velocidad Media",  # Título del gráfico
            x=0.5,  
            xanchor="center"),)
    return fig

def crear_grafico_tendencia_tecnologias():
    fig = px.line(
        tendencia,
        x="Fecha",
        y=tecnologias,
        title="Evolución del Uso de Tecnologías",
        labels={"value": "Proporción", "variable": "Tecnología"}
    )
    fig.update_layout(margin={"l": 20, "r": 20, "t": 40, "b": 20}, 
        height=250, 
        width=800,
        title=dict(
            text="Correlación entre Tecnologías y Velocidad Media",  # Título del gráfico
            x=0.5,  
            xanchor="center"),)
    return fig

def crear_mapa_tendencias_provincias(year):
    filtro = data[data['Fecha'].dt.year == year]
      # Calcular el promedio de Mbps (Media de bajada) por provincia y tecnología predominante
    promedio_data = filtro.groupby(["Provincia", "Tecnologia_Predominante"], as_index=False)["Mbps (Media de bajada)"].mean()
    
    # Crear el gráfico interactivo con Plotly
    fig = px.bar(
        promedio_data,
        x="Provincia",
        y="Mbps (Media de bajada)",
        color="Tecnologia_Predominante",
        title=f"Promedio de Mbps (Media de bajada) por Provincia y Tecnología Predominante ({year})",
        labels={"Provincia": "Provincia", "Mbps (Media de bajada)": "Promedio de Mbps"},
        barmode="group",
    )
   
    fig.update_layout(
        margin={"l": 10, "r": 10, "t": 30, "b": 0},  # Ajustar márgenes
        height=360,  
        width=800, 
        showlegend=False,
        title=dict(
            text=f"Proporción de la Tecnología Predominante por Provincia en {year}",  # Título del gráfico
            x=0.5,  
            xanchor="center",
            ))
    
    return fig


# Inicializar la app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG], suppress_callback_exceptions=True)
app.title = "Análisis de Acceso a Internet en Argentina"

# Layout de la app
app.layout = html.Div([
    dcc.Tabs(id="tabs", value="tab1", children=[
        dcc.Tab(label="Tendencias Temporales", value="tab1"),
        dcc.Tab(label="Relación con Tecnologías", value="tab2"),
        dcc.Tab(label="Penetración y Tecnologías", value="tab3"),
        dcc.Tab(label="Análisis de Tendencias", value="tab4"),
        dcc.Tab(label="KPI", value="tab5"),
    ]),
    html.Div(id="content")
])

# Callback para actualizar el contenido según la pestaña seleccionada
@app.callback(
    Output("content", "children"),
    [Input("tabs", "value")]
)
def update_content(tab):
    if tab == "tab1":
        return html.Div([
            html.Div([
                html.Div([
                    dcc.Graph(id="mapa-interactivo", figure=crear_mapa_interactivo())
                ], 
                style={
                    "width": "30%", 
                    "display": "flex", 
                    "flex-direction": "column", 
                    "justify-content": "center", 
                    "height": "100%",
                    "padding": "1px"  
                    #"margin": "0 auto"
                }),
                html.Div([
                    html.Div([
                        dcc.Graph(id="grafico-tendencia", figure=crear_grafico_tendencia_inicial(), style={"width": "auto","height": "100%","padding": "1px" })
                    ], style={
                        "display": "flex", 
                        "justify-content": "center", 
                        "align-items": "center", 
                        "height": "100%",
                        "padding": "0px"  
                    }),
                    html.Div([
                        dcc.Graph(id="grafico-crecimiento", figure=crear_grafico_crecimiento_inicial(), style={"height": "100%"})
                    ], style={
                        "display": "flex", 
                        "justify-content": "center", 
                        "align-items": "center", 
                        "height": "100%",
                    "padding": "0px"
                        
                    })
                ], style={
                    "width": "60%", 
                    "display": "flex", 
                    "flex-direction": "column", 
                    "justify-content": "space-between", 
                    "align-items": "center",
                    "padding": "0px"  
                })
            ], style={
                "display": "flex", 
                "flex-direction": "row", 
                "height": "80vh",
                "justify-content": "center",
                "padding": "10px"  
            }),
            html.Div([
                html.H4("Conclusiones"),
                html.P("Las provincias tienen patrones de crecimiento diferenciados. Algunas han experimentado incrementos más significativos en comparación con otras")
            ], style={
                "margin-top": "20px", 
                "border-top": "1px solid #ccc", 
                "padding-top": "10px", 
                "text-align": "center",
                "padding": "10px"  
            })
        ])
    elif tab == "tab2":
        return html.Div([

            html.Div([
                html.Div([
                    html.Label("Seleccione el Año:"),
                    dcc.Slider(
                        id="slider-year",
                        min=int(vel_media_tecnologia["Fecha"].min()),
                        max=int(vel_media_tecnologia["Fecha"].max()),
                        step=1,
                        value=int(vel_media_tecnologia["Fecha"].min()),
                        marks={int(year): str(year) for year in vel_media_tecnologia["Fecha"].unique()}
                    ),
                    dcc.Graph(id="grafico-velocidad-tecnologia", style={"width": "auto","height": "100%","overflow": "hidden"})
                ], style={"width": "100%", "height": "60%", "padding": "10px"}),
                
                html.Div([
                    dcc.Graph(id="grafico-correlacion", figure=crear_grafico_correlacion())
                    ], style={"width": "100%", "height": "40%", "padding": "10px"})
                ], style={"width": "50%", "display": "flex", "flex-direction": "column", "justify-content": "space-between", "align-items": "center"}),



            html.Div([
                html.Div([
                    dcc.Graph(id="grafico-provincia-tendencias", style={"width": "auto", "height": "100%","overflow": "hidden"})
                    ], style={"width": "100%", "height": "60%", "padding": "10px"}),
                html.Div([
                    dcc.Graph(id="grafico-tendencia-tecnologias", figure=crear_grafico_tendencia_tecnologias())
                    ], style={"width": "100%","height": "40%", "padding": "10px"}),
                ],style={"width": "50%", "display": "flex", "flex-direction": "column", "justify-content": "space-between", "align-items": "center"}),
         ], style={"width": "100%", "display": "flex", "flex-direction": "row", "height": "80vh"})
    elif tab == "tab3":
        return dbc.Container([
            dbc.Row([
                dbc.Col(html.H4("Análisis Estadístico: Velocidad vs Penetración", className="text-center mb-4"), width=12)
            ]),
            dbc.Row([
                # Scatter plot: Velocidad Media vs Penetración por Población
                dbc.Col(dcc.Graph(id="scatter-penetracion-poblacion"), width=6),
                # Scatter plot: Velocidad Media vs Penetración por Hogares
                dbc.Col(dcc.Graph(id="scatter-penetracion-hogar"), width=6),
            ]),
            dbc.Row([
                # Tabla de métricas de correlación y regresión
                dbc.Col(html.Div(id="tabla-metricas"), width=12)
            ])
        ])
    elif tab == "tab4":
        return html.Div([
        html.Div([
            html.H4("Top 3 Crecimientos", style={"text-align": "center"}),
            html.Div([
                html.H6("Velocidad Media (Mbps)", style={"margin-top": "10px"}),
                html.Div(id="tabla-top-crecimiento-velocidad"),
                html.H6("Penetración por Hogares (%)", style={"margin-top": "20px"}),
                html.Div(id="tabla-top-crecimiento-hogar"),
                html.H6("Penetración por Población (%)", style={"margin-top": "20px"}),
                html.Div(id="tabla-top-crecimiento-poblacion"),
            ], style={"padding": "10px"})
        ], style={"width": "25%", "float": "left"}),

        html.Div([
            html.Div([
                dcc.Graph(id="grafico-comparacion-crecimiento")
            ], style={"width": "100%", "height": "50%"}),

            html.Div([
                dcc.Graph(id="grafico-distribucion-crecimiento")
            ], style={"width": "100%", "height": "50%"})
        ], style={"width": "75%", "float": "right", "padding": "10px"})
    ], style={"display": "flex"})
    elif tab == "tab5":
        return html.Div([
            html.H3("KPI: Penetración por Hogares", 
                    style={"text-align": "center",
                           "font-size": "32px", 
                           "margin-top": "20px",
                           "margin-bottom": "10px",
                           "height": "40px"
                    }),
            html.P("Objetivo: Aumentar en un 2% el acceso al servicio de internet trimestral, cada 100 hogares, por provincia para el próximo año.",
                   style={
                       "text-align": "center",       
                       "font-size": "18px",          
                       "margin-top": "5px",         
                       "margin-bottom": "15px",     
                       "color": "#555",
                       "height": "40px"

    }),
            dcc.Graph(id="grafico-kpi-penetracion", style={"width": "90%","height": "600px","overflow": "hidden","margin":"0 auto"}), 
            dcc.Graph(id="grafico-tendencia-penetracion",style={"width": "90%","height": "600px","overflow": "hidden","margin":"0 auto"}), 

            html.H3("KPI: Velocidad Media de Descarga", style={"text-align": "center",
                           "font-size": "32px", 
                           "margin-top": "20px",
                           "margin-bottom": "10px",
                           "height": "40px"
                    }),
            html.P("Objetivo: Aumentar en un 40% la velocidad media de descarga de internet para el próximo año, para las dos provincias con menor velocidad de descarga.", style={
                       "text-align": "center",       
                       "font-size": "18px",          
                       "margin-top": "5px",         
                       "margin-bottom": "15px",     
                       "color": "#555",
                       "height": "40px"

    }),
            dcc.Graph(id="grafico-kpi-velocidad",style={"width": "90%","height": "600px","overflow": "hidden","margin":"0 auto"}),  # Placeholder para gráfico de KPI de velocidad
            html.Div(id="graficas-tendencia-provincias",style={"width": "90%","height": "1200px","overflow": "hidden","margin":"0 auto"})  # Placeholder para gráficos por provincia
        ])

# Callbacks placeholders para todas las pestañas
@app.callback(
    [
        Output("grafico-tendencia", "figure"),
        Output("grafico-crecimiento", "figure"),
    ],
    [
        Input("mapa-interactivo", "hoverData"),
    ]
)
def update_graficos(hoverData):
    if hoverData:
        provincia_hover = gdf.loc[hoverData["points"][0]["location"],"Provincia"]
        provincia_data = vel_media_provincia[vel_media_provincia["Provincia"] == provincia_hover]
        fig_tendencia = px.line(
            provincia_data,
            x="Fecha",
            y="Mbps (Media de bajada)",
            title=f"Tendencia de Velocidad Media en {provincia_hover}",
            labels={"Mbps (Media de bajada)": "Velocidad Media (Mbps)", "Fecha": "Fecha"}
            )
        fig_tendencia.update_layout(
            title={
            "text": f"Tendencia de Velocidad Media en {provincia_hover}",
            "x": 0.5,  # Centrado horizontalmente
            "xanchor": "center",  # Anclaje horizontal centrado
            "yanchor": "top"  # Anclaje vertical superior
            },
            margin={
            "l": 5,  # Margen izquierdo mínimo
            "r": 5,  # Margen derecho mínimo
            "t": 40,  # Espacio suficiente para el título
            "b": 5   # Margen inferior mínimo
            },
            font=dict(size=12),  # Ajustar tamaño de fuente
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),  # Ajustar la posición de la leyenda
            height=None,  # Dinámico según el contenedor
            width=None    # Dinámico según el contenedor
)
        
    else:
        fig_tendencia = crear_grafico_tendencia_inicial()
        fig_tendencia.update_layout(
            title={
            "text": "Tendencia Nacional de la Velocidad Media de Internet",
            "x": 0.5,  # Centrado horizontalmente
            "xanchor": "center",  # Anclaje horizontal centrado
            "yanchor": "top"  # Anclaje vertical superior
            },
            margin={
            "l": 5,  # Margen izquierdo mínimo
            "r": 5,  # Margen derecho mínimo
            "t": 40,  # Espacio suficiente para el título
            "b": 5   # Margen inferior mínimo
            },
            font=dict(size=12),  # Ajustar tamaño de fuente
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),  # Ajustar la posición de la leyenda
            height=None,  # Dinámico según el contenedor
            width=None    # Dinámico según el contenedor
        )

    fig_crecimiento = crear_grafico_crecimiento_inicial()
    fig_crecimiento.update_layout(
            title={
            "x": 0.5,  # Centrado horizontalmente
            "xanchor": "center",  # Anclaje horizontal centrado
            "yanchor": "top"  # Anclaje vertical superior
            },
            margin={
            "l": 5,  # Margen izquierdo mínimo
            "r": 5,  # Margen derecho mínimo
            "t": 40,  # Espacio suficiente para el título
            "b": 5   # Margen inferior mínimo
            },
            font=dict(size=8),  # Ajustar tamaño de fuente
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),  # Ajustar la posición de la leyenda
            height=None,  # Dinámico según el contenedor
            width=None    # Dinámico según el contenedor
    )


    return fig_tendencia, fig_crecimiento


@app.callback(
    [
        Output("grafico-velocidad-tecnologia", "figure"),
        Output("grafico-provincia-tendencias", "figure")
    ],
    [Input("slider-year", "value")]
)
def update_graficos_velocidad_y_tecnologia(year):
   
    fig_velocidad = crear_grafico_velocidad_tecnologia(year)
    fig_provincia = crear_mapa_tendencias_provincias(year)
    
    return fig_velocidad, fig_provincia

# Callback para la pestaña de Analisis de Tendencia
@app.callback(
    Output("scatter-penetracion-poblacion", "figure"),
    Output("scatter-penetracion-hogar", "figure"),
    Output("tabla-metricas", "children"),
    Input("tabs", "value")
)
def update_analisis_estadistico(tab):
    if tab != "tab3":
        raise dash.exceptions.PreventUpdate

    # Scatter plot: Velocidad Media vs. Penetración por Población
    fig_poblacion = px.scatter(
        merged_data,
        x="Penetración_población",
        y="Velocidad_media",
        color="Provincia",
        title="Velocidad Media vs Penetración por Población",
        labels={"Penetración_población": "Penetración por Población (%)", "Velocidad_media": "Velocidad Media (Mbps)"}
    )
    fig_poblacion.update_layout(title={"x": 0.5}, margin={"t": 50})

    # Scatter plot: Velocidad Media vs Penetración por Hogares
    fig_hogar = px.scatter(
        merged_data,
        x="Penetración_hogar",
        y="Velocidad_media",
        color="Provincia",
        title="Velocidad Media vs Penetración por Hogares",
        labels={"Penetración_hogar": "Penetración por Hogares (%)", "Velocidad_media": "Velocidad Media (Mbps)"}
    )
    fig_hogar.update_layout(title={"x": 0.5}, margin={"t": 50})

    # Calcular métricas de correlación y regresión
    correlation_poblacional, p_value_poblacional = pearsonr(merged_data["Penetración_población"], merged_data["Velocidad_media"])
    correlation_hogar, p_value_hogar = pearsonr(merged_data["Penetración_hogar"], merged_data["Velocidad_media"])

    X_poblacion = merged_data[["Penetración_población"]]
    y_poblacion = merged_data["Velocidad_media"]
    reg_poblacion = LinearRegression().fit(X_poblacion, y_poblacion)

    X_hogar = merged_data[["Penetración_hogar"]]
    y_hogar = merged_data["Velocidad_media"]
    reg_hogar = LinearRegression().fit(X_hogar, y_hogar)

    # Crear tabla de resultados
    tabla = dbc.Table(
        [
            html.Thead(html.Tr([
                html.Th("Métrica"), html.Th("Población"), html.Th("Hogares")
            ])),
            html.Tbody([
                html.Tr([
                    html.Td("Correlación de Pearson"),
                    html.Td(round(correlation_poblacional, 2)),
                    html.Td(round(correlation_hogar, 2))
                ]),
                html.Tr([
                    html.Td("P-valor"),
                    html.Td(f"{p_value_poblacional:.2e}"),
                    html.Td(f"{p_value_hogar:.2e}")
                ]),
                html.Tr([
                    html.Td("Pendiente (slope)"),
                    html.Td(round(reg_poblacion.coef_[0], 2)),
                    html.Td(round(reg_hogar.coef_[0], 2))
                ]),
                html.Tr([
                    html.Td("Intercepto"),
                    html.Td(round(reg_poblacion.intercept_, 2)),
                    html.Td(round(reg_hogar.intercept_, 2))
                ]),
                html.Tr([
                    html.Td("R²"),
                    html.Td(round(reg_poblacion.score(X_poblacion, y_poblacion), 2)),
                    html.Td(round(reg_hogar.score(X_hogar, y_hogar), 2))
                ])
            ])
        ],
        bordered=True,
        hover=True,
        responsive=True,
        striped=True,
    )

    return fig_poblacion, fig_hogar, tabla

@app.callback(
    [
        Output("tabla-top-crecimiento-velocidad", "children"),
        Output("tabla-top-crecimiento-hogar", "children"),
        Output("tabla-top-crecimiento-poblacion", "children"),
        Output("grafico-comparacion-crecimiento", "figure"),
        Output("grafico-distribucion-crecimiento", "figure")
    ],
    [Input("tabs", "value")]
)
def update_tab4_content(tab):
    if tab != "tab4":
        raise dash.exceptions.PreventUpdate

    # Tablas Top 10
    tabla_velocidad = dbc.Table.from_dataframe(
        top_crecimiento["Top_crecimeinto_velocidad (Mbps)"].nlargest(3, 'Tasa_de_crecimiento_vel_media').rename(
            columns={"Tasa_de_crecimiento_vel_media": "Velocidad Media (%)"}
        ),
        striped=True,
        bordered=True,
        hover=True,
    )
    tabla_hogar = dbc.Table.from_dataframe(
        top_crecimiento["Top_crecimiento_penetracion_hogar (%)"].nlargest(3, 'Tasa_de_crecimiento_penetracion_hogar').rename(
            columns={"Tasa_de_crecimiento_penetracion_hogar": "Penetracion Hogar (%)"}
        ),
        striped=True,
        bordered=True,
        hover=True
    )
    tabla_poblacion = dbc.Table.from_dataframe(
        top_crecimiento["Top_crecimiento_penetracion_poblacion (%)"].nlargest(3, 'Tasa_de_crecimiento_penetracion_poblacion').rename(
            columns={"Tasa_de_crecimiento_penetracion_poblacion": "Penetracion Poblacion (%)"}
        ),
        striped=True,
        bordered=True,
        hover=True
    )

    # Gráfico Comparativo
    fig_comparacion = px.bar(
        resumen_crecimiento.melt(
            id_vars=["Provincia"],
            value_vars=["Tasa_de_crecimiento_vel_media", "Tasa_de_crecimiento_penetracion_hogar", "Tasa_de_crecimiento_penetracion_poblacion"],
            var_name="Métrica",
            value_name="Tasa de Crecimiento"
        ),
        x="Provincia",
        y="Tasa de Crecimiento",
        color="Métrica",
        barmode="group",
        title="Comparación de Crecimiento Promedio por Provincia"
    )

    # Gráfico de Distribución
    fig_distribucion = px.box(
        resumen_crecimiento.melt(
            id_vars=["Provincia"],
            value_vars=["Tasa_de_crecimiento_vel_media", "Tasa_de_crecimiento_penetracion_hogar", "Tasa_de_crecimiento_penetracion_poblacion"],
            var_name="Métrica",
            value_name="Tasa de Crecimiento"
        ),
        x="Métrica",
        y="Tasa de Crecimiento",
        title="Distribución de Crecimientos por Métrica"
    )

    return tabla_velocidad, tabla_hogar, tabla_poblacion, fig_comparacion, fig_distribucion

@app.callback(
    [
        Output("grafico-kpi-penetracion", "figure"),
        Output("grafico-tendencia-penetracion", "figure"),
        Output("grafico-kpi-velocidad", "figure"),
        Output("graficas-tendencia-provincias", "children")
    ],
    [Input("tabs", "value")]
)
def update_tab5_content(tab):
    if tab != "tab5":
        raise dash.exceptions.PreventUpdate

    # Crear gráficos para KPI de penetración
    fig_kpi_penetracion = crear_grafico_kpi_penetracion(kpi_mean)
    fig_tendencia_penetracion = crear_grafico_tendencia_penetracion(
        penetracion_hogar_estimado_mean, 
        penetracion_hogar_simulado_mean
    )

    # Crear gráficos para KPI de velocidad
    fig_kpi_velocidad = crear_grafico_kpi_velocidad(kpi_mean_provincia)

    # Crear gráficos de tendencias para cada provincia
    provincias_graficas = []
    for provincia in velocidad_media_proyectado["Provincia"].unique():
        provincia_data = velocidad_media_proyectado[velocidad_media_proyectado["Provincia"] == provincia]
        provincias_graficas.append(
            html.Div([
                html.H5(f"Provincia: {provincia}"),
                dcc.Graph(figure=crear_grafico_tendencia_velocidad(provincia_data))
            ])
        )

    return fig_kpi_penetracion, fig_tendencia_penetracion, fig_kpi_velocidad, provincias_graficas



if __name__ == "__main__":
    app.run_server(debug=True)
