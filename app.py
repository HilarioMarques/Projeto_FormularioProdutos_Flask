from flask import Flask, render_template, redirect, url_for, flash, request
from models import db, Produto, Cliente, Venda
from forms import ProdutoForm, ClienteForm, LoginForm, ComprarForm
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua_chave_secreta'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///loja.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, faça login para acessar essa página.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return Cliente.query.get(int(user_id))

with app.app_context():
    db.create_all()

#ROTA PADRÃO 
@app.route('/')
def index():
    return render_template('index.html')

#AUTENTICAÇÃO DO CLIENTE
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('listar_produtos_cliente'))
    
    form = LoginForm()
    if form.validate_on_submit():
        cpf = form.cpf.data
        cliente = Cliente.query.filter_by(cpf=cpf).first()

        #decidi fazer a autenticação por cpf
        if cliente:
            login_user(cliente)
            flash(f'Login realizado com sucesso! Bem-vindo(a), {cliente.nome}.', 'success')

            return redirect(url_for("listar_produtos_cliente"))
        else:
            flash("CPF não encontrado. Por favor verifique o número.", "danger")
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Você saiu da sua conta.", "info")
    return redirect(url_for("index"))

#ROTAS DE CLIENTE/COMPRA

#LISTAR PRODUTOS PARA CLIENTE LOGADO
@app.route('/comprar')
@login_required
def listar_produtos_cliente():
    produtos = Produto.query.all()
    forms_compra = {p.id: ComprarForm(produto_id=p.id) for p in produtos}
    return render_template('lista_produtos_cliente.html', produtos=produtos, forms_compra=forms_compra)

#REALIZAR COMPRA
@app.route('/comprar_produto/<int:produto_id>', methods=["POST"])
@login_required
def comprar_produto(produto_id):
    produto = Produto.query.get_or_404(produto_id)
    form = ComprarForm(request.form)

    # O ID do produto vem no campo hidden, mas o Flask-WTF exige que o form.validate_on_submit() seja chamado e que o campo 'produto_id' no form seja preenchido corretamente pelo lado do cliente.
    # Como produto_id está passando na URL e no form, vamos apenas garantir que o form seja válido.
    
    # Vou preencher o campo produto_id manualmente para validação, pois ele não é submetido como um campo 'name' padrão.
    # Poderia passar o produto_id no HiddenField. Vou considerar que o HiddenField está sendo usado.

    if form.validate_on_submit() and int(form.produto_id.data) == produto_id:

        quantidade = form.quantidade.data

        venda = Venda(
            cliente_id=current_user.id,
            produto_id=produto.id,
            preco_unitario=produto.preco,
            quantidade=quantidade
        )

        db.session.add(venda)
        db.session.commit()

        flash(f"Compra de {quantidade}x {produto.nome} realizada com sucesso! (Total: R$ {produto.preco * quantidade:.2f})", "success")
        return redirect(url_for('listar_produtos_cliente'))
    
    flash("Falha na compra. Verifique a quantidade.", "danger")
    return redirect(url_for("listar_produtos_cliente"))


#VER AS COMPRAS DO CLIENTE LOGADO
@app.route('/minhas_compras')
@login_required
def minhas_compras():
    compras = Venda.query.filter_by(cliente_id=current_user.id).order_by(Venda.data_venda.desc()).all()
    return render_template("minhas_compras.html", compras=compras)


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
#qualquer coisa
