"""
HomeSpend Server - Main Dash + Flask Application
Combines authentication, data processing and dashboard
"""

import os
import sys
from datetime import datetime
from flask import Flask, session, redirect, request
import dash
from dash import html, dcc, callback, Output, Input, State, clientside_callback, ClientsideFunction
import dash_bootstrap_components as dbc
from dotenv import load_dotenv
import pandas as pd
import pytz

# Load environment variables
load_dotenv()

# Import local modules
from auth import init_auth, require_auth
from graph import OneDriveManager
from etl import HomeSpendETL
from layout import layout

# Import pages
from pages import home, transactions, fixed, data


# Initialize Flask app
server = Flask(__name__)
server.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')

# Initialize Dash app
app = dash.Dash(
    __name__,
    server=server,
    external_stylesheets=[dbc.themes.LUX, dbc.icons.FONT_AWESOME],
    suppress_callback_exceptions=True,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"},
        {"name": "description", "content": "HomeSpend - Dashboard financiero personal"}
    ]
)

app.title = "HomeSpend - Dashboard Financiero"

# Initialize authentication
auth = init_auth(server)

# Initialize ETL processor
etl_processor = HomeSpendETL()

# Global data store
app_data = {
    'raw_data': None,
    'processed_data': None,
    'last_refresh': None,
    'onedrive_manager': None
}


def get_user_display_name():
    """Get user display name from session"""
    return session.get('user_name', 'Usuario')


def create_sample_data():
    """Create sample data for demonstration"""
    from datetime import datetime, timedelta
    import random
    
    # Sample data
    sample_records = []
    base_date = datetime.now() - timedelta(days=30)
    
    merchants = ["SUPERMERCADO LA COSECHA", "GASOLINERA DELTA", "RESTAURANTE MACHU PICCHU", 
                 "FARMACIA FISCHEL", "UBER TRIP", "WALMART", "AMAZON PRIME", "NETFLIX"]
    responsibles = ["ALVARO FERNANDO OVIEDO MATAMOROS", "FIORELLA INFANTE AMORE", "LUIS ESTEBAN OVIEDO MATAMOROS"]
    
    for i in range(50):
        date = base_date + timedelta(days=random.randint(0, 30))
        sample_records.append({
            'Date': date.strftime('%Y-%m-%d'),
            'Description': random.choice(merchants),
            'Amount': random.randint(5000, 150000),
            'Responsible': random.choice(responsibles),
            'Card': f"***{random.choice(['9366', '2081', '4136'])}",
            'Category': 'Gastos Generales'
        })
    
    # Fixed expenses are now managed directly in OneDrive Excel file
    # No need to add them to sample data
    
    return {
        'raw_data': sample_records,
        'processed_data': sample_records,
        'last_refresh': datetime.now().isoformat(),
        'demo_mode': True
    }


def refresh_data_from_onedrive():
    """Refresh data from OneDrive"""
    try:
        access_token = auth.get_access_token()
        if not access_token:
            return False, "No hay token de acceso válido"
        
        # Create OneDrive manager
        onedrive_manager = OneDriveManager(access_token)
        app_data['onedrive_manager'] = onedrive_manager
        
        # Check if file exists
        if not onedrive_manager.file_exists():
            return False, f"Archivo {onedrive_manager.file_name} no encontrado en OneDrive"
        
        # Download and process data
        raw_df = onedrive_manager.get_transactions_data()
        if raw_df is None:
            return False, "Error al leer datos del archivo Excel"
        
        # Process data with ETL
        processed_df = etl_processor.process_data(raw_df, inject_fixed=True)
        
        # Store data
        app_data['raw_data'] = raw_df
        app_data['processed_data'] = processed_df
        app_data['last_refresh'] = datetime.now(pytz.timezone(os.getenv('TZ', 'UTC')))
        
        return True, f"Datos actualizados exitosamente. {len(processed_df)} registros procesados."
        
    except Exception as e:
        return False, f"Error al refrescar datos: {str(e)}"


