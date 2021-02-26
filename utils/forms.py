from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField, SelectField, \
    IntegerField, TimeField, FieldList, FormField
from wtforms.validators import DataRequired, Optional, ValidationError, Email, EqualTo
from utils.models import Employee, Brigade, Order, Material, CardinalityViolation


class MaterialField(FlaskForm):
    material = SelectField('Материал', validators=[DataRequired()], choices=[x.name for x in Material.nodes.all()]
                           , validate_choice=False)
    count = IntegerField('Количество', validators=[DataRequired()])


class CreateEmployee(FlaskForm):
    name = StringField('Имя сотрудника', validators=[DataRequired()])
    birth_date = DateField('Дата рождение', validators=[DataRequired()])
    passport = StringField('Пасспорт', validators=[DataRequired()])
    position = StringField('Должность', validators=[DataRequired()])

    brigade = IntegerField('Номер бригады', validators=[DataRequired()])

    submit = SubmitField('Добавить сотрудника')


class CreateOrder(FlaskForm):
    brigade = SelectField('Бригада', validators=[DataRequired()], validate_choice=False)
    number = IntegerField('Номер', validators=[DataRequired()])

    material = FieldList(FormField(MaterialField), 'Материал', min_entries=1)

    cost = IntegerField('Стоимость работы', validators=[DataRequired()])

    submit = SubmitField('Добавить пациента')

    def validate_brigade(self, brigade):
        brigade = Brigade.nodes.get_or_none(number=brigade.data)
        not_done_orders = [x for x in brigade.order.all() if not x.is_done]
        if not_done_orders:
            raise ValidationError('Эта бригада уже занята другим заказом!')

    def validate_number(self, number):
        order = Order.nodes.get_or_none(number=str(number.data))
        if order is not None:
            raise ValidationError('Такой заказ уже существует.')
