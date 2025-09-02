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
    
    # Date range defaults
    min_date = df['Date'].min() if not df.empty else (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    max_date = df['Date'].max() if not df.empty else datetime.now().strftime('%Y-%m-%d')
    
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
                                html.Label("Categoría:", className="form-label"),
                                dcc.Dropdown(
                                    id="category-filter",
                                    options=[{"label": "Todas las categorías", "value": "all"}] + 
                                            [{"label": cat, "value": cat} for cat in categories],
                                    value="all",
                                    placeholder="Selecciona una categoría",
                                    clearable=False
                                )
                            ], width=4),
                            
                            # Responsible Filter
                            dbc.Col([
                                html.Label("Responsable:", className="form-label"),
                                dcc.Dropdown(
                                    id="responsible-filter",
                                    options=[{"label": "Todos los responsables", "value": "all"}] + 
                                            [{"label": resp, "value": resp} for resp in responsibles],
                                    value="all",
                                    placeholder="Selecciona un responsable",
                                    clearable=False
                                )
                            ], width=4),
                            
                            # Date Range Filter
                            dbc.Col([
                                html.Label("Rango de Fechas:", className="form-label"),
                                dcc.DatePickerRange(
                                    id="date-range-filter",
                                    start_date=min_date,
                                    end_date=max_date,
                                    display_format='DD/MM/YYYY',
                                    placeholder="Selecciona fechas"
                                )
                            ], width=4)
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
    [Input("category-filter", "value"),
     Input("responsible-filter", "value"),
     Input("date-range-filter", "start_date"),
     Input("date-range-filter", "end_date")],
    [State("transactions-data-store", "data")]
)
def update_transactions_table(category, responsible, start_date, end_date, data):
    """Update transactions table based on filters"""
    
    if not data or not data.get('processed_data'):
        return html.Div("No hay datos disponibles"), "₡0", "0", "₡0", "₡0"
    
    df = pd.DataFrame(data['processed_data'])
    
    # Apply filters
    if category and category != "all":
        df = df[df['Category'] == category]
    
    if responsible and responsible != "all":
        df = df[df['Responsible'] == responsible]
    
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
                    html.Th("Fecha", className="text-nowrap"),
                    html.Th("Descripción", className="text-nowrap"),
                    html.Th("Categoría", className="text-nowrap"),
                    html.Th("Responsable", className="text-nowrap"),
                    html.Th("Monto", className="text-end text-nowrap"),
                    html.Th("Tarjeta", className="text-nowrap")
                ])
            ]),
            html.Tbody(table_rows)
        ], striped=True, hover=True, responsive=True, className="table-sm")
    
    return table, total_formatted, count_formatted, avg_formatted, max_formatted