from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SubmitField, HiddenField, IntegerField
# 👇 CERTIFIQUE-SE DE ADICIONAR 'Email' e 'Length' AQUI
from wtforms.validators import DataRequired, NumberRange, Email, Length 

class ProdutoForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    preco = DecimalField('Preço (R$)', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Cadastrar')

# --- ADICIONE ESTA CLASSE NOVA ---
class ClienteForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired(), Length(max=100)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    # Adicionamos validação de tamanho para o CPF
    cpf = StringField('CPF (apenas números)', validators=[
        DataRequired(), 
        Length(min=11, max=11, message='O CPF deve conter 11 dígitos.')
    ])
    submit = SubmitField('Cadastrar Cliente')

class LoginForm(FlaskForm):
    cpf = StringField('CPF (apenas números)', validators=[
        DataRequired(), 
        Length(min=11, max=11, message='O CPF deve conter 11 dígitos.')
    ])
    submit = SubmitField('Entrar')

class ComprarForm(FlaskForm):
    produto_id = HiddenField(validators=[DataRequired()])
    quantidade = IntegerField('Quantidade', default=1, validators=[DataRequired(), NumberRange(min=1, message="A quantidade mínima é 1")
    ])
    submit = SubmitField("Comprar")
