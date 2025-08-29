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
        
        # KPI Cards (dynamic - will update with filters)
        dbc.Row(id="kpi-cards-row", className="mb-4"),
        
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
                            
                            # Responsible Filter (Multi-select)
                            dbc.Col([
                                html.Label("👤 Responsables:", className="fw-bold mb-2"),
                                dcc.Dropdown(
                                    id="responsible-filter",
                                    options=[{"label": r, "value": r} for r in responsibles if r != "Todos"],
                                    value=[],  # Empty list for multi-select
                                    multi=True,
                                    placeholder="Selecciona responsables (vacío = todos)"
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
            # Time series chart
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
            ], width=12, lg=6),
            
            # Category chart  
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5([
                            html.I(className="fas fa-chart-bar me-2"),
                            "📊 Gastos por Categoría"
                        ], className="mb-0")
                    ]),
                    dbc.CardBody([
                        dcc.Loading(
                            dcc.Graph(id="category-chart"),
                            type="default"
                        )
                    ])
                ])
            ], width=12, lg=6),
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
        dcc.Store(id="home-data-store", data={'processed_data': df.to_dict('records')} if df is not None and not df.empty else {'processed_data': []}),
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
    Output("kpi-cards-row", "children"),
    Input("filtered-data-store", "data")
)
def update_kpi_cards(filtered_data):
    """Update KPI cards based on filtered data"""
    print(f"KPI cards callback triggered")
    
    if not filtered_data or not filtered_data.get('filtered_data'):
        print("No filtered data for KPI cards")
        return create_default_kpi_cards()
    
    try:
        df = pd.DataFrame(filtered_data['filtered_data'])
        print(f"KPI cards data: {len(df)} records")
        
        if df.empty:
            return create_default_kpi_cards()
        
        # Calculate filtered KPIs
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
        df = df.dropna(subset=['Amount'])
        
        total_amount = df['Amount'].sum()
        total_transactions = len(df)
        avg_amount = total_amount / total_transactions if total_transactions > 0 else 0
        
        # Create updated cards
        cards = [
            dbc.Col([
                create_kpi_card(
                    "Gasto Total (Filtrado)",
                    f"₡{total_amount:,.0f}",
                    None,
                    "fas fa-wallet",
                    "primary"
                )
            ], width=12, lg=3),
            dbc.Col([
                create_kpi_card(
                    "# Transacciones", 
                    f"{total_transactions}",
                    None,
                    "fas fa-list",
                    "info"
                )
            ], width=12, lg=3),
            dbc.Col([
                create_kpi_card(
                    "Ticket Promedio",
                    f"₡{avg_amount:,.0f}",
                    None,
                    "fas fa-receipt",
                    "success"
                )
            ], width=12, lg=3),
            dbc.Col([
                create_kpi_card(
                    "Período Filtrado",
                    f"{filtered_data.get('start_date', 'N/A')} - {filtered_data.get('end_date', 'N/A')}",
                    None,
                    "fas fa-calendar",
                    "warning"
                )
            ], width=12, lg=3),
        ]
        
        return cards
        
    except Exception as e:
        print(f"Error updating KPI cards: {e}")
        return create_default_kpi_cards()


def create_default_kpi_cards():
    """Create default KPI cards when no data is available"""
    return [
        dbc.Col([
            create_kpi_card(
                "Gasto Total",
                "₡0",
                None,
                "fas fa-wallet",
                "primary"
            )
        ], width=12, lg=3),
        dbc.Col([
            create_kpi_card(
                "# Transacciones", 
                "0",
                None,
                "fas fa-list",
                "info"
            )
        ], width=12, lg=3),
        dbc.Col([
            create_kpi_card(
                "Ticket Promedio",
                "₡0",
                None,
                "fas fa-receipt",
                "success"
            )
        ], width=12, lg=3),
        dbc.Col([
            create_kpi_card(
                "Sin Filtros",
                "Selecciona filtros",
                None,
                "fas fa-filter",
                "warning"
            )
        ], width=12, lg=3),
    ]


