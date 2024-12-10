from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import functools

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notes.db'
app.config['SECRET_KEY'] = 'seu_secret_key_aqui'  # Altere para uma chave secreta forte
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    notes = db.relationship('Note', backref='author', lazy=True)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    code = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(50))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'code': self.code,
            'language': self.language,
            'description': self.description,
            'created_at': self.created_at.strftime('%d/%m/%Y %H:%M')
        }

with app.app_context():
    db.create_all()

def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor, faça login para continuar.', 'error')
            return redirect(url_for('login'))
        
        user = User.query.filter_by(id=session['user_id']).first()
        if not user:
            session.pop('user_id', None)
            flash('Sessão inválida. Por favor, faça login novamente.', 'error')
            return redirect(url_for('login'))
            
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def home():
    if 'user_id' in session:
        user = User.query.filter_by(id=session['user_id']).first()
        if user:
            return redirect(url_for('notes'))
        session.pop('user_id', None)
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        user = User.query.filter_by(id=session['user_id']).first()
        if user:
            return redirect(url_for('notes'))
        session.pop('user_id', None)
        
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('notes'))
        
        return render_template('login.html', error='Email ou senha incorretos')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        user = User.query.filter_by(id=session['user_id']).first()
        if user:
            return redirect(url_for('notes'))
        session.pop('user_id', None)
        
    if request.method == 'POST':
        try:
            name = request.form['name']
            email = request.form['email']
            password = request.form['password']
            confirm_password = request.form['confirm_password']

            if password != confirm_password:
                return render_template('register.html', error='As senhas não coincidem')

            if User.query.filter_by(email=email).first():
                return render_template('register.html', error='Email já cadastrado')

            hashed_password = generate_password_hash(password)
            new_user = User(name=name, email=email, password=hashed_password)
            
            db.session.add(new_user)
            db.session.commit()
            
            session['user_id'] = new_user.id
            flash('Conta criada com sucesso!', 'success')
            return redirect(url_for('notes'))
            
        except Exception as e:
            db.session.rollback()
            return render_template('register.html', error='Erro ao criar conta. Tente novamente.')
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('home'))

@app.route('/notes')
@login_required
def notes():
    user = User.query.filter_by(id=session['user_id']).first()
    notes = Note.query.filter_by(user_id=user.id).order_by(Note.created_at.desc()).all()
    return render_template('index.html', notes=notes, user=user)

@app.route('/add_note', methods=['POST'])
@login_required
def add_note():
    try:
        title = request.form['title']
        code = request.form['code']
        language = request.form['language']
        description = request.form['description']
        
        new_note = Note(
            title=title,
            code=code,
            language=language,
            description=description,
            user_id=session['user_id']
        )
        db.session.add(new_note)
        db.session.commit()
        
        flash('Nota adicionada com sucesso!', 'success')
        return redirect(url_for('notes'))
    except Exception as e:
        flash('Erro ao adicionar nota. Tente novamente.', 'error')
        return redirect(url_for('notes'))

@app.route('/delete_note/<int:id>', methods=['POST'])
@login_required
def delete_note(id):
    try:
        note = Note.query.get_or_404(id)
        if note.user_id != session['user_id']:
            return jsonify({'success': False, 'message': 'Acesso negado'}), 403
            
        db.session.delete(note)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Nota excluída com sucesso!'})
    except Exception as e:
        return jsonify({'success': False, 'message': 'Erro ao excluir nota.'}), 500

@app.template_filter('strftime')
def _jinja2_filter_datetime(date, fmt=None):
    if fmt is None:
        fmt = '%d/%m/%Y %H:%M'
    return date.strftime(fmt)

# Criar tabelas
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True) 
