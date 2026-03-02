import os
import sys
from pathlib import Path
from django.core.asgi import get_asgi_application

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT.parent))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
application = get_asgi_application()
