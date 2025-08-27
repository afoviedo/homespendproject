"""
Data Page - Raw data preview and management
"""

import dash_bootstrap_components as dbc
from dash import html, dcc

from layout import layout


def create_layout(raw_data = None, processed_data = None):
    """Create data page layout"""
    
    # Page header
    page_header = html.Div([
        html.H2("🗄️ Gestión de Datos", className="mb-0"),
        html.P("Vista y administración de datos en bruto y procesados", className="text-muted")
    ], className="mb-4")
    
    # Data info
    info_card = dbc.Card([
        dbc.CardHeader("📊 Información de Datos"),
        dbc.CardBody([
            dbc.Alert([
                html.I(className="fas fa-cloud me-2"),
                html.Strong("Fuente de datos: "),
                "HomeSpend.xlsx en OneDrive"
            ], color="info")
        ])
    ])
    
    return html.Div([
        page_header,
        info_card,
        
        # Hidden stores
        dcc.Store(id="data-page-store"),
    ])