# App layout
app.layout = dbc.Container([
    dcc.Location(id="url", refresh=False),
    
    # Navbar
    html.Div(id="navbar-container"),
    
    # Sidebar
    html.Div(id="sidebar-container"),
    
    # Main content area
    dbc.Row([
        dbc.Col([
            # Sidebar toggle button
            html.Div(id="sidebar-toggle-container", className="mb-3"),
            
            # Page content
            html.Div(id="page-content")
        ], width=12)
    ]),
    
    # Global stores
    dcc.Store(id="global-data-store"),
    dcc.Store(id="user-store"),
    
    # Global loading
    dcc.Loading(
        id="global-loading",
        type="dot",
        children=html.Div(id="global-loading-output")
    ),
    
    # Global interval for data refresh
    dcc.Interval(
        id="global-refresh-interval",
        interval=300000,  # 5 minutes
        n_intervals=0,
        disabled=True
    ),
    
], fluid=True)


@callback(
    [Output("navbar-container", "children"),
     Output("sidebar-container", "children"),
     Output("sidebar-toggle-container", "children"),
     Output("user-store", "data")],
    [Input("url", "pathname")]
)
def update_layout_components(pathname):
    """Update layout components based on authentication"""
    
    if not auth.is_authenticated():
        return html.Div(), html.Div(), html.Div(), {}
    
    user_name = get_user_display_name()
    user_data = auth.get_user_info()
    
    # Create layout components
    navbar = layout.create_navbar(user_name)
    sidebar = layout.create_sidebar()
    sidebar_toggle = layout.create_sidebar_toggle()
    
    return navbar, sidebar, sidebar_toggle, user_data


@callback(
    Output("page-content", "children"),
    [Input("url", "pathname"),
     Input("global-data-store", "data")]
)
def display_page(pathname, global_data):
    """Display page content based on URL"""
    
    if not auth.is_authenticated():
        return dbc.Container([
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H3("🔐 Autenticación Requerida", className="text-center mb-4"),
                            html.P("Por favor inicia sesión con tu cuenta Microsoft para acceder a HomeSpend.", 
                                  className="text-center text-muted mb-4"),
                            dbc.Button(
                                [html.I(className="fab fa-microsoft me-2"), "Iniciar Sesión con Microsoft"],
                                href="/login",
                                color="primary",
                                size="lg",
                                className="w-100"
                            )
                        ])
                    ], className="shadow")
                ], width=12, lg=6, className="mx-auto")
            ], className="min-vh-100 d-flex align-items-center")
        ], fluid=True)
    
    # Default data structure
    processed_data = global_data.get('processed_data', []) if global_data else []
    raw_data = global_data.get('raw_data', []) if global_data else []
    
    # Calculate KPIs
    kpis = {
        'total_amount': 0,
        'total_transactions': 0,
        'avg_amount': 0,
        'vs_previous_month': 0
    }
    if processed_data:
        df = pd.DataFrame(processed_data)
        calculated_kpis = etl_processor.calculate_kpis(df)
        kpis = {
            'total_amount': calculated_kpis.get('total_amount', 0),
            'total_transactions': calculated_kpis.get('transaction_count', 0),
            'avg_amount': calculated_kpis.get('average_ticket', 0),
            'vs_previous_month': calculated_kpis.get('month_delta', 0)
        }
    
    # Route to appropriate page
    if pathname == "/" or pathname == "/home":
        return home.create_layout(pd.DataFrame(processed_data) if processed_data else None, kpis)
    elif pathname == "/transactions":
        return transactions.create_layout(pd.DataFrame(processed_data) if processed_data else None)
    elif pathname == "/fixed":
        return fixed.create_layout()
    elif pathname == "/data":
        return data.create_layout(
            pd.DataFrame(raw_data) if raw_data else None,
            pd.DataFrame(processed_data) if processed_data else None
        )
    else:
        return dbc.Container([
            dbc.Alert([
                html.H4("⚠️ Página no encontrada", className="alert-heading"),
                html.P(f"La página '{pathname}' no existe."),
                html.Hr(),
                dbc.Button("🏠 Ir al Inicio", href="/", color="primary")
            ], color="warning")
        ])


