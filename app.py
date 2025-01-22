import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output
import pandas as pd
import plotly.express as px
import json
import geopandas as gpd
import plotly.graph_objects as go
from scipy.stats import pearsonr
from sklearn.linear_model import LinearRegression



# Inicializar la app con tema
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
app.title = "Análisis de Acceso a Internet en Argentina"

# Cargar datos

vel_media_provincia = pd.read_csv('./Datasets/vel_media_provincia.csv', parse_dates=['Fecha'])
penetracion_hogar = pd.read_csv('./Datasets/penetracion_hogar.csv', parse_dates=['Fecha'])
penetracion_poblac = pd.read_csv('./Datasets/penetracion_poblac.csv', parse_dates=['Fecha'])
tecnologia_provincia = pd.read_csv('./Datasets/tecnologia_provincia.csv', parse_dates=['Fecha'])



# Cargar GeoJSON y procesar datos
geojson_path = './Mapas/map.geojson'
gdf = gpd.read_file(geojson_path)
gdf["Provincia"] = gdf["nombre"]
gdf = gdf.merge(vel_media_provincia, on="Provincia", how="left")


# Integrar los datos de tecnologías con velocidad media
data = pd.merge(tecnologia_provincia, vel_media_provincia, on=["Provincia", "Fecha"], how="inner")

# Calcular la proporción de cada tecnología en el total por provincia
tecnologias = ["ADSL", "Cablemodem", "Fibra óptica", "Wireless", "Otros"]
for tecnologia in tecnologias:
    data[f"prop_{tecnologia}"] = data[tecnologia] / data["Total"]

# Análisis por tecnología predominante
data["Tecnologia_Predominante"] = data[tecnologias].idxmax(axis=1)

# Merge de datasets para análisis estadístico
merged_data = pd.merge(penetracion_hogar, penetracion_poblac, on=["Provincia", "Fecha"], how="inner")
merged_data = pd.merge(merged_data, tecnologia_provincia, on=["Provincia", "Fecha"], how="inner")
merged_data = pd.merge(merged_data, vel_media_provincia, on=["Provincia", "Fecha"], how="inner")
merged_data.rename(columns={
    "Accesos por cada 100 hogares": "Penetración_hogar",
    "Accesos por cada 100 hab": "Penetración_población",
    "Mbps (Media de bajada)": "Velocidad_media"
}, inplace=True)

# Función para crear el mapa interactivo
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
        colorbar=dict(title='Mbps (Media de bajada)'),
        hoverinfo='text',
        text=gdf['Provincia'] + ': ' + gdf["Mbps (Media de bajada)"].astype(str) + ' Mbps',
    ))

    fig_mapa.update_layout(
        mapbox_style="carto-positron",
        mapbox_zoom=3,
        mapbox_center={"lat": -38.4161, "lon": -63.6167},  # Centro de Argentina
        title_text='Velocidad Media de Internet por Provincia',
        margin={"r": 0, "t": 50, "l": 0, "b": 0}
    )
    return fig_mapa

# Layout del dashboard
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Análisis de Acceso a Internet en Argentina", 
                        className="text-center text-primary mb-4"), width=12)
    ]),
    dbc.Row([
        dbc.Col(html.P("Explora patrones temporales, diferencias geográficas y relación con tecnologías en el acceso a internet.", 
                       className="text-center"), width=12)
    ]),
    dbc.Tabs([
        dbc.Tab(label="Tendencias Temporales", tab_id="temporal"),
        dbc.Tab(label="Variaciones Geográficas", tab_id="geografico"),
        dbc.Tab(label="Relación con Tecnologías", tab_id="tecnologias"),
        dbc.Tab(label="Insights Combinados", tab_id="insights"),
        dbc.Tab(label="Analisis Estadisticos", tab_id="analisis")
    ], id="tabs", active_tab="temporal"),
    html.Div(id="tab-content")
], fluid=True)

