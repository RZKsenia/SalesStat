import pandas as pd
from bokeh.document import document
from bokeh.models import CustomJS, Div
from bokeh.plotting import figure, output_file, show, ColumnDataSource
from bokeh.layouts import gridplot
from bokeh.models.widgets import Tabs, Panel, DataTable, DateFormatter, TableColumn
from Scripts.Sales import Sales
import datetime
from bokeh.models import HoverTool
import numpy as np

class GUI(object):
    """
    Интерфейс приложения
    """
    # основные цвета интерфейса:
    colors = {
        'white' : '#f9feff',
        'light-gray' : '#e9e7db',
        'yellow' : '#eae100',
        'olive' : '#6f7408',
        'light-brown' : '#977035',
        'dark-brown' : '#362917'
    }
    sale = Sales()
    df_day_by_day = pd.DataFrame()

    def __init__(self):
        #for i in range(0, 1500):
        #    self.sale.insert_transaction()

        document.title = 'Аналитика продаж'
        # сразу показываем аналитику за 7 дней:
        tdelta = datetime.timedelta(days=7)
        self.date_begin = (datetime.datetime.now() - tdelta).strftime('%Y-%m-%d')
        self.date_end = datetime.datetime.now().strftime('%Y-%m-%d')

        self.analyst_for_seven_days() # подводим аналитику за 7 дней

        # Высплывающая подсказка:
        tooltips_seven_days = [
            ('Продаж совершено', '@SalesCount')
        ]

        plot_title_seven_days = 'Продажи за период с ' + self.date_begin + ' по ' + self.date_end
        # диаграмма продаж за недельный период:
        p_seven_days = self.build_bokeh_vbar(
            data_frame=self.df_day_by_day,
            plot_width=600,
            plot_height=400,
            plot_title=plot_title_seven_days,
            x_range=self.df_day_by_day['Date'],
            x_label_orientation=0,
            y_label_orientation=0,
            x_axis_title='Дата',
            y_axis_title='Кол-во продаж',
            tooltips=tooltips_seven_days,
            x_value_source='Date',
            y_value_source='SalesCount'
        )

        self.median_check = self.sale.median_check() # медиана чеков
        self.min_check = self.sale.min_check() # минимальный чек
        self.max_check = self.sale.max_check() # максимальный чек
        # Информационный блок:
        div_info = Div(text='<div style= "font-size: 15px; color:' + str(self.colors['olive']) +
                            '"><ul><li><b>Медиана чеков: </b><i>' +
                            str(self.median_check).format('%.2f') +
                            " руб.</i><li><b>Минимальный чек: </b><i>" + str(self.min_check).format('%.2f') +
                            ' руб. </i><li><b>Максимальный чек: </b><i>' + str(self.max_check).format('%.2f') +
                       " руб. </i></ul><div>")

        # наиболее популярные категории товаров:
        # self.df_most_popular = self.sale.most_popular_category(categories_count=10)

        plot_title_popular = 'Популярность категорий товаров'

        p_most_popular, str_info = self.line_chart_caterogies(
            plot_height=400,
            plot_width=600,
            plot_title='Популярность категорий товаров',
            x_axis_title= 'Год',
            y_axis_title= 'Кол-во продаж',
            x_label_orientation=0,
            y_label_orientation=0
        )

        # Информационный блок:
        div_info2 = Div(text='<div style= "font-size: 15px; color:' + str(self.colors['olive']) +
                            '"><h4>Категории, популярность которых снизилась за последний год: </h4>' +
                             str_info +
                             "<div>")

        rnd_buyer = self.sale.get_random_buyer() # получаем случайного покупателя
        # Блок информации о покупателе:
        div_text = '<div style= "font-size: 15px;"><h3>Информация о покупателе</h3>' \
                   '<ul><li><b>Buyer ID: </b>' + rnd_buyer['BuyerID'] + \
                    "<li><b>Имя покупателя: </b>" + rnd_buyer['BuyerName'] + \
                    "<li><b>День Рождения: </b>" + rnd_buyer['Birthday'] + '</ul>'

        # получаем информацию о самых популярных товарах покупателя:
        df_most_popular_products_of_buyer = self.sale.most_popular_products_of_buyer(buyer_id=rnd_buyer['BuyerID'],
                                                                                     quantity=20)

        source = ColumnDataSource(df_most_popular_products_of_buyer)
        columns = [
            TableColumn(field="Product", title="Наименование товара"),
            TableColumn(field="Popularity", title="Куплено ед. товара"),
        ]
        div_popularity_info = DataTable(source=source, columns=columns, width=500, height=300)
        div_buyer_info = Div(text=div_text)
        div_buyer_popular_products_title = Div(text='<h3>Самые популярные товары покупателя:')

        # собираем в сетку элементы управления и графики:
        gp = gridplot(children=[[p_seven_days, p_most_popular, div_info2], [div_info]])
        gp_b = gridplot(children=[[div_buyer_info], [div_buyer_popular_products_title], [div_popularity_info]])
        # панели для отображения информации:
        sales_week_panel = Panel(child=gp, title='Аналитика продаж')
        buyers_panel = Panel(child=gp_b, title='Покупатели')
        # вкладки:
        tabs = Tabs(tabs=[sales_week_panel, buyers_panel])

        show(tabs)

    def analyst_for_seven_days(self):
        # получаем аналитику по кол-ву продаж за последнюю неделю:
        self.df_day_by_day = self.sale.sales_from_date_to_date(
            date_begin=str(self.date_begin),
            date_end=str(self.date_end))

    def build_bokeh_hbar(self, y_values, x_values, bar_height, plot_width, plot_height, plot_title,
                         tooltips, data_frame, x_axis_title, y_axis_title, x_label_orientation,
                         y_label_orientation):
        """
        Горизонтальная столбчатая диаграмма

        :return: диаграмма
        """
        source_for_tooltips = ColumnDataSource(data=data_frame)

        p = figure(
            y_range=y_values,
            x_range=x_values,
            plot_width=plot_width,
            plot_height=plot_height,
            title=plot_title,
            background_fill_color=self.colors['white'],
            tools="hover",
            tooltips=tooltips
        )

        p.title.text_font_size = '20px'
        p.title.text_color = self.colors['dark-brown']

        p.hbar(y='Category',
               right='Bought',
               height=bar_height,
               color=self.colors['yellow'],
               source=source_for_tooltips)

        p.xaxis.axis_label = x_axis_title
        p.xaxis.major_label_orientation = x_label_orientation
        p.xgrid.grid_line_color = self.colors['light-gray']
        p.ygrid.grid_line_color = self.colors['light-gray']
        p.yaxis.axis_label = y_axis_title
        p.yaxis.major_label_text_color = self.colors['dark-brown']
        p.yaxis.major_label_orientation = y_label_orientation

        return p


    def build_bokeh_vbar(self, data_frame, plot_width, plot_height, plot_title, x_range,
                         x_label_orientation, y_label_orientation, x_axis_title, y_axis_title,
                         tooltips, x_value_source, y_value_source):
        """
        Построить столбчатую вертикальную диаграмму
        :param data_frame: набор данных pandas.DataFrame
        :param plot_width: ширина диаграммы
        :param plot_height: высота диаграммы
        :param plot_title: заголовок диаграммы
        :param x_range: источник данных для оси Х
        :param x_label_orientation: угол поворота подписей на оси Х
        :param y_label_orientation: угол поворота подписей на оси У
        :param x_axis_title: подпись для оси Х
        :param y_axis_title: подпись для оси У
        :param tooltips: список кортежей для всплывающих подсказок
        :param x_value_source: строка, название столбца данных, которые послужат для оси Х
        :param y_value_source: строка, название столбца данных, которые послужат для оси У
        :return: фигура figure bokeh
        """
        # Из источника данных будет взята информация и для графика,
        # и для подсказок:
        source_for_tooltips = ColumnDataSource(data=data_frame)

        p = figure(
            x_range=x_range,
            plot_width=plot_width,
            plot_height=plot_height,
            title=plot_title,
            tooltips=tooltips
        )
        p.title.text_font_size = '20px'
        p.title.text_color = self.colors['dark-brown']

        p.vbar(
            x=x_value_source,
            top=y_value_source,
            width=0.5,
            color=self.colors['yellow'],
            source= source_for_tooltips
        )

        p.xaxis.axis_label = x_axis_title
        p.xaxis.major_label_orientation = x_label_orientation
        p.xgrid.grid_line_color = self.colors['light-gray']
        p.ygrid.grid_line_color = self.colors['light-gray']
        p.yaxis.axis_label = y_axis_title
        p.yaxis.major_label_text_color = self.colors['dark-brown']
        p.yaxis.major_label_orientation = y_label_orientation

        return p

    def buble_char(self, x_values, y_values, sizes, plot_width, plot_height):
        """
        Построение пузырьковой диаграммы
        :param x_values: значения для оси Х (категории)
        :param y_values: значения для оси Х (можно использовать номера категорий)
        :param sizes: диаметры окружностей
        :return:
        """
        p = figure(plot_width=plot_width,
                   plot_height=plot_height)

        p.circle(x= y_values,
                 y= y_values,
                 size=sizes,
                 color=self.colors['olive'],
                 alpha=0.5)
        return p

    def line_chart_caterogies(self, plot_width, plot_height, plot_title, x_axis_title, y_axis_title,
                              x_label_orientation, y_label_orientation):
        """
        линейный график для множества линий
        :return:
        """
        # для хранения пар Категория : Процент снижания продаж за год
        df_changes = pd.DataFrame(columns=['Category', 'Changed'])
        ch_cntr = 0
        data_frame = self.sale.most_popular_category(str(10)) # получаем самые популярные категории

        tooltips_popular = [
            ('Категория', '@category'),
            ('Год', '@year'),
            ('Ед. товара продано', '@bought')
        ]

        p = figure(
            plot_width=plot_width,
            plot_height=plot_height,
            title=plot_title,
            tooltips= tooltips_popular
        )

        for c in data_frame['Category'].to_list():
            # проходим по всем уникальным категориям
            df = self.sale.most_popular_category_by_year(str(c))
            x_list = df['Year'].to_list()
            y_list = df['Bought'].to_list()

            source_for_tooltips = ColumnDataSource(data=dict(
                year=x_list,
                bought=y_list,
                category=[c for i in range(0, len(x_list))]
            ))

            # Проверяем - не упала ли популярность категорий:
            if y_list[-2] > y_list[-1]:
                y1 = y_list[-2]
                y2 = y_list[-1]
                tmp_result = y1 / y2
                tmp_result = tmp_result - int(tmp_result)
                tmp_result *= 100
                # заносим процент снижения продаж в словарь:
                df_changes.at[ch_cntr, 'Category'] = str(c)
                df_changes.at[ch_cntr, 'Changed'] = float(tmp_result)
                ch_cntr += 1
                clr = 'olive'
            else:
                clr = 'yellow'

            p.line(
                'year',
                'bought',
                color=self.colors[clr],
                line_width=2,
                source=source_for_tooltips
            )

            p.dot(
                'year',
                'bought',
                size= 25,
                color=self.colors[clr],
                line_width=2,
                source=source_for_tooltips
            )

        p.title.text_font_size = '20px'
        p.title.text_color = self.colors['dark-brown']
        p.xaxis.axis_label = x_axis_title
        p.yaxis.axis_label = y_axis_title
        p.xaxis.major_label_orientation = x_label_orientation
        p.xgrid.grid_line_color = self.colors['light-gray']
        p.ygrid.grid_line_color = self.colors['light-gray']
        p.yaxis.major_label_text_color = self.colors['dark-brown']
        p.yaxis.major_label_orientation = y_label_orientation

        str_info = '<ul>'
        df_changes = df_changes.sort_values(by='Changed', ascending= False) # сортируем по столбцу процентов
        indexes = df_changes.index

        for ch_cntr in indexes:
            str_info += '<li>' + df_changes.at[ch_cntr, 'Category'] + \
                        ' ' + str('%.2f' % df_changes.at[ch_cntr, 'Changed'])+ r' %'

        if str_info == '<ul>':
            str_info = 'Список пуст.'

        return p, str_info

g = GUI()