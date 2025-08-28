"""
Home Page - Dashboard Overview
Main dashboard with KPIs, charts and summary information
"""

import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Output, Input, State
import plotly.express as px
import pandas as pd
from datetime import datetime

from layout import layout


def create_layout(data: pd.DataFrame = None, kpis: dict = None):
    """Create home page layout with KPIs and charts"""
    
    # Default values if no data
    if kpis is None:
        kpis = {
            'total_amount': 0,
            'transaction_count': 0,
            'average_ticket': 0,
            'month_delta': 0,
            'top_merchants': [],
            'spending_by_responsible': {}
        }
    
    # Format currency
    def format_currency(amount):
        try:
            return f"₡{amount:,.0f}"
        except:
            return "₡0"
    
    # Page header
    page_header = html.Div([
        html.H2("📊 Resumen Financiero", className="mb-0"),
        html.P("Dashboard principal con indicadores clave", className="text-muted")
    ], className="mb-4")
    
    # KPI Cards Row
    kpi_cards = dbc.Row([
        dbc.Col([
            layout.create_kpi_card(
                title="Gasto Total (Mes Actual)",
                value=format_currency(kpis.get('total_amount', 0)),
                delta=kpis.get('month_delta', "0%"),
                icon="fas fa-wallet",
                color="primary"
            )
        ], width=12, lg=3, className="mb-3"),
        
        dbc.Col([
            layout.create_kpi_card(
                title="# Transacciones",
                value=str(int(kpis.get('transaction_count', 0))),
                icon="fas fa-receipt",
                color="info"
            )
        ], width=12, lg=3, className="mb-3"),
        
        dbc.Col([
            layout.create_kpi_card(
                title="Ticket Promedio",
                value=format_currency(kpis.get('average_ticket', 0)),
                icon="fas fa-chart-bar",
                color="success"
            )
        ], width=12, lg=3, className="mb-3"),
        
        dbc.Col([
            layout.create_kpi_card(
                title="Δ vs Mes Anterior",
                value=f"{kpis.get('month_delta', 0):+.1f}%",
                icon="fas fa-trending-up" if kpis.get('month_delta', 0) > 0 else "fas fa-trending-down",
                color="warning"
            )
        ], width=12, lg=3, className="mb-3"),
    ], className="mb-4")
    
    # Charts and data
    content_row = dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("📈 Datos del Mes Actual"),
                dbc.CardBody([
                    layout.create_loading_spinner("home-content")
                ])
            ])
        ], width=12)
    ])
    
    return html.Div([
        page_header,
        kpi_cards,
        content_row,
        
        # Hidden div to store data
        dcc.Store(id="home-data-store"),
    ])


@callback(
    Output("home-content", "children"),
    [Input("home-data-store", "data")]
)
def update_home_content(stored_data):
    """Update home page content"""
    
    if not stored_data or not stored_data.get('processed_data'):
        return layout.create_empty_state("No hay datos disponibles")
    
    try:
        # Convert stored data back to DataFrame
        df = pd.DataFrame(stored_data['processed_data'])
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Current month data
        now = datetime.now()
        current_month = df[
            (df['Date'].dt.month == now.month) & 
            (df['Date'].dt.year == now.year)
        ]
        
        if current_month.empty:
            return layout.create_empty_state("No hay datos para el mes actual")
        
        # Create summary table
        summary_table = dbc.Table.from_dataframe(
            current_month[['Date', 'Description', 'Amount', 'Responsible']].head(10),
            striped=True,
            bordered=True,
            hover=True,
            responsive=True,
            className="mb-0"
        )
        
        return html.Div([
            html.H5(f"Transacciones Recientes ({len(current_month)} total)"),
            summary_table
        ])
        
    except Exception as e:
        return layout.create_empty_state(f"Error al cargar datos: {str(e)}")