# Callback para renderizar contenido según pestaña
@app.callback(
    Output("tab-content", "children"),
    Input("tabs", "active_tab")
)
def render_tab_content(active_tab):
    if active_tab == "temporal":
        return dbc.Container([
            dbc.Row([
                dbc.Col(dbc.Button("Reiniciar", id="reset-button", color="primary", className="mb-2"), width=12)
            ]),
            dbc.Row([
                # Lado izquierdo: mapa
                dbc.Col([
                    dcc.Graph(id="grafico-mapa", config={"scrollZoom": False}, style={"height": "80vh"})
                ], width=4),
                # Lado derecho: gráficas
                dbc.Col([
                    dbc.Row([
                        dcc.Graph(id="grafico-tendencia", style={"height": "40vh"})
                    ]),
                    dbc.Row([
                        dcc.Graph(id="grafico-crecimiento", style={"height": "40vh"})
                    ])
                ], width=8)
            ])
        ])
    elif active_tab == "geografico":
        return dbc.Container([
            dbc.Row([
                dbc.Col(dcc.Graph(id="mapa-geografico"), width=12)
            ]),
            dbc.Row([
                dbc.Col(html.P("Aquí se mostrarán visualizaciones geográficas adicionales."), width=12)
            ])
        ])
    elif active_tab == "tecnologias":
        return dbc.Container([
            dbc.Row([
                dbc.Col(html.H4("Relación entre Tecnologías y Velocidad Media", className="text-center mb-4"), width=12)
            ]),
            dbc.Row([
                # Gráfico de Barras: Velocidad Media por Tecnología Predominante
                dbc.Col(dcc.Graph(id="barras-tecnologia"), width=6),
                # Gráfico de Líneas: Evolución de las Tecnologías en el Tiempo
                dbc.Col(dcc.Graph(id="lineas-tecnologia"), width=6),
            ]),
            dbc.Row([
                # Mapa Interactivo: Proporción de Tecnologías
                dbc.Col(dcc.Graph(id="mapa-tecnologia"), width=12)
            ]),
            dbc.Row([
                dbc.Col(html.Div(id="resumen-correlaciones"), width=12)
            ])
        ])
    elif active_tab == "insights":
        return dbc.Container([
            dbc.Row([
                dbc.Col(html.H5("Insights Combinados", className="text-center"), width=12),
                dbc.Col(html.P("Aquí se presentarán los análisis combinados de los datos."), width=12)
            ])
        ])
    elif active_tab == "analisis":
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


# Callback para la pestaña de tendencias temporales
@app.callback(
    Output("grafico-mapa", "figure"),
    Output("grafico-tendencia", "figure"),
    Output("grafico-crecimiento", "figure"),
    Input("grafico-mapa", "hoverData"),
    Input("reset-button", "n_clicks")
)
def update_temporal_analysis(hoverData, n_clicks):
    # Crear el mapa interactivo
    fig_mapa = crear_mapa_interactivo()

    # Detectar si se presionó el botón de reinicio
    if n_clicks:
        # Gráfica de tendencia nacional
        promedio_nacional = vel_media_provincia.groupby("Fecha")["Mbps (Media de bajada)"].mean().reset_index()
        fig_tendencia = px.line(
            promedio_nacional,
            x="Fecha",
            y="Mbps (Media de bajada)",
            title="Tendencia Nacional de Velocidad Media",
            labels={"Mbps (Media de bajada)": "Velocidad Media (Mbps)", "Fecha": "Fecha"}
        )

        fig_tendencia.update_layout(
            title={"text": "Tendencia Nacional de Velocidad Media",
                    "x": 0.5,  # Centrado horizontalmente
                    "xanchor": "center",  # Asegura que el anclaje del texto esté en el centro
                    "yanchor": "top"  # Asegura que el anclaje vertical esté en la parte superior
                    })
    elif hoverData:
        # Gráfica de tendencia por provincia
        provincia_hover = gdf.loc[hoverData["points"][0]["location"], "Provincia"]
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
            "xanchor": "center",  # Anclado al centro horizontal
            "yanchor": "top"  # Anclado a la parte superior
        }
    )
    else:
        # Gráfica nacional por defecto
        promedio_nacional = vel_media_provincia.groupby("Fecha")["Mbps (Media de bajada)"].mean().reset_index()
        fig_tendencia = px.line(
            promedio_nacional,
            x="Fecha",
            y="Mbps (Media de bajada)",
            title="Tendencia Nacional de Velocidad Media",
            labels={"Mbps (Media de bajada)": "Velocidad Media (Mbps)", "Fecha": "Fecha"}
        )
        fig_tendencia.update_layout(
            title={"text": "Tendencia Nacional de Velocidad Media",
                    "x": 0.5,  # Centrado horizontalmente
                    "xanchor": "center",  # Asegura que el anclaje del texto esté en el centro
                    "yanchor": "top"  # Asegura que el anclaje vertical esté en la parte superior
                    })

    # Calcular crecimiento porcentual promedio
    vel_media_provincial = vel_media_provincia.pivot(index="Fecha", columns="Provincia", values="Mbps (Media de bajada)")
    vel_media_crecimiento = vel_media_provincial.pct_change().mean() * 100
    vel_media_crecimiento_sorted = vel_media_crecimiento.sort_values(ascending=False)

    # Gráfica de barras del crecimiento porcentual
    fig_crecimiento = px.bar(
        vel_media_crecimiento_sorted,
        x=vel_media_crecimiento_sorted.index,
        y=vel_media_crecimiento_sorted.values,
        title="Crecimiento Promedio de Velocidad Media por Provincia (%)",
        labels={"x": "Provincia", "y": "Crecimiento Promedio (%)"}
    )
    fig_crecimiento.update_traces(marker_color="blue", marker_line_color="black", marker_line_width=1)
    fig_crecimiento.update_layout(
    title={
        "text": "Crecimiento Promedio de Velocidad Media por Provincia (%)",
        "x": 0.5,  # Centrado horizontalmente
        "xanchor": "center",  # Ancla al centro horizontal
        "yanchor": "top"  # Ancla a la parte superior
    },
    xaxis_title="Provincia",
    yaxis_title="Crecimiento Promedio (%)",
    xaxis_tickangle=45,
    margin={"t": 50, "b": 50}
)

    return fig_mapa, fig_tendencia, fig_crecimiento


