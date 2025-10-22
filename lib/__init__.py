"""
CGI Framework Library
Python 3.7+ standard library only
"""

from .cgi_app import CGIApp
from .request import Request
from .response import Response
from .router import Router
from .session import Session
from .auth import Auth, login_required, admin_required
from .template import Template, render_template
from .database import Database

__all__ = [
    'CGIApp',
    'Request',
    'Response',
    'Router',
    'Session',
    'Auth',
    'login_required',
    'admin_required',
    'Template',
    'render_template',
    'Database',
]
