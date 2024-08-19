import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from database import init_db, get_db

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'
app.config['UPLOAD_FOLDER'] = '../main_site/uploads'
ALLOWED_EXTENSIONS = {'mp4', 'pdf'}

init_db()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            flash('Login bem-sucedido!', 'success')
            return redirect(url_for('member_area'))
        flash('Usuário ou senha inválidos', 'error')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        if db.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone():
            flash('Nome de usuário já existe', 'error')
        else:
            db.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                       (username, generate_password_hash(password)))
            db.commit()
            flash('Registro bem-sucedido! Faça o login.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/member_area')
def member_area():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    db = get_db()
    courses = db.execute('SELECT * FROM courses').fetchall()
    return render_template('member_area.html', courses=courses)

@app.route('/upload_course', methods=['GET', 'POST'])
def upload_course():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        content = request.form['content']
        video = request.files['video']
        pdf = request.files['pdf']

        video_path = None
        pdf_path = None

        if video and allowed_file(video.filename):
            video_filename = secure_filename(video.filename)
            video_path = os.path.join('uploads', 'videos', video_filename)
            video.save(os.path.join(app.root_path, 'static', video_path))

        if pdf and allowed_file(pdf.filename):
            pdf_filename = secure_filename(pdf.filename)
            pdf_path = os.path.join('uploads', 'pdfs', pdf_filename)
            pdf.save(os.path.join(app.root_path, 'static', pdf_path))

        db = get_db()
        db.execute('INSERT INTO courses (title, description, content, video_path, pdf_path) VALUES (?, ?, ?, ?, ?)',
                   (title, description, content, video_path, pdf_path))
        db.commit()

        flash('Curso adicionado com sucesso!', 'success')
        return redirect(url_for('member_area'))

    return render_template('upload_course.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)