@app.callback(
    Output("scatter-penetracion-poblacion", "figure"),
    Output("scatter-penetracion-hogar", "figure"),
    Output("tabla-metricas", "children"),
    Input("tabs", "active_tab")
)
def update_analisis_estadistico(active_tab):
    if active_tab != "analisis":
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

# Callback para la pestaña de Relación con Tecnologías
@app.callback(
    Output("barras-tecnologia", "figure"),
    Output("lineas-tecnologia", "figure"),
    Output("mapa-tecnologia", "figure"),
    Output("resumen-correlaciones", "children"),
    Input("tabs", "active_tab")
)
def update_relacion_tecnologias(active_tab):
    if active_tab != "tecnologias":
        raise dash.exceptions.PreventUpdate

    # Análisis de Velocidad Media por Tecnología Predominante
    vel_media_tecnologia = data.groupby("Tecnologia_Predominante")["Mbps (Media de bajada)"].mean().sort_values(ascending=False)
    fig_barras = px.bar(
        vel_media_tecnologia,
        x=vel_media_tecnologia.index,
        y=vel_media_tecnologia.values,
        title="Velocidad Media por Tecnología Predominante",
        labels={"x": "Tecnología", "y": "Velocidad Media (Mbps)"}
    )
    fig_barras.update_layout(title={"x": 0.5}, margin={"t": 50})

    # Evolución del Uso de Tecnologías en el Tiempo
    tech_trend_prop = data.groupby("Fecha")[["prop_ADSL", "prop_Cablemodem", "prop_Fibra óptica", "prop_Wireless", "prop_Otros"]].mean()
    fig_lineas = px.line(
        tech_trend_prop,
        x=tech_trend_prop.index,
        y=tech_trend_prop.columns,
        labels={"value": "Proporción (%)", "Fecha": "Fecha"},
        title="Evolución del Uso de Tecnologías en el Tiempo"
    )
    fig_lineas.update_layout(title={"x": 0.5}, margin={"t": 50})

    # Mapa Interactivo: Proporción de Tecnologías
    gdf = gpd.read_file(geojson_path)
    gdf["Provincia"] = gdf["nombre"]
    data_provincia = data.groupby("Provincia")[[f"prop_{tech}" for tech in ["ADSL", "Cablemodem", "Fibra óptica", "Wireless", "Otros"]]].mean().reset_index()
    gdf = gdf.merge(data_provincia, on="Provincia", how="left")

    fig_mapa = go.Figure()
    for tech in ["prop_ADSL", "prop_Cablemodem", "prop_Fibra óptica", "prop_Wireless", "prop_Otros"]:
        fig_mapa.add_trace(go.Choroplethmapbox(
            geojson=gdf.__geo_interface__,
            locations=gdf.index,
            z=gdf[tech],
            colorscale="Viridis",
            colorbar=dict(title=tech.replace("prop_", "Proporción ")),
            marker_opacity=0.6,
            hoverinfo="text",
            text=gdf["Provincia"] + ": " + gdf[tech].astype(str)
        ))
    fig_mapa.update_layout(mapbox_style="carto-positron", mapbox_zoom=3, mapbox_center={"lat": -38.4161, "lon": -63.6167}, margin={"r": 0, "t": 50, "l": 0, "b": 0})

    # Resumen de Correlaciones
    correlacion_tecnologias = data[["Mbps (Media de bajada)"] + [f"prop_{tech}" for tech in ["ADSL", "Cablemodem", "Fibra óptica", "Wireless", "Otros"]]].corr()
    correlacion_veloc_tecnologia = correlacion_tecnologias.loc["Mbps (Media de bajada)", [f"prop_{tech}" for tech in ["ADSL", "Cablemodem", "Fibra óptica", "Wireless", "Otros"]]]

    resumen = dbc.Table(
        [
            html.Thead(html.Tr([html.Th("Tecnología"), html.Th("Correlación con Velocidad Media")])),
            html.Tbody([
                html.Tr([html.Td(tech.replace("prop_", "")), html.Td(round(correlacion, 2))])
                for tech, correlacion in correlacion_veloc_tecnologia.items()
            ])
        ],
        bordered=True,
        hover=True,
        striped=True
    )

    return fig_barras, fig_lineas, fig_mapa, resumen



# Ejecutar la app
if __name__ == "__main__":
    app.run_server(debug=True)