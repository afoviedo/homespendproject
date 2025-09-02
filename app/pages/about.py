"""
About Page - Project Information and Developer Details
"""

import dash_bootstrap_components as dbc
from dash import html, dcc
from datetime import datetime


def create_layout():
    """Create the About page layout"""
    
    current_year = datetime.now().year
    
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1("Acerca de HomeSpend", className="text-center mb-4"),
                html.Hr(),
            ], width=12)
        ]),
        
        # Project Description
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H3("🏠 HomeSpend - Dashboard Financiero Personal", className="card-title mb-3"),
                        html.P([
                            "HomeSpend es una aplicación web moderna diseñada para el control y análisis de gastos personales y familiares. ",
                            "Desarrollada con tecnologías de vanguardia, ofrece una interfaz intuitiva y funcionalidades avanzadas ",
                            "para el seguimiento financiero."
                        ], className="card-text"),
                        html.Hr(),
                        html.H5("🚀 Características Principales:", className="mt-3"),
                        html.Ul([
                            html.Li("Dashboard interactivo con KPIs en tiempo real"),
                            html.Li("Integración con Microsoft OneDrive para sincronización automática"),
                            html.Li("Filtros avanzados por categoría, responsable y fechas"),
                            html.Li("Gráficos y visualizaciones dinámicas"),
                            html.Li("Autenticación segura con Microsoft OAuth2"),
                            html.Li("Interfaz responsive y temas claro/oscuro"),
                            html.Li("Análisis de tendencias y comparativas mensuales")
                        ])
                    ])
                ], className="shadow mb-4")
            ], width=12)
        ]),
        
        # Technology Stack
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H3("🛠️ Stack Tecnológico", className="card-title mb-3"),
                        html.Div([
                            dbc.Row([
                                dbc.Col([
                                    html.H5("Frontend:", className="text-primary"),
                                    html.Ul([
                                        html.Li("Dash (Framework web reactivo)"),
                                        html.Li("Plotly (Gráficos interactivos)"),
                                        html.Li("Dash Bootstrap Components (UI)"),
                                        html.Li("Font Awesome (Iconos)")
                                    ])
                                ], width=6),
                                dbc.Col([
                                    html.H5("Backend:", className="text-success"),
                                    html.Ul([
                                        html.Li("Python 3.11+"),
                                        html.Li("Flask (Servidor web)"),
                                        html.Li("Pandas (Procesamiento de datos)"),
                                        html.Li("Microsoft Graph API (OneDrive)")
                                    ])
                                ], width=6)
                            ])
                        ])
                    ])
                ], className="shadow mb-4")
            ], width=12)
        ]),
        
        # Developer Information
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H3("👨‍💻 Desarrollador", className="card-title mb-3"),
                        html.Div([
                            html.H4("Ingeniero Fernando Oviedo Matamoros", className="text-primary mb-2"),
                            html.P("Costa Rica", className="text-muted mb-3"),
                            html.Hr(),
                            html.H5("🎯 Especialidades:", className="mt-3"),
                            html.Ul([
                                html.Li("Desarrollo de aplicaciones web empresariales"),
                                html.Li("Análisis y procesamiento de datos"),
                                html.Li("Integración de APIs y servicios en la nube"),
                                html.Li("Arquitectura de software escalable"),
                                html.Li("Automatización de procesos de negocio")
                            ]),
                            html.Hr(),
                            html.H5("📧 Contacto:", className="mt-3"),
                            html.P([
                                "Para consultas técnicas, sugerencias o colaboraciones, ",
                                "puedes contactarme a través de los canales profesionales."
                            ], className="text-muted")
                        ])
                    ])
                ], className="shadow mb-4")
            ], width=12)
        ]),
        
        # Project Details
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H3("📋 Detalles del Proyecto", className="card-title mb-3"),
                        html.Div([
                            dbc.Row([
                                dbc.Col([
                                    html.H5("📊 Funcionalidades:", className="text-info"),
                                    html.Ul([
                                        html.Li("Gestión de transacciones financieras"),
                                        html.Li("Categorización automática de gastos"),
                                        html.Li("Análisis de patrones de consumo"),
                                        html.Li("Reportes personalizables"),
                                        html.Li("Sincronización en tiempo real")
                                    ])
                                ], width=6),
                                dbc.Col([
                                    html.H5("🔒 Seguridad:", className="text-warning"),
                                    html.Ul([
                                        html.Li("Autenticación OAuth2 con Microsoft"),
                                        html.Li("Encriptación de datos sensibles"),
                                        html.Li("Sesiones seguras"),
                                        html.Li("Acceso controlado por usuario")
                                    ])
                                ], width=6)
                            ])
                        ])
                    ])
                ], className="shadow mb-4")
            ], width=12)
        ]),
        
        # Copyright and Legal
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H3("⚖️ Información Legal", className="card-title mb-3"),
                        html.Div([
                            html.P([
                                f"© {current_year} HomeSpend. Todos los derechos reservados."
                            ], className="text-center fw-bold mb-3"),
                            html.Hr(),
                            html.H5("📜 Licencia:", className="mt-3"),
                            html.P([
                                "Este software es propiedad intelectual del desarrollador. ",
                                "Su uso está sujeto a los términos y condiciones establecidos."
                            ], className="text-muted mb-3"),
                            html.H5("🛡️ Privacidad:", className="mt-3"),
                            html.P([
                                "HomeSpend respeta la privacidad de los usuarios. ",
                                "Los datos financieros se procesan localmente y solo se sincronizan ",
                                "con OneDrive bajo el control del usuario."
                            ], className="text-muted")
                        ])
                    ])
                ], className="shadow mb-4")
            ], width=12)
        ]),
        
        # Footer
        dbc.Row([
            dbc.Col([
                html.Div([
                    html.Hr(),
                    html.P([
                        "Desarrollado con ❤️ en Costa Rica",
                        html.Br(),
                        f"© {current_year} Fernando Oviedo Matamoros. Todos los derechos reservados."
                    ], className="text-center text-muted mt-4")
                ])
            ], width=12)
        ])
        
    ], fluid=True, className="py-4")


if __name__ == "__main__":
    # For testing
    print("About page module loaded successfully")
