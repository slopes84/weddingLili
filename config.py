import os
from datetime import datetime

# Configurações básicas
SECRET_KEY = 'ligia_paulo_casamento_2025'
BASEDIR = os.path.abspath(os.path.dirname(__file__))

# Configurações do banco de dados
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASEDIR, 'wedding.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Configurações de upload
UPLOAD_FOLDER = os.path.join(BASEDIR, 'static', 'uploads')
ALLOWED_PHOTO_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv', 'webm'}
MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB limite máximo

# Datas importantes
WEDDING_DATE = datetime(2025, 5, 17)
SECTIONS_AVAILABLE_DATE = datetime(2025, 5, 16)

# Tema e cores
THEME = {
    'primary_color': '#E6E6FA',  # Lilás claro
    'secondary_color': '#F5F5DC',  # Bege
    'font_primary': 'Playfair Display, serif',
    'font_secondary': 'Montserrat, sans-serif'
}

# Nomes dos noivos
BRIDE_NAME = 'Lígia'
GROOM_NAME = 'Paulo'
