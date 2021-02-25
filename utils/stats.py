import matplotlib.pyplot as plt
from scipy import interpolate
import numpy as np
from io import BytesIO
import base64


def image_from_plt(fig):
    tmpfile = BytesIO()
    fig.savefig(tmpfile, format='png', transparent=True)
    encoded = base64.b64encode(tmpfile.getvalue()).decode('utf-8')
    return "data:image/png;base64," + encoded


def get_pie(orders, done_orders):
    plt.clf()

    labels = 'Заказы', 'Зав. заказы'
    sizes = [orders, done_orders]
    explode = (0, 0.4)  # only "explode" the 2nd slice (i.e. 'Hogs')

    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    return image_from_plt(fig1)


def get_done_orders_for_every_brigade(x, y):
    y = np.array(y)

    fig, ax = plt.subplots()
    ax.bar(x, y, width=0.7, label='Количество завершенных заказов')
    ax.legend(prop={'size': 20})

    ax.set_facecolor('seashell')
    fig.set_figwidth(12)  # ширина Figure
    fig.set_figheight(6)  # высота Figure
    fig.set_facecolor('floralwhite')

    return image_from_plt(fig)