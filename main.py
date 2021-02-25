from app import app, csrf
from flask import Flask, render_template, redirect, url_for, flash, request, current_app, send_from_directory

from utils.models import Employee, Brigade, Order, Material, generate_export, import_from_csv
from utils.forms import CreateEmployee, CreateOrder

from utils.stats import get_pie, get_done_orders_for_every_brigade

import os
import pandas as pd

import threading


@app.route('/uploads/<path:filename>')
def export(filename):
    uploads = os.path.join(current_app.root_path, app.config['UPLOAD_FOLDER'])
    generate_export()
    return send_from_directory(directory=uploads, filename=filename)


@app.route('/import_db', methods=['POST'])
def import_db():
    file = request.files.get('file')
    file.save(app.config['UPLOAD_FOLDER'] + '/import.csv')
    df = pd.read_csv('files/import.csv', encoding='utf-8')

    df[df['_labels'] == ':Brigade'].to_csv('files/Brigade.csv', sep=',', encoding='utf-8')
    df[df['_labels'] == ':Order'].to_csv('files/Order.csv', sep=',', encoding='utf-8')
    df[df['_labels'] == ':Employee'].to_csv('files/Employee.csv', sep=',', encoding='utf-8')
    df[df['_labels'] == ':Material'].to_csv('files/Material.csv', sep=',', encoding='utf-8')

    df[df['_type'] == 'BRIGADE'].to_csv('files/_BRIGADE.csv', sep=',', encoding='utf-8')
    df[df['_type'] == 'ORDER'].to_csv('files/_ORDER.csv', sep=',', encoding='utf-8')
    df[df['_type'] == 'MATERIAL'].to_csv('files/_MATERIAL.csv', sep=',', encoding='utf-8')

    print(import_from_csv())

    return 'True'


@app.route('/')
def start_page():
    return render_template('main_page.html')


@app.route('/employees')
def get_employees():
    employees = Employee.nodes.all()
    return render_template('employees.html', employees=employees)


@app.route('/employees/create', methods=['GET', 'POST'])
def create_employee():
    form = CreateEmployee()
    if form.validate_on_submit():
        brigade = Brigade.nodes.get_or_none(number=str(form.brigade.data))
        if brigade is None:
            brigade = Brigade(number=str(form.brigade.data))
            brigade.save()
        empl = Employee(name=form.name.data, birth_date=form.birth_date.data,
                        passport=form.passport.data, position=form.position.data)
        empl.save()
        empl.brigade.connect(brigade)
        flash('Сотрудник добавлен')
        return redirect(url_for('create_employee'))
    brigades = Brigade.nodes.all()
    form.brigade.choices = [x.number for x in brigades]
    return render_template('create_employee.html', form=form)


@app.route('/orders')
def get_orders():
    orders = Order.nodes.all()
    return render_template('orders.html', orders=orders)


@app.route('/orders/create', methods=['GET', 'POST'])
def create_order():
    form = CreateOrder()
    if request.method == 'POST':
        if form.validate_on_submit():
            br = Brigade.nodes.get(number=form.brigade.data)
            order = Order(cost=form.cost.data, number=str(form.number.data), is_done=False)
            order.save()
            order.brigade.connect(br)
            for m in form.material:
                material = Material.nodes.get(name=m.material.data)
                rel = order.material.connect(material)
                rel.count = m.count.data
                rel.save()
            flash('Заказ добавлен')
            return redirect(url_for('create_order'))
    brigades = Brigade.nodes.all()
    form.brigade.choices = [x.number for x in brigades]
    return render_template('create_order.html', form=form)


@csrf.exempt
@app.route('/orders/set_done', methods=['POST'])
def set_done():
    data = request.get_json(True)
    order = Order.get_order_by_id(int(data['order_id']))
    order.is_done = data['is_done']
    order.save()

    return 'True'


@app.route('/stats')
def get_stats():
    x_brigades, y_done_orders = Brigade.get_done_orders()

    num_of_not_done_orders, num_of_done_orders = Order.get_num_of_done_orders()

    return render_template('stats.html',
                           done_orders_for_brigades=get_done_orders_for_every_brigade(x_brigades, y_done_orders),
                           num_of_done_orders=get_pie(num_of_not_done_orders, num_of_done_orders))


if __name__ == '__main__':
    threading.Timer(3, import_from_csv, args=['http://0.0.0.0:5000/preload']).start()
    app.run(host='0.0.0.0', port='5000')