@callback(
    Output("filtered-data-store", "data"),
    [Input("date-range-picker", "start_date"),
     Input("date-range-picker", "end_date"),
     Input("responsible-filter", "value"),
     Input("home-data-store", "data")]
)
def filter_data(start_date, end_date, responsible, data):
    """Filter data based on date range and responsible"""
    print(f"Filter callback triggered with data: {data is not None}")
    
    if not data or not data.get('processed_data'):
        print("No data available for filtering")
        return {'filtered_data': []}
    
    try:
        df = pd.DataFrame(data['processed_data'])
        print(f"Original data: {len(df)} records")
        
        if df.empty:
            print("DataFrame is empty")
            return {'filtered_data': []}
        
        # Verify required columns exist
        required_columns = ['Date', 'Amount', 'Responsible']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"Missing required columns: {missing_columns}")
            return {'filtered_data': []}
        
        # Convert dates
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date'])  # Remove rows with invalid dates
        
        if start_date:
            df = df[df['Date'] >= pd.to_datetime(start_date)]
            print(f"After start date filter: {len(df)} records")
        if end_date:
            df = df[df['Date'] <= pd.to_datetime(end_date)]
            print(f"After end date filter: {len(df)} records")
        
        # Filter by responsible (multi-select logic)
        if responsible and len(responsible) > 0:
            df = df[df['Responsible'].isin(responsible)]
            print(f"After responsible filter ({len(responsible)} selected): {len(df)} records")
        else:
            print(f"No responsible filter applied (showing all): {len(df)} records")
        
        result = {
            'filtered_data': df.to_dict('records'),
            'start_date': start_date,
            'end_date': end_date,
            'responsible': responsible
        }
        
        print(f"Returning filtered data: {len(result['filtered_data'])} records")
        return result
        
    except Exception as e:
        print(f"Error in filter_data: {e}")
        return {'filtered_data': []}


