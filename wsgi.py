import sys
import os

# Add your project directory to the Python path
project_home = f'/home/{os.getenv("USER", "mikenkan001")}/X'
if project_home not in sys.path:
    sys.path.append(project_home)

# Import the Flask app
from app import app as application