@callback(
    [Output("global-data-store", "data"),
     Output("global-loading-output", "children")],
    [Input("url", "pathname"),
     Input("global-refresh-interval", "n_intervals")],
    [State("global-data-store", "data")],
    prevent_initial_call=False
)
def refresh_global_data(pathname, interval_count, current_data):
    """Refresh global data from OneDrive"""
    
    if not auth.is_authenticated():
        print("User not authenticated, returning sample data")
        return create_sample_data(), html.Div()
    
    try:
        # Get access token from auth system
        access_token = auth.get_access_token()
        if not access_token:
            print("No access token available, returning sample data")
            return create_sample_data(), html.Div()
        
        print(f"User authenticated, attempting OneDrive connection...")
        
        # Initialize OneDrive manager and ETL with token
        onedrive = OneDriveManager(access_token)
        etl = HomeSpendETL()
        
        # Get file path for logging
        file_path = os.getenv('ONEDRIVE_FILE_PATH', '/Casa/HomeSpend.xlsx')
        
        print(f"Attempting to load OneDrive file: {file_path}")
        
        # Check if file exists
        if not onedrive.file_exists():
            print(f"File not found: {file_path}")
            return create_sample_data(), html.Div()
        
        # Get transactions data directly from OneDrive
        df = onedrive.get_transactions_data()
        if df is None or df.empty:
            print(f"Could not load data from {file_path}")
            return create_sample_data(), html.Div()
        
        print(f"Successfully loaded {len(df)} transactions from OneDrive")
        
        # Process data (fixed expenses are managed in OneDrive Excel file)
        processed_df = etl.process_data(df)
        
        # Calculate KPIs
        kpis = etl.calculate_kpis(processed_df)
        
        print(f"Data processed successfully - {len(processed_df)} transactions, Total: ₡{kpis.get('total_amount', 0):,.0f}")
        
        # Return processed data
        return {
            'raw_data': df.to_dict('records') if not df.empty else [],
            'processed_data': processed_df.to_dict('records') if not processed_df.empty else [],
            'kpis': kpis,
            'last_refresh': datetime.now().isoformat()
        }, html.Div()
        
    except Exception as e:
        print(f"Error loading data: {e}")
        return create_sample_data(), html.Div()


# Sidebar toggle callback - using clientside for better performance
clientside_callback(
    """
    function(n_clicks) {
        if (n_clicks > 0) {
            // Simple toggle based on click count
            return n_clicks % 2 === 1;
        }
        return false;
    }
    """,
    Output("sidebar", "is_open"),
    Input("sidebar-toggle", "n_clicks"),
    prevent_initial_call=True
)


# Note: Page routing is handled by the main display_page callback above (lines 211-271)
# This duplicate callback has been removed to avoid conflicts


# Sync data across all pages
@callback(
    [Output("home-data-store", "data"),
     Output("transactions-data-store", "data"),
     Output("fixed-data-store", "data"),
     Output("data-page-store", "data")],
    [Input("global-data-store", "data")]
)
def sync_page_data(global_data):
    """Sync data to all page stores"""
    if not global_data:
        return {}, {}, {}, {}
    
    # Add fixed expenses status to fixed page data
    fixed_data = global_data.copy()
    if global_data.get('processed_data'):
        df = pd.DataFrame(global_data['processed_data'])
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        # Check if fixed expenses exist for current month
        fixed_current = df[
            (pd.to_datetime(df['Date']).dt.month == current_month) & 
            (pd.to_datetime(df['Date']).dt.year == current_year) &
            (df['Responsible'] == 'Gastos Fijos')
        ]
        
        fixed_data['has_fixed_current_month'] = not fixed_current.empty
        fixed_data['total_fixed_amount'] = fixed_current['Amount'].sum() if not fixed_current.empty else 0
    
    return global_data, global_data, fixed_data, global_data


# Error handling
@server.errorhandler(404)
def not_found(error):
    return redirect('/')


@server.errorhandler(500)
def internal_error(error):
    return redirect('/')


if __name__ == '__main__':
    # Configuration
    host = os.getenv('APP_HOST', '0.0.0.0')
    port = int(os.getenv('APP_PORT', 8090))
    debug = os.getenv('ENV', 'production') != 'production'
    
    print(f"🚀 Starting HomeSpend on {host}:{port}")
    print(f"📊 Environment: {os.getenv('ENV', 'production')}")
    print(f"🔗 Auth redirect: {os.getenv('MS_REDIRECT_URI')}")
    
    # Run server
    app.run_server(
        host=host,
        port=port,
        debug=debug,
        dev_tools_ui=debug,
        dev_tools_props_check=debug
    )
