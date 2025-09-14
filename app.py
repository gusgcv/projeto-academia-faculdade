import os
from flask import Flask, render_template, request, redirect, url_for, g
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'academia.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Aluno(db.Model):
    __tablename__ = 'alunos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    data_nascimento = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f'<Aluno {self.nome}>'


@app.route('/')
def index():
    alunos = Aluno.query.order_by(Aluno.nome).all()
    return render_template('index.html', alunos=alunos)


@app.route('/aluno/novo', methods=['GET', 'POST'])
def novo_aluno():
    if request.method == 'POST':
        nome = request.form['nome']
        cpf = request.form['cpf']
        data_nascimento = request.form['data_nascimento']

        novo_aluno = Aluno(nome=nome, cpf=cpf, data_nascimento=data_nascimento)
        db.session.add(novo_aluno)

        db.session.commit()

        return redirect(url_for('index'))

    return render_template('form_aluno.html')


@app.route('/aluno/exluir/<int:aluno_id>', methods=['POST'])
def excluir_aluno(aluno_id):
    aluno_para_excluir = Aluno.query.get_or_404(aluno_id)
    db.session.delete(aluno_para_excluir)
    db.session.commit()

    return redirect(url_for('index'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        app.run(debug=True)
