#!/usr/bin/env python3
"""
Script de Validación de KPIs
Verifica que los cálculos de los cards sean 100% correctos
"""

import pandas as pd
from datetime import datetime
import sys
import os

# Add app directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from etl import HomeSpendETL


def validate_kpis_manually():
    """
    Script para validar manualmente los KPIs con datos de ejemplo
    """
    print("🔍 VALIDACIÓN MANUAL DE KPIs")
    print("=" * 50)
    
    # Create sample data for testing
    current_month = datetime.now().month
    current_year = datetime.now().year
    prev_month = current_month - 1 if current_month > 1 else 12
    prev_year = current_year if current_month > 1 else current_year - 1
    
    sample_data = [
        # Current month data
        {'Date': f'{current_year}-{current_month:02d}-01', 'Amount': 50000, 'Responsible': 'Juan', 'Description': 'Supermercado', 'Card': '1234'},
        {'Date': f'{current_year}-{current_month:02d}-05', 'Amount': 75000, 'Responsible': 'Maria', 'Description': 'Gasolina', 'Card': '5678'},
        {'Date': f'{current_year}-{current_month:02d}-10', 'Amount': 30000, 'Responsible': 'Juan', 'Description': 'Farmacia', 'Card': '1234'},
        
        # Previous month data
        {'Date': f'{prev_year}-{prev_month:02d}-01', 'Amount': 40000, 'Responsible': 'Juan', 'Description': 'Supermercado', 'Card': '1234'},
        {'Date': f'{prev_year}-{prev_month:02d}-15', 'Amount': 60000, 'Responsible': 'Maria', 'Description': 'Gasolina', 'Card': '5678'},
    ]
    
    df = pd.DataFrame(sample_data)
    
    print("📊 DATOS DE PRUEBA:")
    print(df.to_string(index=False))
    print()
    
    # Calculate KPIs
    etl = HomeSpendETL()
    kpis = etl.calculate_kpis(df)
    
    print("🧮 CÁLCULOS MANUALES VERIFICACIÓN:")
    print("-" * 40)
    
    # Manual calculations for current month
    current_data = df[pd.to_datetime(df['Date']).dt.month == current_month]
    prev_data = df[pd.to_datetime(df['Date']).dt.month == prev_month]
    
    current_total_manual = current_data['Amount'].sum()
    prev_total_manual = prev_data['Amount'].sum()
    current_count_manual = len(current_data)
    avg_ticket_manual = current_total_manual / current_count_manual if current_count_manual > 0 else 0
    delta_manual = ((current_total_manual - prev_total_manual) / prev_total_manual * 100) if prev_total_manual > 0 else 0
    
    print(f"✅ Total Mes Actual (Manual): ₡{current_total_manual:,.0f}")
    print(f"📋 KPI Sistema:              ₡{kpis['total_amount']:,.0f}")
    print(f"   ✓ {'CORRECTO' if current_total_manual == kpis['total_amount'] else 'ERROR'}")
    print()
    
    print(f"✅ # Transacciones (Manual): {current_count_manual}")
    print(f"📋 KPI Sistema:              {kpis['transaction_count']}")
    print(f"   ✓ {'CORRECTO' if current_count_manual == kpis['transaction_count'] else 'ERROR'}")
    print()
    
    print(f"✅ Ticket Promedio (Manual): ₡{avg_ticket_manual:,.0f}")
    print(f"📋 KPI Sistema:              ₡{kpis['average_ticket']:,.0f}")
    print(f"   ✓ {'CORRECTO' if abs(avg_ticket_manual - kpis['average_ticket']) < 1 else 'ERROR'}")
    print()
    
    print(f"✅ Delta % (Manual): {delta_manual:.1f}%")
    print(f"📋 KPI Sistema:      {kpis['month_delta']:.1f}%")
    print(f"   ✓ {'CORRECTO' if abs(delta_manual - kpis['month_delta']) < 0.1 else 'ERROR'}")
    print()
    
    print("🔍 VERIFICACIÓN ADICIONAL:")
    print(f"   Mes actual: {current_month}/{current_year}")
    print(f"   Mes anterior: {prev_month}/{prev_year}")
    print(f"   Total mes actual manual: {current_total_manual}")
    print(f"   Total mes anterior manual: {prev_total_manual}")
    print(f"   Diferencia: {current_total_manual - prev_total_manual}")
    print(f"   % Cambio: {delta_manual:.2f}%")


if __name__ == "__main__":
    validate_kpis_manually()

