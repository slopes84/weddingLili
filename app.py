from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
from datetime import datetime

# Inicializar aplicação Flask (IMPORTANTE: a variável DEVE se chamar 'app')
app = Flask(__name__)
app.config.from_pyfile('config.py')

# Garantir que as pastas de upload existam
for section in ['despedida', 'cerimonia', 'boda', 'festa', 'diversos']:
    for media_type in ['photos', 'videos']:
        os.makedirs(os.path.join(app.static_folder, 'uploads', media_type, section), exist_ok=True)

# Inicializar banco de dados
db = SQLAlchemy(app)

# Inicializar gerenciador de login
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Importar rotas e modelos
from models import User, Section, Photo, Video, Dedication
import routes

def initialize_db():
    """Inicializa o banco de dados com dados padrão se necessário"""
    # Verificar se já existem seções
    if Section.query.count() == 0:
        sections = [
            {
                'name': 'Despedida de Solteiros',
                'slug': 'despedida',
                'description': 'Momentos especiais da despedida de solteiros',
                'requires_date_check': False
            },
            {
                'name': 'Cerimônia',
                'slug': 'cerimonia',
                'description': 'A cerimônia de casamento da Lígia e do Paulo',
                'requires_date_check': True
            },
            {
                'name': 'Boda',
                'slug': 'boda',
                'description': 'A celebração da boda',
                'requires_date_check': True
            },
            {
                'name': 'Festa',
                'slug': 'festa',
                'description': 'A festa de casamento',
                'requires_date_check': True
            },
            {
                'name': 'Diversos',
                'slug': 'diversos',
                'description': 'Outros momentos especiais',
                'requires_date_check': False
            }
        ]
        
        for section_data in sections:
            section = Section(**section_data)
            db.session.add(section)
        
        # Criar usuário administrador
        from werkzeug.security import generate_password_hash
        admin = User(
            username='admin',
            email='admin@casamento.com',
            password_hash=generate_password_hash('admin123'),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()

# Inicializar o banco de dados dentro do contexto da aplicação
with app.app_context():
    db.create_all()
    initialize_db()

if __name__ == '__main__':
    app.run(debug=True)
