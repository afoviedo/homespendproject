# 💰 HomeSpend - Dashboard Financiero Premium

Dashboard financiero profesional construido con **Plotly Dash** y **Microsoft Graph**, diseñado para gestionar gastos familiares con autenticación OAuth2 y datos en OneDrive.

![Python](https://img.shields.io/badge/python-v3.11+-blue.svg)
![Dash](https://img.shields.io/badge/dash-v2.17+-green.svg)
![Docker](https://img.shields.io/badge/docker-ready-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🌟 Características

### 🎨 Interfaz Premium
- **Diseño moderno** con `dash-bootstrap-components` y tema LUX
- **Navbar responsive** con autenticación Microsoft
- **Sidebar colapsable** con filtros y navegación
- **Cards KPI** con indicadores visuales y deltas
- **Gráficos interactivos** con Plotly (líneas, barras, pie charts)
- **Tablas filtrables** con búsqueda y exportación CSV

### 🔐 Autenticación Segura
- **Microsoft OAuth2** con Authorization Code Flow
- **Refresh tokens** automático para sesiones persistentes
- **Scopes específicos**: `Files.Read`, `offline_access`, `User.Read`
- **Middleware de autenticación** transparente

### 📊 Funcionalidades de Dashboard
- **Resumen**: KPIs, tendencias mensuales, gasto por responsable, top comercios
- **Transacciones**: Tabla filtrable con búsqueda avanzada y exportación
- **Gastos Fijos**: Gestión automática con toggle de persistencia OneDrive
- **Datos**: Vista de datos crudos y procesados con diagnósticos

### 🤖 Reglas de Negocio Automatizadas
- **Asignación de responsables** por número de tarjeta:
  - Card 9366 → `FIORELLA INFANTE AMORE`
  - Card 2081/4136 → `LUIS ESTEBAN OVIEDO MATAMOROS`
  - Otros → `ALVARO FERNANDO OVIEDO MATAMOROS`
- **Gastos fijos mensuales** automáticos (día 1):
  - Vivienda: ₡430,000
  - Vehículo: ₡230,000
  - Donaciones: ₡240,000

### ☁️ Integración OneDrive
- **Lectura automática** de archivo `HomeSpend.xlsx`
- **Escritura opcional** de gastos fijos en hoja `FixedExpenses`
- **Detección de cambios** y refresh inteligente
- **Manejo de errores** robusto con fallbacks

## 🚀 Instalación y Despliegue

### Prerrequisitos
- Python 3.11+
- Docker y Docker Compose
- Cuenta Microsoft con acceso a OneDrive
- VPS con Nginx (opcional) o Traefik

### 1. Clonar y configurar

```bash
git clone https://github.com/afoviedo/homespendproject.git
cd homespendproject

# Copiar archivo de configuración
cp env.example .env

# Editar variables de entorno
nano .env
```

### 2. Configurar Microsoft App

1. Ve a [Azure Portal](https://portal.azure.com)
2. Registra una nueva aplicación en **Azure Active Directory**
3. Configura **Redirect URI**: `https://dashboard.srv867766.hstgr.cloud/auth/callback`
4. Genera **Client Secret**
5. Asigna permisos: `Files.Read`, `offline_access`, `User.Read`

### 3. Configurar variables de entorno

```env
APP_NAME=HomeSpend
ENV=production
TZ=America/Costa_Rica
FLASK_SECRET_KEY=your-super-secret-key-here

# Microsoft Identity
MS_TENANT_ID=common
MS_CLIENT_ID=your-client-id
MS_CLIENT_SECRET=your-client-secret
MS_REDIRECT_URI=https://dashboard.srv867766.hstgr.cloud/auth/callback
MS_SCOPES=offline_access Files.Read User.Read

# OneDrive file
ONEDRIVE_FILE_NAME=HomeSpend.xlsx
ONEDRIVE_FILE_PATH=/HomeSpend.xlsx

# App
APP_HOST=0.0.0.0
APP_PORT=8090
```

### 4. Desplegar con Docker

```bash
# Despliegue básico
docker compose up -d

# Ver logs
docker compose logs -f
```

## 🔧 Desarrollo

### Ejecutar en modo desarrollo

```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
export FLASK_SECRET_KEY="dev-secret"
export ENV="development"
# ... otras variables

# Ejecutar servidor
python app/server.py
```

## 🚨 Troubleshooting

### Problemas comunes:

**Error de autenticación:**
```bash
# Verificar configuración OAuth
docker logs homespend_app | grep "OAuth"
```

**Error de conexión OneDrive:**
```bash
# Verificar permisos de la app
# Verificar nombre y path del archivo Excel
```

## 📄 Licencia

Este proyecto está bajo la Licencia MIT.

---

**⭐ Si este proyecto te es útil, considera darle una estrella en GitHub!**
