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

    treinos = db.relationship('Treino', back_populates='aluno', lazy=True, cascade="all, delete-orphan")

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
    
    treinos = db.relationship('Treino', back_populates='funcionario', lazy=True)


class Exercicio(db.Model):
    __tablename__ = 'exercicios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    grupo_muscular = db.Column(db.String(255), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    itens_treino = db.relationship('ItemTreino', back_populates='exercicio', lazy=True)
    

class Treino(db.Model):
    __tablename__ = 'treinos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    aluno_id = db.Column(db.Integer, db.ForeignKey('alunos.id'), nullable=False)
    funcionario_id = db.Column(db.Integer, db.ForeignKey('funcionarios.id'), nullable=True)
    aluno = db.relationship('Aluno', back_populates='treinos')
    funcionario = db.relationship('Funcionario', back_populates='treinos')
    itens = db.relationship('ItemTreino', back_populates='treino', lazy=True, cascade="all, delete-orphan")

class ItemTreino(db.Model):
    __tablename__ = 'itens_treino'
    id = db.Column(db.Integer, primary_key=True)
    treino_id = db.Column(db.Integer, db.ForeignKey('treinos.id'), nullable=False)
    exercicio_id = db.Column(db.Integer, db.ForeignKey('exercicios.id'), nullable=False)
    series = db.Column(db.String(20), nullable=False)
    repeticoes = db.Column(db.String(20), nullable=True)
    descanso_seg = db.Column(db.Integer, nullable=True)
    observacoes = db.Column(db.Text, nullable=True)

    treino = db.relationship('Treino', back_populates='itens')
    exercicio = db.relationship('Exercicio', back_populates='itens_treino')


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
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], funcionario_para_excluir.foto))
        except OSError:
            pass
    db.session.delete(funcionario_para_excluir)
    db.session.commit()
    return redirect(url_for('lista_funcionarios'))

@app.route('/exercicios')
def lista_exercicios():
    exercicios = Exercicio.query.order_by(Exercicio.grupo_muscular, Exercicio.nome).all()
    return render_template('lista_exercicios.html', exercicios=exercicios)

@app.route('/exercicio/novo', methods=['GET', 'POST'])
def novo_exercicio():
    if request.method == 'POST':
        grupos_selecionados = request.form.getlist('grupo_muscular')
        grupos_string = ",".join(grupos_selecionados)

        novo_ex = Exercicio(
            nome=request.form['nome'],
            grupo_muscular=grupos_string,
            descricao=request.form.get('descricao')
        )
        db.session.add(novo_ex)
        db.session.commit()
        return redirect(url_for('lista_exercicios'))
    return render_template('form_exercicio.html', exercicio=None)

@app.route('/exercicio/editar/<int:exercicio_id>', methods=['GET', 'POST'])
def editar_exercicio(exercicio_id):
    exercicio = Exercicio.query.get_or_404(exercicio_id)
    if request.method == 'POST':
        grupos_selecionados = request.form.getlist('grupo_muscular')
        grupos_string = ",".join(grupos_selecionados)

        exercicio.nome = request.form['nome']
        exercicio.grupo_muscular = grupos_string
        exercicio.descricao = request.form.get('descricao')
        db.session.commit()
        return redirect(url_for('lista_exercicios'))
    return render_template('form_exercicio.html', exercicio=exercicio)

@app.route('/exercicio/excluir/<int:exercicio_id>', methods=['POST'])
def excluir_exercicio(exercicio_id):
    exercicio_para_excluir = Exercicio.query.get_or_404(exercicio_id)
    db.session.delete(exercicio_para_excluir)
    db.session.commit()
    return redirect(url_for('lista_exercicios'))

@app.route('/aluno/<int:aluno_id>/treinos')
def gerenciar_treinos(aluno_id):
    aluno = Aluno.query.get_or_404(aluno_id)
    exercicios_disponiveis = Exercicio.query.order_by(Exercicio.nome).all()
    return render_template('gerenciar_treinos.html', aluno=aluno, exercicios_disponiveis=exercicios_disponiveis)

@app.route('/aluno/<int:aluno_id>/treino/novo', methods=['POST'])
def novo_treino(aluno_id):
    nome_treino = request.form['nome_treino']
    novo_treino = Treino(
        nome=nome_treino,
        aluno_id=aluno_id,
        funcionario_id=None 
    )
    db.session.add(novo_treino)
    db.session.commit()
    return redirect(url_for('gerenciar_treinos', aluno_id=aluno_id))

@app.route('/treino/<int:treino_id>/excluir', methods=['POST'])
def excluir_treino(treino_id):
    treino = Treino.query.get_or_404(treino_id)
    aluno_id = treino.aluno_id
    db.session.delete(treino)
    db.session.commit()
    return redirect(url_for('gerenciar_treinos', aluno_id=aluno_id))

@app.route('/treino/<int:treino_id>/adicionar_item', methods=['POST'])
def adicionar_item_treino(treino_id):
    treino = Treino.query.get_or_404(treino_id)
    
    novo_item = ItemTreino(
        treino_id=treino.id,
        exercicio_id=request.form['exercicio_id'],
        series=request.form.get('series'),
        repeticoes=request.form.get('repeticoes'),
        descanso_seg=request.form.get('descanso_seg'),
        observacoes=request.form.get('observacoes')
    )
    db.session.add(novo_item)
    db.session.commit()
    return redirect(url_for('gerenciar_treinos', aluno_id=treino.aluno_id))

@app.route('/item_treino/<int:item_id>/excluir', methods=['POST'])
def excluir_item_treino(item_id):
    item = ItemTreino.query.get_or_404(item_id)
    aluno_id = item.treino.aluno_id
    db.session.delete(item)
    db.session.commit()
    return redirect(url_for('gerenciar_treinos', aluno_id=aluno_id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
