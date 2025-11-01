from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class ProdutoForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    preco = DecimalField('Preço (R$)', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Cadastrar')
