from flask import Flask, render_template, redirect, url_for, flash, request
from models import db, Produto, Cliente
from forms import ProdutoForm, ClienteForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua_chave_secreta'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///loja.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

#ROTA PARA ADICIONAR E LISTAR CLIENTES

@app.route('/add_cliente', methods=['GET', 'POST'])
def add_cliente():
    form = ClienteForm()
    if form.validate_on_submit():
        # Verificação para evitar duplicatas (já que email e cpf são únicos no models.py)
        existing_email = Cliente.query.filter_by(email=form.email.data).first()
        existing_cpf = Cliente.query.filter_by(cpf=form.cpf.data).first()

        if existing_email:
            flash('Este email já está cadastrado.', 'danger')
        elif existing_cpf:
            flash('Este CPF já está cadastrado.', 'danger')
        else:
            cliente = Cliente(
                nome=form.nome.data,
                email=form.email.data,
                cpf=form.cpf.data
            )
            db.session.add(cliente)
            db.session.commit()
            flash(f'Cliente "{cliente.nome}" cadastrado com sucesso!', 'success')
            return redirect(url_for('listar_clientes'))
            
    return render_template('form_cliente.html', form=form)

@app.route('/clientes')
def listar_clientes():
    clientes = Cliente.query.all()
    return render_template('lista_clientes.html', clientes=clientes)

@app.route('/add_produto', methods=['GET', 'POST'])
def add_produto():
    form = ProdutoForm()
    if form.validate_on_submit():
        produto = Produto(nome=form.nome.data, preco=float(form.preco.data))
        db.session.add(produto)
        db.session.commit()
        flash(f'Produto "{produto.nome}" cadastrado com sucesso!', 'success')
        return redirect(url_for('listar_produtos'))
    return render_template('form_produto.html', form=form)

@app.route('/produtos')
def listar_produtos():
    produtos = Produto.query.all()
    return render_template('lista_produtos.html', produtos=produtos)

#Nova rota: remover produtos
@app.route('/remover_produto/<int:id>', methods=['POST'])
def remover_produto(id):
    produto = Produto.query.get_or_404(id)
    db.session.delete(produto)
    db.session.commit()
    flash(f'Produto "{produto.nome}" removido com sucesso!', 'success')
    return redirect(url_for('listar_produtos'))

# NOVA ROTA: editar produtos
@app.route('/editar_produto/<int:id>', methods=['GET', 'POST'])
def editar_produto(id):
    produto = Produto.query.get_or_404(id)
    form = ProdutoForm(obj=produto)  # pré-preenche o formulário
    if form.validate_on_submit():
        produto.nome = form.nome.data
        produto.preco = float(form.preco.data)
        db.session.commit()
        flash(f'Produto "{produto.nome}" atualizado com sucesso!', 'success')
        return redirect(url_for('listar_produtos'))
    return render_template('form_produto.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
