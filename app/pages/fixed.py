"""
Fixed Expenses Page - Manage fixed monthly expenses
"""

import dash_bootstrap_components as dbc
from dash import html, dcc

from layout import layout


def create_layout(fixed_expenses_data = None):
    """Create fixed expenses page layout"""
    
    # Page header
    page_header = html.Div([
        html.H2("📅 Gastos Fijos", className="mb-0"),
        html.P("Gestión de gastos fijos mensuales automáticos", className="text-muted")
    ], className="mb-4")
    
    # Fixed expenses info
    config_card = dbc.Card([
        dbc.CardHeader("⚙️ Configuración de Gastos Fijos"),
        dbc.CardBody([
            html.P("Los siguientes gastos fijos se inyectan automáticamente el día 1 de cada mes:", className="text-muted mb-3"),
            
            dbc.ListGroup([
                dbc.ListGroupItem([
                    html.H6("🏠 Vivienda", className="mb-1"),
                    html.P("₡430,000", className="mb-0 fw-bold text-primary"),
                ]),
                dbc.ListGroupItem([
                    html.H6("🚗 Vehículo", className="mb-1"),
                    html.P("₡230,000", className="mb-0 fw-bold text-info"),
                ]),
                dbc.ListGroupItem([
                    html.H6("💝 Donaciones", className="mb-1"),
                    html.P("₡240,000", className="mb-0 fw-bold text-success"),
                ]),
            ], flush=True)
        ])
    ])
    
    return html.Div([
        page_header,
        config_card,
        
        # Hidden stores
        dcc.Store(id="fixed-data-store"),
    ])
