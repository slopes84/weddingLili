from flask import current_app
from datetime import datetime
import os

def get_file_path(media_type, section_slug, filename):
    """Gera o caminho do arquivo para exibição"""
    return os.path.join('uploads', media_type, section_slug, filename)

def check_date_availability():
    """Verifica se a data limite para acessar seções restritas foi atingida"""
    now = datetime.now()
    return now >= current_app.config['SECTIONS_AVAILABLE_DATE']

def format_date(date):
    """Formata data para exibição no formato brasileiro"""
    return date.strftime('%d/%m/%Y')
