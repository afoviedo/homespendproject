"""
Transactions Page - Detailed transaction listing and filtering
"""

import dash_bootstrap_components as dbc
from dash import html, dcc
import pandas as pd

from layout import layout


def create_layout(data: pd.DataFrame = None):
    """Create transactions page layout"""
    
    # Page header
    page_header = html.Div([
        html.H2("📋 Transacciones", className="mb-0"),
        html.P("Listado detallado de todas las transacciones", className="text-muted")
    ], className="mb-4")
    
    # Content
    content = dbc.Card([
        dbc.CardHeader("📊 Tabla de Transacciones"),
        dbc.CardBody([
            layout.create_loading_spinner("transactions-table", "Cargando transacciones...")
        ])
    ])
    
    return html.Div([
        page_header,
        content,
        
        # Hidden stores
        dcc.Store(id="transactions-data-store"),
    ])
