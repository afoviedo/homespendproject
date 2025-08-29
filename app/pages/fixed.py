"""
Fixed Expenses Page - Gestión de gastos fijos
"""

import pandas as pd
from dash import html, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc
from typing import Optional


def create_layout(df: Optional[pd.DataFrame] = None) -> html.Div:
    """Create fixed expenses page layout"""
    
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2([
                    html.I(className="fas fa-calendar-alt me-3"),
                    "📅 GASTOS FIJOS"
                ], className="mb-0"),
                html.P("Gestión y seguimiento de gastos fijos mensuales", className="text-muted")
            ])
        ], className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                dbc.Alert([
                    html.H4("🚧 En Desarrollo", className="alert-heading"),
                    html.P("Esta página estará disponible próximamente para gestionar gastos fijos recurrentes.")
                ], color="info")
            ])
        ])
    ], fluid=True)