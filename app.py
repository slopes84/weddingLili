
from flask import Flask, request, jsonify, send_from_directory, render_template
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
DEDICATORIAS_FILE = 'dedicatorias.txt'
ADMIN_PASSWORD = 'admin123'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    password = request.form.get('password')
    if password != ADMIN_PASSWORD:
        return jsonify({'error': 'Acesso negado'}), 403

    if 'file' not in request.files or 'category' not in request.form:
        return jsonify({'error': 'Faltando dados no formulário'}), 400

    file = request.files['file']
    category = request.form['category']

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        category_path = os.path.join(app.config['UPLOAD_FOLDER'], category)
        os.makedirs(category_path, exist_ok=True)
        file.save(os.path.join(category_path, filename))
        return jsonify({'message': 'Upload concluído com sucesso!'}), 200

    return jsonify({'error': 'Arquivo inválido'}), 400

@app.route('/images/<category>', methods=['GET'])
def list_images(category):
    category_path = os.path.join(app.config['UPLOAD_FOLDER'], category)
    if not os.path.exists(category_path):
        return jsonify([])

    files = os.listdir(category_path)
    urls = [f'/uploads/{category}/{file}' for file in files if allowed_file(file)]
    return jsonify(urls)

@app.route('/uploads/<category>/<filename>')
def uploaded_file(category, filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], category), filename)

@app.route('/dedicatorias', methods=['POST'])
def save_dedicatoria():
    mensagem = request.form.get('mensagem')
    if not mensagem:
        return jsonify({'error': 'Mensagem não fornecida'}), 400

    with open(DEDICATORIAS_FILE, 'a', encoding='utf-8') as f:
        f.write(mensagem + '\n')

    return jsonify({'message': 'Dedicatória salva com sucesso!'}), 200

@app.route('/dedicatorias', methods=['GET'])
def list_dedicatorias():
    if not os.path.exists(DEDICATORIAS_FILE):
        return jsonify([])

    with open(DEDICATORIAS_FILE, 'r', encoding='utf-8') as f:
        mensagens = [line.strip() for line in f.readlines() if line.strip()]

    return jsonify(mensagens)

if __name__ == '__main__':
    app.run(debug=True)
