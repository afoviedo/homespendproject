"""
ETL Module - Data processing with business rules
Handles data cleaning, responsible assignment, and fixed expenses injection
"""

import pandas as pd
import numpy as np
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple
import pytz


class HomeSpendETL:
    """ETL processor for HomeSpend financial data"""
    
    def __init__(self, timezone: str = 'America/Costa_Rica'):
        self.timezone = pytz.timezone(timezone)
        
        # Business rules for responsible assignment
        self.responsible_rules = {
            '9366': 'FIORELLA INFANTE AMORE',
            '2081': 'LUIS ESTEBAN OVIEDO MATAMOROS', 
            '4136': 'LUIS ESTEBAN OVIEDO MATAMOROS',
            'default': 'ALVARO FERNANDO OVIEDO MATAMOROS'
        }
        
        # Fixed expenses configuration
        self.fixed_expenses = [
            {
                'Description': 'Vivienda',
                'Amount': 430000,
                'Responsible': 'Gastos Fijos',
                'Date': None,  # Will be set to first day of month
                'Card': 'FIXED'
            },
            {
                'Description': 'Vehículo', 
                'Amount': 230000,
                'Responsible': 'Gastos Fijos',
                'Date': None,
                'Card': 'FIXED'
            },
            {
                'Description': 'Donaciones',
                'Amount': 240000,
                'Responsible': 'Gastos Fijos', 
                'Date': None,
                'Card': 'FIXED'
            }
        ]
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize the raw data"""
        if df is None or df.empty:
            return pd.DataFrame()
        
        # Make a copy to avoid modifying original
        cleaned_df = df.copy()
        
        # Standardize column names
        column_mapping = {
            'Fecha': 'Date',
            'Descripción': 'Description', 
            'Descripcion': 'Description',
            'Business': 'Description',  # English version
            'Monto': 'Amount',
            'Responsable': 'Responsible',
            'Tarjeta': 'Card'
        }
        
        # Rename columns if they exist
        for old_name, new_name in column_mapping.items():
            if old_name in cleaned_df.columns:
                cleaned_df = cleaned_df.rename(columns={old_name: new_name})
        
        # Ensure required columns exist
        required_columns = ['Date', 'Description', 'Amount', 'Responsible', 'Card']
        for col in required_columns:
            if col not in cleaned_df.columns:
                cleaned_df[col] = np.nan
        
        # Clean Date column
        cleaned_df['Date'] = self._clean_dates(cleaned_df['Date'])
        
        # Clean Amount column
        cleaned_df['Amount'] = self._clean_amounts(cleaned_df['Amount'])
        
        # Clean text columns
        text_columns = ['Description', 'Responsible', 'Card']
        for col in text_columns:
            cleaned_df[col] = self._clean_text(cleaned_df[col])
        
        # Remove rows with invalid data
        cleaned_df = cleaned_df.dropna(subset=['Date', 'Amount'])
        cleaned_df = cleaned_df[cleaned_df['Amount'] != 0]
        
        return cleaned_df
    
    def _clean_dates(self, date_series: pd.Series) -> pd.Series:
        """Clean and parse date column"""
        def parse_date(date_val):
            if pd.isna(date_val):
                return None
                
            if isinstance(date_val, (datetime, date)):
                return date_val
            
            if isinstance(date_val, str):
                # Try different date formats
                formats = ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y']
                for fmt in formats:
                    try:
                        return pd.Timestamp(datetime.strptime(date_val, fmt))
                    except ValueError:
                        continue
            
            # Try pandas to_datetime as fallback
            try:
                return pd.to_datetime(date_val)
            except:
                return None
        
        return date_series.apply(parse_date)
    
    def _clean_amounts(self, amount_series: pd.Series) -> pd.Series:
        """Clean and parse amount column"""
        def parse_amount(amount_val):
            if pd.isna(amount_val):
                return 0.0
            
            if isinstance(amount_val, (int, float)):
                return float(amount_val)
            
            if isinstance(amount_val, str):
                # Remove currency symbols and spaces
                cleaned = amount_val.replace('₡', '').replace(',', '').replace(' ', '')
                try:
                    return float(cleaned)
                except ValueError:
                    return 0.0
            
            return 0.0
        
        return amount_series.apply(parse_amount)
    
    def _clean_text(self, text_series: pd.Series) -> pd.Series:
        """Clean text columns"""
        def clean_text_value(text_val):
            if pd.isna(text_val):
                return ''
            return str(text_val).strip()
        
        return text_series.apply(clean_text_value)
    
    def apply_responsible_rules(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply business rules for responsible assignment"""
        if df.empty:
            return df
        
        processed_df = df.copy()
        
        def assign_responsible(row):
            # Only assign if responsible is empty or NaN
            if pd.isna(row['Responsible']) or row['Responsible'] == '':
                card_str = str(row['Card']).strip()
                
                # Check each rule
                for card_number, responsible in self.responsible_rules.items():
                    if card_number != 'default' and card_number in card_str:
                        return responsible
                
                # Default case
                return self.responsible_rules['default']
            
            # Keep existing responsible
            return row['Responsible']
        
        processed_df['Responsible'] = processed_df.apply(assign_responsible, axis=1)
        
        return processed_df
    
    def inject_fixed_expenses(self, df: pd.DataFrame, target_month: int = None, target_year: int = None) -> pd.DataFrame:
        """Inject fixed expenses for the target month (defaults to current month)"""
        if target_month is None or target_year is None:
            now = datetime.now(self.timezone)
            target_month = target_month or now.month
            target_year = target_year or now.year
        
        # Create first day of target month
        first_day = date(target_year, target_month, 1)
        
        # Check if fixed expenses already exist for this month
        if not df.empty:
            df_month_data = df[
                (pd.to_datetime(df['Date']).dt.month == target_month) & 
                (pd.to_datetime(df['Date']).dt.year == target_year) &
                (df['Responsible'] == 'Gastos Fijos')
            ]
            
            # If fixed expenses already exist, don't inject again
            if not df_month_data.empty:
                return df
        
        # Create fixed expenses rows
        fixed_rows = []
        for expense in self.fixed_expenses:
            fixed_row = expense.copy()
            fixed_row['Date'] = pd.Timestamp(first_day)  # Convert to Timestamp for consistency
            fixed_rows.append(fixed_row)
        
        # Convert to DataFrame and combine
        fixed_df = pd.DataFrame(fixed_rows)
        
        if df.empty:
            return fixed_df
        else:
            combined_df = pd.concat([df, fixed_df], ignore_index=True)
            # Sort by date
            combined_df = combined_df.sort_values('Date').reset_index(drop=True)
            return combined_df
    
    def process_data(self, raw_df: pd.DataFrame, inject_fixed: bool = True) -> pd.DataFrame:
        """Complete ETL pipeline"""
        # Step 1: Clean data
        cleaned_df = self.clean_data(raw_df)
        
        # Step 2: Apply responsible rules
        processed_df = self.apply_responsible_rules(cleaned_df)
        
        # Step 3: Inject fixed expenses if requested
        if inject_fixed:
            processed_df = self.inject_fixed_expenses(processed_df)
        
        return processed_df
    
    def calculate_kpis(self, df: pd.DataFrame) -> Dict:
        """Calculate KPIs from processed data"""
        if df.empty:
            return {
                'total_amount': 0,
                'transaction_count': 0,
                'average_ticket': 0,
                'month_delta': 0,
                'top_merchants': [],
                'spending_by_responsible': {}
            }
        
        # Current month data
        now = datetime.now(self.timezone)
        current_month_data = df[
            (pd.to_datetime(df['Date']).dt.month == now.month) & 
            (pd.to_datetime(df['Date']).dt.year == now.year)
        ]
        
        # Previous month data for delta calculation
        prev_month = now.month - 1 if now.month > 1 else 12
        prev_year = now.year if now.month > 1 else now.year - 1
        prev_month_data = df[
            (pd.to_datetime(df['Date']).dt.month == prev_month) & 
            (pd.to_datetime(df['Date']).dt.year == prev_year)
        ]
        
        # Calculate KPIs
        current_total = current_month_data['Amount'].sum()
        prev_total = prev_month_data['Amount'].sum()
        
        month_delta = ((current_total - prev_total) / prev_total * 100) if prev_total > 0 else 0
        
        # Top merchants (descriptions)
        top_merchants = (
            current_month_data.groupby('Description')['Amount']
            .sum()
            .sort_values(ascending=False)
            .head(10)
            .to_dict()
        )
        
        # Spending by responsible
        spending_by_responsible = (
            current_month_data.groupby('Responsible')['Amount']
            .sum()
            .to_dict()
        )
        
        return {
            'total_amount': current_total,
            'transaction_count': len(current_month_data),
            'average_ticket': current_total / len(current_month_data) if len(current_month_data) > 0 else 0,
            'month_delta': month_delta,
            'top_merchants': list(top_merchants.items()),
            'spending_by_responsible': spending_by_responsible
        }
