"""
Archivo de configuración Passenger WSGI para cPanel
Python 3.12 + Passenger
Usuario: najmhqti
Versión simplificada
"""

import sys
import os

# Agregar el directorio actual al path de Python
sys.path.insert(0, os.path.dirname(__file__))

# Configurar variables de entorno
os.environ['FLASK_ENV'] = 'production'

# Importar la aplicación Flask
from app import app as application

# Configuración de producción
application.config['DEBUG'] = False
application.config['PROPAGATE_EXCEPTIONS'] = True
