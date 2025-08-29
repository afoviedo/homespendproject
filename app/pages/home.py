"""
Home Page - Resumen Financiero Mejorado
Dashboard principal con gráficos, tablas y filtros avanzados
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from dash import html, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc
from typing import Dict, Any, Optional


def create_layout(df: Optional[pd.DataFrame] = None, kpis: Dict[str, Any] = None) -> html.Div:
    """Create enhanced home page layout with charts, tables and filters"""
    
    if df is None or df.empty:
        return create_empty_state()
    
    # Get unique responsibles for filter
    responsibles = ["Todos"] + sorted(df['Responsible'].unique().tolist())
    
    # Calculate date range
    min_date = pd.to_datetime(df['Date']).min().date()
    max_date = pd.to_datetime(df['Date']).max().date()
    
    layout = dbc.Container([
        # Header
        dbc.Row([
            dbc.Col([
                html.H2([
                    html.I(className="fas fa-chart-bar me-3"),
                    "📊 RESUMEN FINANCIERO"
                ], className="mb-0"),
                html.P("Dashboard principal con indicadores clave", className="text-muted")
            ])
        ], className="mb-4"),
        
        # KPI Cards (existing)
        dbc.Row([
            dbc.Col([
                create_kpi_card(
                    "Gasto Total (Mes Actual)",
                    f"₡{kpis.get('total_amount', 0):,.0f}",
                    kpis.get('vs_previous_month', 0),
                    "fas fa-wallet",
                    "primary"
                )
            ], width=12, lg=3),
            dbc.Col([
                create_kpi_card(
                    "# Transacciones", 
                    f"{kpis.get('total_transactions', 0)}",
                    None,
                    "fas fa-list",
                    "info"
                )
            ], width=12, lg=3),
            dbc.Col([
                create_kpi_card(
                    "Ticket Promedio",
                    f"₡{kpis.get('avg_amount', 0):,.0f}",
                    None,
                    "fas fa-receipt",
                    "success"
                )
            ], width=12, lg=3),
            dbc.Col([
                create_kpi_card(
                    "vs Mes Anterior",
                    f"+{kpis.get('vs_previous_month', 0):.1f}%",
                    kpis.get('vs_previous_month', 0),
                    "fas fa-chart-line",
                    "warning"
                )
            ], width=12, lg=3),
        ], className="mb-4"),
        
        # Filters Row
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5([
                            html.I(className="fas fa-filter me-2"),
                            "🔧 Filtros"
                        ], className="mb-0")
                    ]),
                    dbc.CardBody([
                        dbc.Row([
                            # Date Range Filter
                            dbc.Col([
                                html.Label("📅 Rango de Fechas:", className="fw-bold mb-2"),
                                dcc.DatePickerRange(
                                    id="date-range-picker",
                                    start_date=min_date,
                                    end_date=max_date,
                                    display_format='DD/MM/YYYY',
                                    style={'width': '100%'}
                                )
                            ], width=12, lg=4),
                            
                            # Responsible Filter
                            dbc.Col([
                                html.Label("👤 Responsable:", className="fw-bold mb-2"),
                                dcc.Dropdown(
                                    id="responsible-filter",
                                    options=[{"label": r, "value": r} for r in responsibles],
                                    value="Todos",
                                    clearable=False
                                )
                            ], width=12, lg=4),
                            
                            # Chart Period Filter
                            dbc.Col([
                                html.Label("📊 Período del Gráfico:", className="fw-bold mb-2"),
                                dcc.Dropdown(
                                    id="chart-period-filter",
                                    options=[
                                        {"label": "Por Día", "value": "daily"},
                                        {"label": "Por Semana (ISO)", "value": "weekly"},
                                        {"label": "Por Mes", "value": "monthly"}
                                    ],
                                    value="monthly",
                                    clearable=False
                                )
                            ], width=12, lg=4),
                        ])
                    ])
                ])
            ])
        ], className="mb-4"),
        
        # Charts Row
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5([
                            html.I(className="fas fa-chart-line me-2"),
                            "📈 Evolución de Gastos en el Tiempo"
                        ], className="mb-0")
                    ]),
                    dbc.CardBody([
                        dcc.Loading(
                            dcc.Graph(id="time-series-chart"),
                            type="default"
                        )
                    ])
                ])
            ])
        ], className="mb-4"),
        
        # Tables Row
        dbc.Row([
            # Last 10 Transactions
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5([
                            html.I(className="fas fa-clock me-2"),
                            "🕒 Últimas 10 Transacciones"
                        ], className="mb-0")
                    ]),
                    dbc.CardBody([
                        html.Div(id="last-transactions-table")
                    ])
                ])
            ], width=12, lg=6),
            
            # Top 5 Transactions
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5([
                            html.I(className="fas fa-trophy me-2"),
                            "🏆 Top 5 Transacciones Más Altas"
                        ], className="mb-0")
                    ]),
                    dbc.CardBody([
                        html.Div(id="top-transactions-table")
                    ])
                ])
            ], width=12, lg=6),
        ], className="mb-4"),
        
        # Data stores
        dcc.Store(id="home-data-store"),
        dcc.Store(id="filtered-data-store"),
        
    ], fluid=True)
    
    return layout


def create_empty_state() -> html.Div:
    """Create empty state when no data is available"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                dbc.Alert([
                    html.H4([
                        html.I(className="fas fa-info-circle me-2"),
                        "📊 Datos del Mes Actual"
                    ], className="alert-heading"),
                    html.P("No hay datos disponibles para mostrar el resumen financiero."),
                    html.Hr(),
                    html.P("Verifica tu conexión a OneDrive o contacta al administrador.", className="mb-0")
                ], color="info")
            ])
        ], className="mt-5")
    ], fluid=True)


