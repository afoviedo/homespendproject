"""
Microsoft Graph API Client
Handles OneDrive file operations and Excel data management
"""

import os
import io
import json
from typing import Optional, Dict, Any, List
from datetime import datetime

import requests
import pandas as pd
from openpyxl import Workbook, load_workbook


class GraphClient:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://graph.microsoft.com/v1.0"
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
    
    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get OneDrive file information"""
        try:
            # Encode file path for URL
            encoded_path = requests.utils.quote(file_path, safe='')
            url = f"{self.base_url}/me/drive/root:/{encoded_path}"
            
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            else:
                raise Exception(f"Failed to get file info: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"Error getting file info: {str(e)}")
            return None
    
    def download_file(self, file_path: str) -> Optional[bytes]:
        """Download file content from OneDrive"""
        try:
            # Get file info first
            file_info = self.get_file_info(file_path)
            if not file_info:
                print(f"File not found: {file_path}")
                return None
            
            # Get download URL
            download_url = file_info.get('@microsoft.graph.downloadUrl')
            if not download_url:
                raise Exception("No download URL available")
            
            # Download file content
            response = requests.get(download_url)
            
            if response.status_code == 200:
                return response.content
            else:
                raise Exception(f"Failed to download file: {response.status_code}")
                
        except Exception as e:
            print(f"Error downloading file: {str(e)}")
            return None
    
    def read_excel_file(self, file_path: str, sheet_name: str = None) -> Optional[pd.DataFrame]:
        """Read Excel file from OneDrive and return as DataFrame"""
        try:
            # Download file content
            file_content = self.download_file(file_path)
            if not file_content:
                return None
            
            # Read Excel from bytes
            excel_buffer = io.BytesIO(file_content)
            
            if sheet_name:
                df = pd.read_excel(excel_buffer, sheet_name=sheet_name)
            else:
                df = pd.read_excel(excel_buffer)
            
            return df
            
        except Exception as e:
            print(f"Error reading Excel file: {str(e)}")
            return None


class OneDriveManager:
    """High-level OneDrive manager for HomeSpend app"""
    
    def __init__(self, access_token: str):
        self.client = GraphClient(access_token)
        self.file_path = os.getenv('ONEDRIVE_FILE_PATH', '/HomeSpend.xlsx')
        self.file_name = os.getenv('ONEDRIVE_FILE_NAME', 'HomeSpend.xlsx')
    
    def get_transactions_data(self) -> Optional[pd.DataFrame]:
        """Get transactions data from main sheet"""
        return self.client.read_excel_file(self.file_path, sheet_name='Sheet1')
    
    def file_exists(self) -> bool:
        """Check if HomeSpend.xlsx exists on OneDrive"""
        file_info = self.client.get_file_info(self.file_path)
        return file_info is not None
