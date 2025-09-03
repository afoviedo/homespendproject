"""
Transactions Page - Vista de todas las transacciones con filtros avanzados
Replicando la estructura robusta de Home para garantizar funcionamiento
"""

import pandas as pd
from datetime import datetime, timedelta
from dash import html, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc
from typing import Optional


def create_layout(df: Optional[pd.DataFrame] = None) -> html.Div:
    """Create transactions page layout with filters and data table - replicating Home structure"""
    
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
    
    # Get unique responsibles for filter (same logic as Home)
    responsibles = sorted(df['Responsible'].unique().tolist())
    
    # Get unique categories for filter (same logic as Home)
    if 'Category' in df.columns and not df['Category'].isna().all():
        category_column = 'Category'
        print(f"Using Category column for transactions layout")
    elif 'Description' in df.columns:
        category_column = 'Description'
        print(f"Using Description column as fallback for transactions layout")
    else:
        category_column = None
        print(f"No category column available for transactions layout")
    
    if category_column:
        categories = sorted(df[category_column].unique().tolist())
        # Filter out empty/null values
        categories = [cat for cat in categories if cat and str(cat).strip()]
        print(f"Found {len(categories)} categories for transactions layout: {categories[:5]}...")
    else:
        categories = []
        print("No categories available for transactions layout")
    
    # Calculate date range with extended limits (same logic as Home)
    min_date = pd.to_datetime(df['Date']).min().date()
    max_date = pd.to_datetime(df['Date']).max().date()
    
    # Extend the range to allow more navigation
    extended_min_date = min_date - timedelta(days=365)  # 1 year before
    extended_max_date = max_date + timedelta(days=365)  # 1 year after
    
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
        
        # Filters Row (exact same structure as Home)
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5([
                            html.I(className="fas fa-filter me-2"),
                            "Filtros"
                        ], className="mb-0")
                    ]),
                    dbc.CardBody([
                        # First Row - Responsible and Category Filters
                        dbc.Row([
                            # Responsible Filter (Multi-select)
                            dbc.Col([
                                html.Label("Responsables:", className="fw-bold mb-2"),
                                dcc.Dropdown(
                                    id="transactions-responsible-filter",
                                    options=[{"label": r, "value": r} for r in responsibles],
                                    value=[],  # Empty list for multi-select
                                    multi=True,
                                    placeholder="Selecciona responsables (vacío = todos)"
                                )
                            ], width=12, lg=6),
                            
                            # Category Filter (Multi-select)
                            dbc.Col([
                                html.Label("Categorías:", className="fw-bold mb-2"),
                                dcc.Dropdown(
                                    id="transactions-category-filter",
                                    options=[{"label": cat, "value": cat} for cat in categories],
                                    value=[],  # Empty list for multi-select
                                    multi=True,
                                    placeholder="Selecciona categorías (vacío = todas)"
                                )
                            ], width=12, lg=6),
                        ], className="mb-3"),
                        
                        # Second Row - Date Range
                        dbc.Row([
                            # Date Range Filter
                            dbc.Col([
                                html.Label("Rango de Fechas:", className="fw-bold mb-2"),
                                dbc.Row([
                                    dbc.Col([
                                        html.Label("Desde:", className="small text-muted"),
                                        dcc.Input(
                                            id="transactions-start-date",
                                            type="date",
                                            value=min_date.strftime('%Y-%m-%d'),
                                            min=extended_min_date.strftime('%Y-%m-%d'),
                                            max=extended_max_date.strftime('%Y-%m-%d'),
                                            className="form-control",
                                            style={'width': '100%'}
                                        )
                                    ], width=6),
                                    dbc.Col([
                                        html.Label("Hasta:", className="small text-muted"),
                                        dcc.Input(
                                            id="transactions-end-date",
                                            type="date",
                                            value=max_date.strftime('%Y-%m-%d'),
                                            min=extended_min_date.strftime('%Y-%m-%d'),
                                            max=extended_max_date.strftime('%Y-%m-%d'),
                                            className="form-control",
                                            style={'width': '100%'}
                                        )
                                    ], width=6)
                                ])
                            ], width=12, lg=12),
                        ])
                    ])
                ])
            ])
        ], className="mb-4"),
        
        # Summary Stats Row (same structure as Home KPIs)
        dbc.Row(id="transactions-summary-row", className="mb-4"),
        
        # Data Table Row (main content)
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.H5([
                            html.I(className="fas fa-table me-2"),
                            "Tabla de Transacciones"
                        ], className="mb-0")
                    ]),
                    dbc.CardBody([
                        dcc.Loading(
                            html.Div(id="transactions-table-container"),
                            type="default"
                        )
                    ])
                ])
            ])
        ])
        
    ], fluid=True)


