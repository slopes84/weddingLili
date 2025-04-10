from flask import render_template, redirect, url_for, flash, request, abort, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app import app, db
from models import User, Section, Photo, Video, Dedication
import os
from datetime import datetime
import uuid
import imghdr
import mimetypes

# Funções auxiliares
def allowed_photo(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_PHOTO_EXTENSIONS']

def allowed_video(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_VIDEO_EXTENSIONS']

def check_restricted_sections_availability():
    now = datetime.now()
    return now >= app.config['SECTIONS_AVAILABLE_DATE']

# Contexto global para templates
@app.context_processor
def inject_context():
    def get_sections():
        sections = Section.query.all()
        if not current_user.is_authenticated or (current_user.is_authenticated and not current_user.is_admin):
            if not check_restricted_sections_availability():
                sections = [s for s in sections if not s.requires_date_check]
        return sections
    
    return dict(
        wedding_date=app.config['WEDDING_DATE'],
        theme=app.config['THEME'],
        bride_name=app.config['BRIDE_NAME'],
        groom_name=app.config['GROOM_NAME'],
        get_sections=get_sections
    )

# Rotas
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Verificar se usuário ou email já existem
        user_exists = User.query.filter_by(username=username).first()
        email_exists = User.query.filter_by(email=email).first()
        
        if user_exists:
            flash('Nome de usuário já existe')
            return redirect(url_for('register'))
        
        if email_exists:
            flash('Email já está em uso')
            return redirect(url_for('register'))
        
        # Criar novo usuário
        new_user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registro realizado com sucesso!')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if not user or not check_password_hash(user.password_hash, password):
            flash('Credenciais inválidas')
            return redirect(url_for('login'))
        
        login_user(user)
        return redirect(url_for('index'))
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/section/<slug>')
@login_required
def section(slug):
    section = Section.query.filter_by(slug=slug).first_or_404()
    
    # Verificar disponibilidade da seção
    if section.requires_date_check and not check_restricted_sections_availability():
        if not current_user.is_admin:
            flash('Esta seção estará disponível a partir de 16 de maio de 2025')
            return redirect(url_for('index'))
    
    photos = Photo.query.filter_by(section_id=section.id).order_by(Photo.upload_date.desc()).all()
    videos = Video.query.filter_by(section_id=section.id).order_by(Video.upload_date.desc()).all()
    
    return render_template('section.html', section=section, photos=photos, videos=videos)

@app.route('/upload/photo/<section_slug>', methods=['POST'])
@login_required
def upload_photo(section_slug):
    section = Section.query.filter_by(slug=section_slug).first_or_404()
    
    # Verificar disponibilidade da seção
    if section.requires_date_check and not check_restricted_sections_availability():
        if not current_user.is_admin:
            flash('Esta seção estará disponível a partir de 16 de maio de 2025')
            return redirect(url_for('index'))
    
    if 'photo' not in request.files:
        flash('Nenhum arquivo selecionado')
        return redirect(url_for('section', slug=section_slug))
    
    file = request.files['photo']
    
    if file.filename == '':
        flash('Nenhum arquivo selecionado')
        return redirect(url_for('section', slug=section_slug))
    
    if file and allowed_photo(file.filename):
        # Criar nome único para o arquivo
        original_filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{original_filename}"
        
        # Caminho para salvar o arquivo
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'photos', section_slug, unique_filename)
        file.save(file_path)
        
        # Salvar no banco de dados
        new_photo = Photo(
            filename=unique_filename,
            original_filename=original_filename,
            section_id=section.id,
            user_id=current_user.id
        )
        
        db.session.add(new_photo)
        db.session.commit()
        
        flash('Foto enviada com sucesso!')
    else:
        flash('Tipo de arquivo não permitido')
    
    return redirect(url_for('section', slug=section_slug))

@app.route('/upload/video/<section_slug>', methods=['POST'])
@login_required
def upload_video(section_slug):
    section = Section.query.filter_by(slug=section_slug).first_or_404()
    
    # Verificar disponibilidade da seção
    if section.requires_date_check and not check_restricted_sections_availability():
        if not current_user.is_admin:
            flash('Esta seção estará disponível a partir de 16 de maio de 2025')
            return redirect(url_for('index'))
    
    if 'video' not in request.files:
        flash('Nenhum arquivo selecionado')
        return redirect(url_for('section', slug=section_slug))
    
    file = request.files['video']
    
    if file.filename == '':
        flash('Nenhum arquivo selecionado')
        return redirect(url_for('section', slug=section_slug))
    
    if file and allowed_video(file.filename):
        # Criar nome único para o arquivo
        original_filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{original_filename}"
        
        # Caminho para salvar o arquivo
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'videos', section_slug, unique_filename)
        file.save(file_path)
        
        # Salvar no banco de dados
        new_video = Video(
            filename=unique_filename,
            original_filename=original_filename,
            section_id=section.id,
            user_id=current_user.id
        )
        
        db.session.add(new_video)
        db.session.commit()
        
        flash('Vídeo enviado com sucesso!')
    else:
        flash('Tipo de arquivo não permitido')
    
    return redirect(url_for('section', slug=section_slug))

@app.route('/dedication', methods=['POST'])
@login_required
def add_dedication():
    content = request.form.get('content')
    
    if not content:
        flash('A dedicatória não pode estar vazia')
        return redirect(url_for('index'))
    
    new_dedication = Dedication(
        content=content,
        user_id=current_user.id
    )
    
    db.session.add(new_dedication)
    db.session.commit()
    
    flash('Dedicatória enviada com sucesso!')
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        abort(403)
    
    dedications = Dedication.query.order_by(Dedication.creation_date.desc()).all()
    users = User.query.all()
    photos = Photo.query.order_by(Photo.upload_date.desc()).all()
    videos = Video.query.order_by(Video.upload_date.desc()).all()
    
    return render_template('admin.html', 
                          dedications=dedications, 
                          users=users,
                          photos=photos,
                          videos=videos)

# Rota de download apenas para administradores
@app.route('/download/<type>/<filename>')
@login_required
def download_file(type, filename):
    if not current_user.is_admin:
        abort(403)
    
    if type == 'photo':
        item = Photo.query.filter_by(filename=filename).first_or_404()
        folder = 'photos'
    elif type == 'video':
        item = Video.query.filter_by(filename=filename).first_or_404()
        folder = 'videos'
    else:
        abort(404)
    
    section_slug = item.section.slug
    
    return send_from_directory(
        os.path.join(app.config['UPLOAD_FOLDER'], folder, section_slug),
        filename,
        as_attachment=True,
        download_name=item.original_filename
    )
