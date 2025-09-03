"""
Transactions Page - Vista de todas las transacciones con filtros avanzados
"""

import pandas as pd
from dash import html, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc
from typing import Optional
from datetime import datetime, timedelta


def create_layout(df: Optional[pd.DataFrame] = None) -> html.Div:
    """Create transactions page layout with filters and data table"""
    
    if df is None or df.empty:
        return dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H2([
                        html.I(className="fas fa-list me-3"),
                        "TRANSACCIONES"
                    ], className="mb-0"),
                    html.P("Vista detallada de todas las transacciones", className="text-muted")
                ])
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Alert([
                        html.H4("No hay datos disponibles", className="alert-heading"),
                        html.P("No se encontraron transacciones para mostrar. Verifica que los datos estén cargados correctamente.")
                    ], color="warning")
                ])
            ])
        ], fluid=True)
    
    # Get unique values for filters
    categories = sorted(df['Category'].unique()) if 'Category' in df.columns else []
    responsibles = sorted(df['Responsible'].unique()) if 'Responsible' in df.columns else []
    
    # Date range defaults - handle both string and datetime formats
    if not df.empty:
        min_date_obj = df['Date'].min()
        max_date_obj = df['Date'].max()
        
        # Convert to string if it's a datetime object
        if hasattr(min_date_obj, 'strftime'):
            min_date = min_date_obj.strftime('%Y-%m-%d')
        else:
            min_date = str(min_date_obj)
            
        if hasattr(max_date_obj, 'strftime'):
            max_date = max_date_obj.strftime('%Y-%m-%d')
        else:
            max_date = str(max_date_obj)
    else:
        min_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        max_date = datetime.now().strftime('%Y-%m-%d')
    
    return dbc.Container([
        # Header
        dbc.Row([
            dbc.Col([
                html.H2([
                    html.I(className="fas fa-list me-3"),
                    "TRANSACCIONES"
                ], className="mb-0"),
                html.P(f"Vista detallada de {len(df)} transacciones", className="text-muted")
            ])
        ], className="mb-4"),
        
        # Filters Section
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("🔍 Filtros", className="card-title mb-3"),
                        dbc.Row([
                            # Category Filter
                            dbc.Col([
                                html.Label("Categorías:", className="fw-bold mb-2"),
                                dcc.Dropdown(
                                    id="transactions-category-filter",
                                    options=[{"label": cat, "value": cat} for cat in categories],
                                    value=[],  # Empty list for multi-select
                                    multi=True,
                                    placeholder="Selecciona categorías (vacío = todas)"
                                )
                            ], width=12, lg=4),
                            
                            # Responsible Filter
                            dbc.Col([
                                html.Label("Responsables:", className="fw-bold mb-2"),
                                dcc.Dropdown(
                                    id="transactions-responsible-filter",
                                    options=[{"label": resp, "value": resp} for resp in responsibles],
                                    value=[],  # Empty list for multi-select
                                    multi=True,
                                    placeholder="Selecciona responsables (vacío = todos)"
                                )
                            ], width=12, lg=4),
                            
                            # Date Range Filter
                            dbc.Col([
                                html.Label("Rango de Fechas:", className="fw-bold mb-2"),
                                dbc.Row([
                                    dbc.Col([
                                        html.Label("Desde:", className="small text-muted"),
                                        dcc.Input(
                                            id="transactions-start-date",
                                            type="date",
                                            value=min_date,
                                            className="form-control",
                                            style={'width': '100%'}
                                        )
                                    ], width=6),
                                    dbc.Col([
                                        html.Label("Hasta:", className="small text-muted"),
                                        dcc.Input(
                                            id="transactions-end-date",
                                            type="date",
                                            value=max_date,
                                            className="form-control",
                                            style={'width': '100%'}
                                        )
                                    ], width=6)
                                ])
                            ], width=12, lg=4)
                        ], className="mb-3"),
                        
                        # Summary Stats
                        dbc.Row([
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H6("Total Filtrado", className="card-title text-muted"),
                                        html.H4(id="filtered-total", className="text-primary mb-0")
                                    ])
                                ], className="text-center")
                            ], width=3),
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H6("Transacciones", className="card-title text-muted"),
                                        html.H4(id="filtered-count", className="text-success mb-0")
                                    ])
                                ], className="text-center")
                            ], width=3),
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H6("Promedio", className="card-title text-muted"),
                                        html.H4(id="filtered-avg", className="text-info mb-0")
                                    ])
                                ], className="text-center")
                            ], width=3),
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H6("Máximo", className="card-title text-muted"),
                                        html.H4(id="filtered-max", className="text-warning mb-0")
                                    ])
                                ], className="text-center")
                            ], width=3)
                        ])
                    ])
                ], className="shadow mb-4")
            ], width=12)
        ]),
        
        # Data Table
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H5("📊 Tabla de Transacciones", className="card-title mb-3"),
                        html.Div(id="transactions-table-container")
                    ])
                ], className="shadow")
            ], width=12)
        ])
        
    ], fluid=True)


