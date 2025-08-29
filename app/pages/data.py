"""
Data Page - Gestión y visualización de datos
"""

import pandas as pd
from dash import html, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc
from typing import Optional


def create_layout(raw_df: Optional[pd.DataFrame] = None, processed_df: Optional[pd.DataFrame] = None) -> html.Div:
    """Create data management page layout"""
    
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2([
                    html.I(className="fas fa-database me-3"),
                    "DATOS"
                ], className="mb-0"),
                html.P("Gestión y visualización de datos de OneDrive", className="text-muted")
            ])
        ], className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                dbc.Alert([
                    html.H4("En Desarrollo", className="alert-heading"),
                    html.P("Esta página estará disponible próximamente para gestionar la sincronización con OneDrive.")
                ], color="info")
            ])
        ])
    ], fluid=True)