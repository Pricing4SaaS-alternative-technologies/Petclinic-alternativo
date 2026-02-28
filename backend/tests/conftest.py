import sys
import os

# Agregar la carpeta padre (backend) al path para que pytest encuentre el módulo app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
