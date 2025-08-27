"""
Premium Layout Components
Creates professional UI with navbar, sidebar and styled components
"""

import dash_bootstrap_components as dbc
from dash import html, dcc
import plotly.graph_objects as go
from typing import Dict, List, Any


class PremiumLayout:
    """Premium layout components for HomeSpend dashboard"""
    
    def __init__(self, theme=dbc.themes.LUX):
        self.theme = theme
        self.primary_color = "#007bff"
        self.success_color = "#28a745"
        self.danger_color = "#dc3545"
        self.warning_color = "#ffc107"
        self.info_color = "#17a2b8"
        
    def create_navbar(self, user_name: str = "Usuario") -> dbc.NavbarSimple:
        """Create premium navbar with logo and logout"""
        return dbc.NavbarSimple(
            children=[
                dbc.DropdownMenu(
                    children=[
                        dbc.DropdownMenuItem("Perfil", header=True),
                        dbc.DropdownMenuItem(f"👤 {user_name}", disabled=True),
                        dbc.DropdownMenuItem(divider=True),
                        dbc.DropdownMenuItem("🚪 Cerrar Sesión", href="/logout", external_link=True),
                    ],
                    nav=True,
                    in_navbar=True,
                    label="👤 Usuario",
                    align_end=True,
                ),
            ],
            brand="💰 HomeSpend",
            brand_href="/",
            color="primary",
            dark=True,
            className="mb-4",
            brand_style={"fontSize": "1.5rem", "fontWeight": "bold"}
        )
    
    def create_sidebar(self) -> dbc.Offcanvas:
        """Create collapsible sidebar for navigation and filters"""
        sidebar_content = [
            html.Hr(),
            html.P("📊 Navegación", className="text-muted mb-3"),
            
            dbc.Nav(
                [
                    dbc.NavLink(
                        [html.I(className="fas fa-home me-2"), "Resumen"],
                        href="/",
                        active="exact",
                        className="mb-2"
                    ),
                    dbc.NavLink(
                        [html.I(className="fas fa-list me-2"), "Transacciones"],
                        href="/transactions",
                        active="exact",
                        className="mb-2"
                    ),
                    dbc.NavLink(
                        [html.I(className="fas fa-calendar-alt me-2"), "Gastos Fijos"],
                        href="/fixed",
                        active="exact",
                        className="mb-2"
                    ),
                    dbc.NavLink(
                        [html.I(className="fas fa-database me-2"), "Datos"],
                        href="/data",
                        active="exact",
                        className="mb-2"
                    ),
                ],
                vertical=True,
                pills=True,
            ),
            
            html.Hr(),
            html.P("🔧 Filtros", className="text-muted mb-3"),
            
            # Refresh button
            dbc.Button(
                [html.I(className="fas fa-sync-alt me-2"), "Refrescar Datos"],
                id="refresh-data-btn",
                color="outline-primary",
                className="w-100 mb-3"
            ),
        ]
        
        return dbc.Offcanvas(
            sidebar_content,
            id="sidebar",
            title="🎛️ Controles",
            is_open=False,
            placement="start",
            style={"width": "350px"}
        )
    
    def create_sidebar_toggle(self) -> dbc.Button:
        """Create button to toggle sidebar"""
        return dbc.Button(
            html.I(className="fas fa-bars"),
            id="sidebar-toggle",
            color="outline-secondary",
            className="me-3",
            size="sm"
        )
    
    def create_kpi_card(self, title: str, value: str, delta: float = None, 
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
            card_body.append(
                html.Hr(className="my-2")
            )
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
    
    def create_loading_spinner(self, component_id: str, text: str = "Cargando...") -> dcc.Loading:
        """Create loading spinner component"""
        return dcc.Loading(
            id=f"loading-{component_id}",
            type="graph",
            children=html.Div(id=component_id),
        )
    
    def create_empty_state(self, message: str = "No hay datos disponibles", 
                          icon: str = "fas fa-inbox") -> html.Div:
        """Create empty state component"""
        return html.Div([
            html.Div([
                html.I(className=f"{icon} fa-4x text-muted mb-3"),
                html.H4(message, className="text-muted"),
                html.P("Intenta refrescar los datos o verificar tu conexión.", 
                      className="text-muted")
            ], className="text-center py-5")
        ], className="w-100")


# Global layout instance
layout = PremiumLayout()