def create_kpi_card(title: str, value: str, delta: float = None, 
                   icon: str = "fas fa-chart-line", color: str = "primary") -> dbc.Card:
    """Create KPI card with icon and delta"""
    
    # Determine delta color and icon
    delta_color = "success" if delta and delta > 0 else "danger" if delta and delta < 0 else "secondary"
    delta_icon = "fa-arrow-up" if delta and delta > 0 else "fa-arrow-down" if delta and delta < 0 else "fa-minus"
    delta_text = f"{delta:+.1f}%" if delta is not None else ""
    
    card_body = [
        dbc.Row([
            dbc.Col([
                html.H4(value, className="mb-0 fw-bold"),
                html.P(title, className="text-muted mb-0"),
            ], width=8),
            dbc.Col([
                html.I(className=f"{icon} fa-2x text-{color}")
            ], width=4, className="text-end")
        ]),
    ]
    
    if delta is not None:
        card_body.append(html.Hr(className="my-2"))
        card_body.append(
            html.Small([
                html.I(className=f"fas {delta_icon} text-{delta_color} me-1"),
                html.Span(delta_text, className=f"text-{delta_color}")
            ], className="text-muted")
        )
    
    return dbc.Card(
        dbc.CardBody(card_body),
        className="h-100 shadow-sm"
    )


# Callbacks for the home page
@callback(
    Output("filtered-data-store", "data"),
    [Input("date-range-picker", "start_date"),
     Input("date-range-picker", "end_date"),
     Input("responsible-filter", "value")],
    [State("home-data-store", "data")]
)
def filter_data(start_date, end_date, responsible, data):
    """Filter data based on date range and responsible"""
    if not data or not data.get('processed_data'):
        return {}
    
    df = pd.DataFrame(data['processed_data'])
    
    # Convert dates
    df['Date'] = pd.to_datetime(df['Date'])
    if start_date:
        df = df[df['Date'] >= pd.to_datetime(start_date)]
    if end_date:
        df = df[df['Date'] <= pd.to_datetime(end_date)]
    
    # Filter by responsible
    if responsible and responsible != "Todos":
        df = df[df['Responsible'] == responsible]
    
    return {
        'filtered_data': df.to_dict('records'),
        'start_date': start_date,
        'end_date': end_date,
        'responsible': responsible
    }


