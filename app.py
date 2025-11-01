from flask import Flask, render_template, redirect, url_for, flash, request
from models import db, Produto
from forms import ProdutoForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua_chave_secreta'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///loja.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

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

# NOVA ROTA: editar produto
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