@callback(
    Output("time-series-chart", "figure"),
    [Input("filtered-data-store", "data"),
     Input("chart-period-filter", "value"),
     Input("theme-store", "data")]
)
def update_time_series_chart(filtered_data, period, theme):
    """Update time series chart based on filtered data, period and theme"""
    print(f"Chart callback triggered with period: {period}")
    print(f"Filtered data available: {filtered_data is not None}")
    
    if not filtered_data or not filtered_data.get('filtered_data'):
        print("No filtered data available for chart")
        return create_empty_chart(theme=theme)
    
    df = pd.DataFrame(filtered_data['filtered_data'])
    print(f"Chart data: {len(df)} records")
    
    if df.empty:
        print("DataFrame is empty")
        return create_empty_chart(theme=theme)
    
    # Ensure required columns and data types
    required_columns = ['Date', 'Amount']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"Missing required columns for chart: {missing_columns}")
        return create_empty_chart(theme=theme)
    
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
    
    # Remove rows with invalid data
    df = df.dropna(subset=['Date', 'Amount'])
    
    if df.empty:
        print("No valid data after cleaning")
        return create_empty_chart(theme=theme)
    
    # Group by period
    try:
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
        
        print(f"Grouped data: {len(df_grouped)} points")
        
        if df_grouped.empty:
            return create_empty_chart(theme=theme)
        
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
        
        # Customize chart with dynamic theme
        chart_template = "plotly_dark" if theme == "dark" else "plotly_white"
        
        fig.update_layout(
            template=chart_template,
            height=400,
            xaxis_title=x_title,
            yaxis_title="Monto (₡)",
            hovermode='x unified',
            yaxis=dict(tickformat='₡,.0f'),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig
        
    except Exception as e:
        print(f"Error creating chart: {e}")
        return create_empty_chart(theme=theme)


@callback(
    Output("category-chart", "figure"),
    [Input("filtered-data-store", "data"),
     Input("theme-store", "data")]
)
def update_category_chart(filtered_data, theme):
    """Update category chart based on filtered data and theme"""
    print(f"Category chart callback triggered")
    
    if not filtered_data or not filtered_data.get('filtered_data'):
        print("No filtered data available for category chart")
        return create_empty_chart("No hay datos disponibles para mostrar categorías", theme=theme)
    
    df = pd.DataFrame(filtered_data['filtered_data'])
    print(f"Category chart data: {len(df)} records")
    
    if df.empty:
        print("DataFrame is empty for category chart")
        return create_empty_chart("No hay datos en el período seleccionado", theme=theme)
    
    try:
        # Ensure required columns and data types
        required_columns = ['Description', 'Amount']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"Missing required columns for category chart: {missing_columns}")
            return create_empty_chart("Error: Columnas faltantes en los datos", theme=theme)
        
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
        df = df.dropna(subset=['Amount'])
        
        if df.empty:
            print("No valid data after cleaning for category chart")
            return create_empty_chart("No hay datos válidos para mostrar", theme=theme)
        
        # Use Description as category (Business column)
        df_grouped = df.groupby('Description')['Amount'].sum().reset_index()
        df_grouped = df_grouped.sort_values('Amount', ascending=True)  # Sort for better visualization
        
        print(f"Category grouped data: {len(df_grouped)} categories")
        
        if df_grouped.empty:
            return create_empty_chart("No hay categorías para mostrar", theme=theme)
        
        # Create horizontal bar chart
        fig = px.bar(
            df_grouped, 
            x='Amount', 
            y='Description',
            orientation='h',
            title="Gastos por Categoría",
            labels={'Amount': 'Monto (₡)', 'Description': 'Categoría'},
            color='Amount',
            color_continuous_scale='Blues'
        )
        
        # Customize chart with dynamic theme
        chart_template = "plotly_dark" if theme == "dark" else "plotly_white"
        
        fig.update_layout(
            template=chart_template,
            height=400,
            xaxis_title="Monto (₡)",
            yaxis_title="Categoría",
            showlegend=False,
            margin=dict(l=150, r=50, t=50, b=50),  # More left margin for category names
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        # Format x-axis as currency
        fig.update_xaxes(tickformat='₡,.0f')
        
        return fig
        
    except Exception as e:
        print(f"Error creating category chart: {e}")
        return create_empty_chart("Error al procesar datos de categorías", theme=theme)


@callback(
    Output("last-transactions-table", "children"),
    Input("filtered-data-store", "data")
)
def update_last_transactions_table(filtered_data):
    """Update last 10 transactions table"""
    print(f"Last transactions callback triggered")
    
    if not filtered_data or not filtered_data.get('filtered_data'):
        print("No filtered data for last transactions table")
        return html.P("No hay transacciones disponibles", className="text-muted text-center")
    
    df = pd.DataFrame(filtered_data['filtered_data'])
    print(f"Last transactions data: {len(df)} records")
    
    if df.empty:
        return html.P("No hay transacciones en el período seleccionado", className="text-muted text-center")
    
    try:
        # Verify required columns
        required_columns = ['Date', 'Description', 'Amount', 'Responsible']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"Missing columns for last transactions: {missing_columns}")
            return html.P("Error: Columnas faltantes en los datos", className="text-muted text-center")
        
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
        
        # Remove rows with invalid data
        df = df.dropna(subset=['Date', 'Amount'])
        
        if df.empty:
            return html.P("No hay transacciones válidas en el período seleccionado", className="text-muted text-center")
        
        # Get last 10 transactions
        df_last = df.nlargest(10, 'Date')
        
        # Format the data for display
        df_display = df_last.copy()
        df_display['Date'] = df_display['Date'].dt.strftime('%d/%m/%Y')
        df_display['Amount'] = df_display['Amount'].apply(lambda x: f"₡{x:,.0f}")
        
    except Exception as e:
        print(f"Error formatting last transactions: {e}")
        return html.P("Error al procesar las transacciones", className="text-muted text-center")
    
    # Create table
    table = dbc.Table.from_dataframe(
        df_display[['Date', 'Description', 'Amount', 'Responsible', 'Card']],
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
    print(f"Top transactions callback triggered")
    
    if not filtered_data or not filtered_data.get('filtered_data'):
        print("No filtered data for top transactions table")
        return html.P("No hay transacciones disponibles", className="text-muted text-center")
    
    df = pd.DataFrame(filtered_data['filtered_data'])
    print(f"Top transactions data: {len(df)} records")
    
    if df.empty:
        return html.P("No hay transacciones en el período seleccionado", className="text-muted text-center")
    
    try:
        # Verify required columns
        required_columns = ['Date', 'Description', 'Amount', 'Responsible']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"Missing columns for top transactions: {missing_columns}")
            return html.P("Error: Columnas faltantes en los datos", className="text-muted text-center")
        
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        
        # Remove rows with invalid data
        df = df.dropna(subset=['Date', 'Amount'])
        
        if df.empty:
            return html.P("No hay transacciones válidas en el período seleccionado", className="text-muted text-center")
        
        # Get top 5 highest transactions
        df_top = df.nlargest(5, 'Amount')
        
        # Format the data for display
        df_display = df_top.copy()
        df_display['Date'] = df_display['Date'].dt.strftime('%d/%m/%Y')
        df_display['Amount'] = df_display['Amount'].apply(lambda x: f"₡{x:,.0f}")
        
    except Exception as e:
        print(f"Error formatting top transactions: {e}")
        return html.P("Error al procesar las transacciones", className="text-muted text-center")
    
    # Create table
    table = dbc.Table.from_dataframe(
        df_display[['Date', 'Description', 'Amount', 'Responsible']],
        striped=True,
        bordered=True,
        hover=True,
        responsive=True,
        size='sm'
    )
    
    return table


def create_empty_chart(message="No hay datos disponibles para el período seleccionado", theme="dark"):
    """Create empty chart when no data is available"""
    fig = go.Figure()
    
    # Dynamic colors based on theme
    text_color = "#ffffff" if theme == "dark" else "#333333"
    chart_template = "plotly_dark" if theme == "dark" else "plotly_white"
    
    fig.add_annotation(
        text=message,
        xref="paper", yref="paper",
        x=0.5, y=0.5, xanchor='center', yanchor='middle',
        showarrow=False,
        font=dict(size=16, color=text_color)
    )
    fig.update_layout(
        template=chart_template,
        height=400,
        xaxis=dict(showgrid=False, showticklabels=False),
        yaxis=dict(showgrid=False, showticklabels=False),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig