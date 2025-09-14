import sqlite3
from flask import Flask, render_template_string, request, redirect, url_for, g

# Flask #
app = Flask(__name__)
DATABASE = 'academia.db'

# Base banco de dados em SQlite#


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g. _database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def init_db():
    with app.app_context():
        db = get_db()
        db.execute("""
            CREATE TABLE IF NOT EXISTS alunos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cpf TEXT UNIQUE NOT NULL,
                data_nascimento TEXT NOT NULL
            );
        """)
        db.commit()
        print("Banco de dados iniciado.")


@app.route('/')
def index():

    # pagina inicial dos ja cadastrados#
    db = get_db()
    alunos = db.execute('SELECT * FROM alunos ORDER BY nome').fetchall()
    return render_template_string(HTML_TEMPLATE_INDEX, alunos=alunos)


@app.route('/aluno/novo', methods=['GET', 'POST'])
def novo_aluno():
    if request.method == 'POST':
        nome = request.form['nome']
        cpf = request.form['cpf']
        data_nascimento = request.form['data_nascimento']

        db = get_db()
        db.execute('INSERT INTO alunos (nome, cpf, data_nascimento) VALUES (?, ?, ?)',
                   (nome, cpf, data_nascimento))
        db.commit()

        return redirect(url_for('index'))
                    
    return render_template_string(HTML_TEMPLATE_FORM_ALUNO)
    

@app.route('/aluno/exluir/<int:aluno_id>', methods=['POST'])
def excluir_aluno(aluno_id):
    db = get_db()
    db.execute('DELETE FROM alunos WHERE id= ?', (aluno_id,))
    db.commit()

    return redirect(url_for('index'))


# FAZER HTML PAGINA INICIAL AQUI#
HTML_TEMPLATE_INDEX = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Sistema de Academia</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-200 p-10">
    <div class="max-w-4xl mx-auto bg-white p-8 shadow-lg rounded-lg">
        <h1 class="text-4xl font-bold text-gray-800 mb-2">ALUNOS MATRICULADOS</h1>
        <a href="{{ url_for('novo_aluno') }}" class="bg-green-500 text-white font-semibold py-2 px-4 rounded-md mb-8 inline-block hover:bg-green-600 transition-colors">
            NOVA MATRICULA
        </a>
        <ul class="space-y-4">
            {% for aluno in alunos %}
                <li class="p-4 border-2 border-gray-800 rounded-md flex items-center">
                    <div class="flex-grow">
                        <p class="font-semibold text-lg text-gray-700">{{ aluno.nome }}</p>
                        <p class="text-sm text-gray-500">CPF: {{ aluno.cpf }}</p>
                    </div>
                    <!-- Formulário com o botão de excluir -->
                    <form action="{{ url_for('excluir_aluno', aluno_id=aluno.id) }}" method="post" class="ml-4 flex-shrink-0" onsubmit="return confirm('Tem certeza que deseja excluir este aluno?');">
                        <button type="submit" class="bg-red-500 hover:bg-red-700 text-white font-bold py-1 px-3 rounded-md text-sm transition-colors">
                            Excluir
                        </button>
                    </form>
                </li>
            {% else %}
                <li class="text-gray-500 text-center py-4">Nenhum aluno cadastrado ainda.</li>
            {% endfor %}
        </ul>
    </div>
</body>
</html>
"""

# FAZER HTML PAGINA CADASTRO DE ALUNOS#
HTML_TEMPLATE_FORM_ALUNO = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Cadastrar Aluno</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 p-10">
    <div class="max-w-lg mx-auto">
        <h1 class="text-3xl font-bold mb-6">Nova Matricula</h1>
        <div class="bg-white shadow-md rounded-lg p-8">
            <form method="post" class="space-y-4">
                <div>
                    <label for="nome" class="block font-medium">Nome Completo:</label>
                    <input type="text" name="nome" id="nome" class="w-full border border-gray-300 rounded-md p-2" required>
                </div>
                <div>
                    <label for="cpf" class="block font-medium">CPF:</label>
                    <input type="text" name="cpf" id="cpf" class="w-full border border-gray-300 rounded-md p-2" required>
                </div>
                <div>
                    <label for="data_nascimento" class="block font-medium">Data de Nascimento:</label>
                    <input type="date" name="data_nascimento" id="data_nascimento" class="w-full border border-gray-300 rounded-md p-2" required>
                </div>
                <div class="flex items-center space-x-4 pt-2">
                     <button type="submit" class="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded">
                        Salvar
                    </button>
                    <a href="{{ url_for('index') }}" class="text-gray-600 hover:underline">Cancelar</a>
                </div>
            </form>
        </div>
    </div>
</body>
</html>
"""


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