# Callbacks replicating Home structure but for transactions table
@callback(
    Output("transactions-summary-row", "children"),
    [Input("transactions-responsible-filter", "value"),
     Input("transactions-category-filter", "value"),
     Input("transactions-start-date", "value"),
     Input("transactions-end-date", "value")],
    [State("transactions-data-store", "data")],
    prevent_initial_call=False
)
def update_transactions_summary(responsibles, categories, start_date, end_date, data):
    """Update summary statistics based on filters - same logic as Home KPIs"""
    
    if not data or not data.get('processed_data'):
        return html.Div("No hay datos disponibles")
    
    df = pd.DataFrame(data['processed_data'])
    
    # Apply filters (same logic as Home)
    if responsibles and len(responsibles) > 0:
        df = df[df['Responsible'].isin(responsibles)]
    
    if categories and len(categories) > 0:
        df = df[df['Category'].isin(categories)]
    
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
    
    # Return summary cards (same structure as Home KPIs)
    return dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Total Filtrado", className="card-title text-muted"),
                    html.H4(total_formatted, className="text-primary mb-0")
                ])
            ], className="text-center shadow-sm")
        ], width=12, lg=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Transacciones", className="card-title text-muted"),
                    html.H4(count_formatted, className="text-success mb-0")
                ])
            ], className="text-center shadow-sm")
        ], width=12, lg=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Promedio", className="card-title text-muted"),
                    html.H4(avg_formatted, className="text-info mb-0")
                ])
            ], className="text-center shadow-sm")
        ], width=12, lg=3),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6("Máximo", className="card-title text-muted"),
                    html.H4(max_formatted, className="text-warning mb-0")
                ])
            ], className="text-center shadow-sm")
        ], width=12, lg=3)
    ])


@callback(
    Output("transactions-table-container", "children"),
    [Input("transactions-responsible-filter", "value"),
     Input("transactions-category-filter", "value"),
     Input("transactions-start-date", "value"),
     Input("transactions-end-date", "value")],
    [State("transactions-data-store", "data")],
    prevent_initial_call=False
)
def update_transactions_table(responsibles, categories, start_date, end_date, data):
    """Update transactions table based on filters - same logic as Home charts"""
    
    if not data or not data.get('processed_data'):
        return html.Div("No hay datos disponibles")
    
    df = pd.DataFrame(data['processed_data'])
    
    # Apply filters (same logic as Home)
    if responsibles and len(responsibles) > 0:
        df = df[df['Responsible'].isin(responsibles)]
    
    if categories and len(categories) > 0:
        df = df[df['Category'].isin(categories)]
    
    if start_date and end_date:
        df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
    
    # Create table
    if df.empty:
        return html.Div([
            dbc.Alert([
                html.H6("No hay transacciones que coincidan con los filtros seleccionados", className="alert-heading"),
                html.P("Intenta ajustar los criterios de búsqueda.")
            ], color="info")
        ])
    
    # Sort by date (most recent first)
    df_sorted = df.sort_values('Date', ascending=False)
    
    # Create table rows (limit to 100 for performance)
    table_rows = []
    for _, row in df_sorted.head(100).iterrows():
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
    
    # Create table (same structure as Home tables)
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
    
    return table


