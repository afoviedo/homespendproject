"""
Transactions Page - Vista de todas las transacciones
"""

import pandas as pd
from dash import html, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc
from typing import Optional


def create_layout(df: Optional[pd.DataFrame] = None) -> html.Div:
    """Create transactions page layout"""
    
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
                    html.H4("En Desarrollo", className="alert-heading"),
                    html.P("Esta página estará disponible próximamente con funcionalidades avanzadas de filtrado y exportación.")
                ], color="info")
            ])
        ])
    ], fluid=True)