# Callbacks for filtering and table updates
@callback(
    [Output("transactions-table-container", "children"),
     Output("filtered-total", "children"),
     Output("filtered-count", "children"),
     Output("filtered-avg", "children"),
     Output("filtered-max", "children")],
    [Input("transactions-category-filter", "value"),
     Input("transactions-responsible-filter", "value"),
     Input("transactions-start-date", "value"),
     Input("transactions-end-date", "value"),
     Input("transactions-data-store", "data")],  # Add data store as input to trigger on data change
    [State("transactions-data-store", "data")]
)
def update_transactions_table(categories, responsibles, start_date, end_date, data, data_state):
    """Update transactions table based on filters"""
    
    # Use data_state if data is None (initial load)
    if data is None:
        data = data_state
    
    if not data or not data.get('processed_data'):
        return html.Div("No hay datos disponibles"), "₡0", "0", "₡0", "₡0"
    
    df = pd.DataFrame(data['processed_data'])
    
    # Apply filters
    if categories and len(categories) > 0:
        df = df[df['Category'].isin(categories)]
    
    if responsibles and len(responsibles) > 0:
        df = df[df['Responsible'].isin(responsibles)]
    
    if start_date and end_date:
        df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
    
    # Calculate stats
    total_amount = df['Amount'].sum() if not df.empty else 0
    transaction_count = len(df) if not df.empty else 0
    avg_amount = df['Amount'].mean() if not df.empty else 0
    max_amount = df['Amount'].max() if not df.empty else 0
    
    # Format stats
    total_formatted = f"₡{total_amount:,.0f}"
    count_formatted = f"{transaction_count:,}"
    avg_formatted = f"₡{avg_amount:,.0f}"
    max_formatted = f"₡{max_amount:,.0f}"
    
    # Create table
    if df.empty:
        table = html.Div([
            dbc.Alert([
                html.H6("No hay transacciones que coincidan con los filtros seleccionados", className="alert-heading"),
                html.P("Intenta ajustar los criterios de búsqueda.")
            ], color="info")
        ])
    else:
        # Sort by date (most recent first)
        df_sorted = df.sort_values('Date', ascending=False)
        
        # Create table rows
        table_rows = []
        for _, row in df_sorted.head(100).iterrows():  # Limit to 100 rows for performance
            table_rows.append(
                html.Tr([
                    html.Td(row['Date'], className="text-nowrap"),
                    html.Td(row['Description'], className="text-truncate"),
                    html.Td(row['Category'], className="text-nowrap"),
                    html.Td(row['Responsible'], className="text-truncate"),
                    html.Td(f"₡{row['Amount']:,.0f}", className="text-end fw-bold"),
                    html.Td(row['Card'], className="text-nowrap")
                ])
            )
        
        table = dbc.Table([
            html.Thead([
                html.Tr([
                    html.Td("Fecha", className="text-nowrap fw-bold"),
                    html.Td("Descripción", className="text-nowrap fw-bold"),
                    html.Td("Categoría", className="text-nowrap fw-bold"),
                    html.Td("Responsable", className="text-nowrap fw-bold"),
                    html.Td("Monto", className="text-end text-nowrap fw-bold"),
                    html.Td("Tarjeta", className="text-nowrap fw-bold")
                ])
            ]),
            html.Tbody(table_rows)
        ], striped=True, hover=True, responsive=True, className="table-sm")
    
    return table, total_formatted, count_formatted, avg_formatted, max_formatted


# Initial callback to populate table when page loads
@callback(
    Output("transactions-table-container", "children", allow_duplicate=True),
    Input("transactions-data-store", "data"),
    prevent_initial_call='initial_duplicate'
)
def initial_table_load(data):
    """Load table initially when data becomes available"""
    
    if not data or not data.get('processed_data'):
        return html.Div("Cargando datos...", className="text-center text-muted")
    
    df = pd.DataFrame(data['processed_data'])
    
    if df.empty:
        return html.Div([
            dbc.Alert([
                html.H6("No hay transacciones disponibles", className="alert-heading"),
                html.P("No se encontraron datos para mostrar.")
            ], color="warning")
        ])
    
    # Sort by date (most recent first)
    df_sorted = df.sort_values('Date', ascending=False)
    
    # Create table rows
    table_rows = []
    for _, row in df_sorted.head(100).iterrows():  # Limit to 100 rows for performance
        table_rows.append(
            html.Tr([
                html.Td(row['Date'], className="text-nowrap"),
                html.Td(row['Description'], className="text-truncate"),
                html.Td(row['Category'], className="text-nowrap"),
                html.Td(row['Responsible'], className="text-nowrap"),
                html.Td(f"₡{row['Amount']:,.0f}", className="text-end fw-bold"),
                html.Td(row['Card'], className="text-nowrap")
            ])
        )
    
    table = dbc.Table([
        html.Thead([
            html.Tr([
                html.Td("Fecha", className="text-nowrap fw-bold"),
                html.Td("Descripción", className="text-nowrap fw-bold"),
                html.Td("Categoría", className="text-nowrap fw-bold"),
                html.Td("Responsable", className="text-nowrap fw-bold"),
                html.Td("Monto", className="text-end text-nowrap fw-bold"),
                html.Td("Tarjeta", className="text-nowrap fw-bold")
            ])
        ]),
        html.Tbody(table_rows)
    ], striped=True, hover=True, responsive=True, className="table-sm")
    
    return table