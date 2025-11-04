from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy import UniqueConstraint

db = SQLAlchemy()

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)
    preco = db.Column(db.Float, nullable=False)

    #adicionando relação inversa, opcional mas parece que é útil
    vendas = db.relationship('Venda', backref='produto', lazy=True)

    itens_carrinho = db.relationship("ItemCarrinho", backref="produto", lazy=True)

class Cliente(db.Model, UserMixin): #cliente herda de usermixin
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    cpf = db.Column(db.String(11), unique=True, nullable=False, index=True)

    #um cliente pode ter várias vendas
    vendas = db.relationship('Venda', backref='cliente', lazy=True)

    carrinho = db.relationship('ItemCarrinho', backref='cliente', lazy=True)

    def get_id(self):
        return str(self.id)
    
class Venda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_venda = db.Column(db.DateTime, nullable=False, default=db.func.now())
    quantidade = db.Column(db.Integer, nullable=False, default = 1)

    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'), nullable=False)

    preco_unitario = db.Column(db.Float, nullable=False)

class ItemCarrinho(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False, default = 1)

    __table_args__ = (UniqueConstraint('cliente_id', 'produto_id', name='_cliente_produto_uc'),)