@callback(
    Output("time-series-chart", "figure"),
    [Input("filtered-data-store", "data"),
     Input("chart-period-filter", "value")]
)
def update_time_series_chart(filtered_data, period):
    """Update time series chart based on filtered data and period"""
    if not filtered_data or not filtered_data.get('filtered_data'):
        return create_empty_chart()
    
    df = pd.DataFrame(filtered_data['filtered_data'])
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Group by period
    if period == "daily":
        df_grouped = df.groupby(df['Date'].dt.date)['Amount'].sum().reset_index()
        title = "Gastos por Día"
        x_title = "Fecha"
    elif period == "weekly":
        df['Week'] = df['Date'].dt.isocalendar().week
        df['Year'] = df['Date'].dt.year
        df['WeekYear'] = df['Year'].astype(str) + "-W" + df['Week'].astype(str).str.zfill(2)
        df_grouped = df.groupby('WeekYear')['Amount'].sum().reset_index()
        df_grouped.columns = ['Date', 'Amount']
        title = "Gastos por Semana (ISO)"
        x_title = "Semana"
    else:  # monthly
        df['Month'] = df['Date'].dt.to_period('M')
        df_grouped = df.groupby('Month')['Amount'].sum().reset_index()
        df_grouped['Date'] = df_grouped['Month'].astype(str)
        title = "Gastos por Mes"
        x_title = "Mes"
    
    # Create chart
    fig = px.line(
        df_grouped, 
        x='Date', 
        y='Amount',
        title=title,
        labels={'Amount': 'Monto (₡)', 'Date': x_title}
    )
    
    # Customize chart
    fig.update_traces(
        line=dict(width=3),
        marker=dict(size=8)
    )
    
    fig.update_layout(
        template="plotly_white",
        height=400,
        xaxis_title=x_title,
        yaxis_title="Monto (₡)",
        hovermode='x unified'
    )
    
    # Format y-axis as currency
    fig.update_yaxis(tickformat='₡,.0f')
    
    return fig


@callback(
    Output("last-transactions-table", "children"),
    Input("filtered-data-store", "data")
)
def update_last_transactions_table(filtered_data):
    """Update last 10 transactions table"""
    if not filtered_data or not filtered_data.get('filtered_data'):
        return html.P("No hay transacciones disponibles", className="text-muted text-center")
    
    df = pd.DataFrame(filtered_data['filtered_data'])
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Get last 10 transactions
    df_last = df.nlargest(10, 'Date')
    
    # Create table
    table = dbc.Table.from_dataframe(
        df_last[['Date', 'Description', 'Amount', 'Responsible', 'Card']].round(0),
        striped=True,
        bordered=True,
        hover=True,
        responsive=True,
        size='sm'
    )
    
    return table


@callback(
    Output("top-transactions-table", "children"),
    Input("filtered-data-store", "data")
)
def update_top_transactions_table(filtered_data):
    """Update top 5 highest transactions table"""
    if not filtered_data or not filtered_data.get('filtered_data'):
        return html.P("No hay transacciones disponibles", className="text-muted text-center")
    
    df = pd.DataFrame(filtered_data['filtered_data'])
    
    # Get top 5 highest transactions
    df_top = df.nlargest(5, 'Amount')
    
    # Create table
    table = dbc.Table.from_dataframe(
        df_top[['Date', 'Description', 'Amount', 'Responsible']].round(0),
        striped=True,
        bordered=True,
        hover=True,
        responsive=True,
        size='sm'
    )
    
    return table


def create_empty_chart():
    """Create empty chart when no data is available"""
    fig = go.Figure()
    fig.add_annotation(
        text="No hay datos disponibles para el período seleccionado",
        xref="paper", yref="paper",
        x=0.5, y=0.5, xanchor='center', yanchor='middle',
        showarrow=False,
        font=dict(size=16, color="gray")
    )
    fig.update_layout(
        template="plotly_white",
        height=400,
        xaxis=dict(showgrid=False, showticklabels=False),
        yaxis=dict(showgrid=False, showticklabels=False)
    )
    return fig