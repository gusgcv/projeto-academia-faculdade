import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'academia.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)


class Aluno(db.Model):
    __tablename__ = 'alunos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    foto = db.Column(db.String(100), nullable=True, default='default.png')
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    data_nascimento = db.Column(db.String(10), nullable=False)
    endereco = db.Column(db.String(200), nullable=True)
    cidade = db.Column(db.String(100), nullable=True)
    estado = db.Column(db.String(2), nullable=True)
    cep = db.Column(db.String(9), nullable=True)
    telefone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=True)
    data_matricula = db.Column(db.String(10), nullable=True)
    status = db.Column(db.String(10), default= 'Ativo', nullable=False)

class Funcionario(db.Model):
    __tablename__ = 'funcionarios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    foto = db.Column(db.String(100), nullable=True, default='default.png')
    cargo = db.Column(db.String(50), nullable=False)
    cref = db.Column(db.String(20), unique=True, nullable=True)
    endereco = db.Column(db.String(200), nullable=True)
    cidade = db.Column(db.String(100), nullable=True)
    estado = db.Column(db.String(2), nullable=True)
    cep = db.Column(db.String(9), nullable=True)
    telefone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=True)
    data_admissao = db.Column(db.String(10), nullable=True)



@app.route('/')
def index():
    total_alunos = Aluno.query.count()
    total_funcionarios = Funcionario.query.count()
    return render_template('dashboard.html', total_alunos=total_alunos, total_funcionarios=total_funcionarios)

@app.route('/alunos')
def lista_alunos():
    alunos = Aluno.query.order_by(Aluno.nome).all()
    return render_template('lista_alunos.html', alunos=alunos)

@app.route('/aluno/perfil/<int:aluno_id>')
def perfil_aluno(aluno_id):
    aluno = Aluno.query.get_or_404(aluno_id)
    return render_template('perfil_aluno.html', aluno=aluno)

@app.route('/aluno/novo', methods=['GET', 'POST'])
def novo_aluno():
    if request.method == 'POST':
        foto_filename = 'default.png'
        if 'foto' in request.files:
            file = request.files['foto']
            if file.filename != '':
                foto_filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], foto_filename))

        novo_aluno = Aluno(
            foto=foto_filename,
            nome = request.form['nome'],
            cpf = request.form['cpf'],
            data_nascimento = request.form['data_nascimento'],
            endereco=request.form.get('endereco'),
            cidade=request.form.get('cidade'),
            estado=request.form.get('estado'),
            cep=request.form.get('cep'),
            telefone=request.form.get('telefone'),
            email=request.form.get('email'),
            data_matricula=request.form.get('data_matricula'),
            status=request.form['status'] 
        )
        db.session.add(novo_aluno)
        db.session.commit()
        return redirect(url_for('lista_alunos'))
    return render_template('form_aluno.html')

@app.route('/aluno/editar/<int:aluno_id>', methods=['GET', 'POST'])
def editar_aluno(aluno_id):
    aluno = Aluno.query.get_or_404(aluno_id)
    if request.method == 'POST':
        aluno.nome = request.form['nome']
        aluno.cpf = request.form['cpf']
        aluno.data_nascimento = request.form['data_nascimento']
        aluno.endereco = request.form.get('endereco')
        aluno.cidade = request.form.get('cidade')
        aluno.estado = request.form.get('estado')
        aluno.cep = request.form.get('cep')
        aluno.telefone = request.form.get('telefone')
        aluno.email = request.form.get('email')
        aluno.data_matricula = request.form.get('data_matricula')
        aluno.status = request.form['status']
        
        if 'foto' in request.files:
            file = request.files['foto']
            if file.filename != '':
                foto_filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], foto_filename))
                aluno.foto = foto_filename

        db.session.commit()
    
        return redirect(url_for('perfil_aluno', aluno_id=aluno.id))
    return render_template('form_aluno.html', aluno=aluno)

@app.route('/aluno/excluir/<int:aluno_id>', methods=['POST'])
def excluir_aluno(aluno_id):
    aluno_para_excluir = Aluno.query.get_or_404(aluno_id)
    if aluno_para_exluir.foto != 'default.png':
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], aluno.foto))
        except OSError:
            pass
    db.session.delete(aluno_para_excluir)
    db.session.commit()
    return redirect(url_for('lista_alunos'))

@app.route('/funcionarios')
def lista_funcionarios():
    funcionarios = Funcionario.query.order_by(Funcionario.nome).all()
    return render_template('lista_funcionarios.html', funcionarios=funcionarios)

@app.route('/funcionario/perfil/<int:funcionario_id>')
def perfil_funcionario(funcionario_id):
    funcionario = Funcionario.query.get_or_404(funcionario_id)
    return render_template('perfil_funcionario.html', funcionario=funcionario)

@app.route('/funcionario/novo', methods=['GET', 'POST'])
def novo_funcionario():
    if request.method == 'POST':
        foto_filename = 'default.png'
        if 'foto' in request.files:
            file = request.files['foto']
            if file.filename != '':
                foto_filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], foto_filename))

        novo_funcionario = Funcionario(
            foto=foto_filename,
            nome = request.form['nome'],
            cargo=request.form['cargo'],
            cref = request.form.get('cref'),
            endereco=request.form.get('endereco'),
            cidade=request.form.get('cidade'),
            estado=request.form.get('estado'),
            cep=request.form.get('cep'),
            telefone=request.form.get('telefone'),
            data_admissao=request.form.get('data_admissao'),
            email=request.form.get('email')
        )
        db.session.add(novo_funcionario)
        db.session.commit()
        return redirect(url_for('lista_funcionarios'))
    return render_template('form_funcionario.html')

@app.route('/funcionario/editar/<int:funcionario_id>', methods=['GET', 'POST'])
def editar_funcionario(funcionario_id):
    funcionario = Funcionario.query.get_or_404(funcionario_id)
    if request.method == 'POST':
        funcionario.nome = request.form['nome']
        funcionario.cargo = request.form['cargo']
        funcionario.data_admissao = request.form.get('data_admissao')
        funcionario.cref = request.form.get('cref')
        funcionario.endereco = request.form.get('endereco')
        funcionario.cidade = request.form.get('cidade')
        funcionario.estado = request.form.get('estado')
        funcionario.cep = request.form.get('cep')
        funcionario.telefone = request.form.get('telefone')
        funcionario.email = request.form.get('email')

        if 'foto' in request.files:
            file = request.files['foto']
            if file.filename != '':
                foto_filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], foto_filename))
                funcionario.foto = foto_filename
        
        db.session.commit()
        return redirect(url_for('perfil_funcionario', funcionario_id=funcionario.id))
    return render_template('form_funcionario.html', funcionario=funcionario)

@app.route('/funcionario/excluir/<int:funcionario_id>', methods=['POST'])
def excluir_funcionario(funcionario_id):
    funcionario_para_excluir = Funcionario.query.get_or_404(funcionario_id)
    if funcionario_para_exluir.foto != 'default.png':
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], func.foto))
        except OSError:
            pass
    db.session.delete(funcionario_para_excluir)
    db.session.commit()
    return redirect(url_for('lista_funcionarios'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
