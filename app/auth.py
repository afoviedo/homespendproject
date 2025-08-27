"""
Microsoft OAuth2 Authentication Module
Handles login, logout, token refresh and session management
"""

import os
import json
import secrets
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional, Dict, Any

import requests
from authlib.integrations.flask_client import OAuth
from flask import Flask, session, redirect, url_for, request, jsonify


class MicrosoftAuth:
    def __init__(self, app: Flask):
        self.app = app
        self.oauth = OAuth(app)
        
        # Microsoft OAuth configuration
        self.client_id = os.getenv('MS_CLIENT_ID')
        self.client_secret = os.getenv('MS_CLIENT_SECRET')
        self.tenant_id = os.getenv('MS_TENANT_ID', 'common')
        self.redirect_uri = os.getenv('MS_REDIRECT_URI')
        self.scopes = os.getenv('MS_SCOPES', 'offline_access Files.Read User.Read').split(' ')
        
        # Microsoft endpoints
        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.auth_endpoint = f"{self.authority}/oauth2/v2.0/authorize"
        self.token_endpoint = f"{self.authority}/oauth2/v2.0/token"
        
        # Register Microsoft OAuth client
        self.microsoft = self.oauth.register(
            name='microsoft',
            client_id=self.client_id,
            client_secret=self.client_secret,
            server_metadata_url=f"{self.authority}/v2.0/.well-known/openid-configuration",
            client_kwargs={
                'scope': ' '.join(self.scopes)
            }
        )
        
        self._register_routes()
    
    def _register_routes(self):
        """Register authentication routes"""
        
        @self.app.route('/login')
        def login():
            """Initiate Microsoft OAuth login"""
            # Generate state for security
            state = secrets.token_urlsafe(32)
            session['oauth_state'] = state
            
            redirect_uri = self.redirect_uri
            return self.microsoft.authorize_redirect(redirect_uri, state=state)
        
        @self.app.route('/auth/callback')
        def auth_callback():
            """Handle OAuth callback"""
            try:
                # Verify state parameter
                if request.args.get('state') != session.get('oauth_state'):
                    return jsonify({'error': 'Invalid state parameter'}), 400
                
                # Exchange authorization code for tokens
                token = self.microsoft.authorize_access_token()
                
                if not token:
                    return jsonify({'error': 'Failed to obtain access token'}), 400
                
                # Get user info
                user_info = self._get_user_info(token['access_token'])
                
                # Store tokens and user info in session
                session['access_token'] = token['access_token']
                session['refresh_token'] = token.get('refresh_token')
                session['token_expires_at'] = datetime.now() + timedelta(seconds=token.get('expires_in', 3600))
                session['user_info'] = user_info
                session['authenticated'] = True
                
                # Clear OAuth state
                session.pop('oauth_state', None)
                
                return redirect('/')
                
            except Exception as e:
                self.app.logger.error(f"OAuth callback error: {str(e)}")
                return jsonify({'error': 'Authentication failed'}), 500
        
        @self.app.route('/logout')
        def logout():
            """Logout user and clear session"""
            session.clear()
            logout_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/logout"
            return redirect(logout_url)
    
    def _get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from Microsoft Graph"""
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get('https://graph.microsoft.com/v1.0/me', headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            self.app.logger.error(f"Failed to get user info: {response.status_code}")
            return {}
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return session.get('authenticated', False) and self._is_token_valid()
    
    def _is_token_valid(self) -> bool:
        """Check if access token is still valid"""
        expires_at = session.get('token_expires_at')
        if not expires_at:
            return False
        
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at)
        
        # Token expires in less than 5 minutes - needs refresh
        return datetime.now() < expires_at - timedelta(minutes=5)
    
    def get_access_token(self) -> Optional[str]:
        """Get valid access token, refresh if necessary"""
        if not self.is_authenticated():
            return None
        
        # Check if token needs refresh
        if not self._is_token_valid():
            if self._refresh_token():
                return session.get('access_token')
            else:
                return None
        
        return session.get('access_token')
    
    def _refresh_token(self) -> bool:
        """Refresh access token using refresh token"""
        refresh_token = session.get('refresh_token')
        if not refresh_token:
            return False
        
        try:
            data = {
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'refresh_token': refresh_token,
                'grant_type': 'refresh_token',
                'scope': ' '.join(self.scopes)
            }
            
            response = requests.post(self.token_endpoint, data=data)
            
            if response.status_code == 200:
                token_data = response.json()
                
                # Update session with new tokens
                session['access_token'] = token_data['access_token']
                if 'refresh_token' in token_data:
                    session['refresh_token'] = token_data['refresh_token']
                session['token_expires_at'] = datetime.now() + timedelta(seconds=token_data.get('expires_in', 3600))
                
                return True
            else:
                self.app.logger.error(f"Token refresh failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.app.logger.error(f"Token refresh error: {str(e)}")
            return False
    
    def get_user_info(self) -> Dict[str, Any]:
        """Get current user information"""
        return session.get('user_info', {})


def require_auth(auth_instance):
    """Decorator to require authentication for routes"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not auth_instance.is_authenticated():
                return redirect('/login')
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def init_auth(app: Flask):
    """Initialize authentication for Flask app"""
    return MicrosoftAuth(app)
