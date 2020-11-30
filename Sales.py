import pandas as pd
import sqlite3
import datetime
import random

class Sales(object):
    """
    Класс работы с продажами
    """
    _db_filename = r'C:\Python_projects\SalesStat\Data\Sales.db'

    def __init__(self):
        """
        Инициирование класса продаж
        """
        self.db_connection = sqlite3.connect(self._db_filename)  # соединяемся с бд
        self.db_cursor = self.db_connection.cursor()

    def sales_from_date_to_date(self, date_begin, date_end):
        """
        Продажи в определённый период времени
        :return: набор данных по продажам за указанный период
        """
        command = """
            SELECT DateOfTransaction, COUNT(*) as count FROM transactions
            WHERE DateOfTransaction BETWEEN ? AND ?
            GROUP BY DateOfTransaction
            ORDER BY DateOfTransaction;
            """

        return pd.DataFrame(self.db_cursor.execute(command,
                                                   (str(date_begin.format('%Y-%m-%d')),
                                                    str(date_end.format('%Y-%m-%d')))).fetchall(),
                            columns=['Date', 'SalesCount'])

    def median_check(self):
        """
        Медиана чеков
        :return: сумма среднего чека
        """
        command = """
            SELECT * FROM transactions
            ORDER BY Total;
        """
        df_tmp = pd.DataFrame(self.db_cursor.execute(command).fetchall(),
                              columns=['Index', 'CheckID', 'BuyerID', 'ProductID', 'ProductsCount',
                                        'Total', 'DateOfTransaction'])
        # находим медиану:
        med = float(df_tmp['Total'].median())
        return med

    def most_popular_category(self, categories_count):
        """
        Самая популярная категория товаров
        :param categories_count: число результатов на выходе
        :return:
        """
        command = """
            SELECT products.Category as Category,
                    SUM(transactions.ProductsCount) as Bought
            FROM products, transactions
            WHERE transactions.ProductID = products.ProductID
            GROUP BY products.Category
            ORDER BY Bought DESC
            LIMIT """ + categories_count + ";"

        return pd.DataFrame(self.db_cursor.execute(command).fetchall(),
                            columns=['Category', 'Bought'])

    def most_popular_category_by_year(self, category):
        """
        Самые популярные категории, сгруппированные по годам
        :return:
        """
        command = """
                    SELECT products.Category as Category,
                            strftime('%Y', transactions.DateOfTransaction) as Year,                            
                            SUM(transactions.ProductsCount) as Bought                            
                    FROM products, transactions
                    WHERE transactions.ProductID = products.ProductID
                    AND products.Category = '""" + \
                    category + \
                    """'
                    GROUP BY Year
                    ORDER BY Year;"""

        return pd.DataFrame(self.db_cursor.execute(command).fetchall(),
                            columns=['Category','Year','Bought'])

    def insert_transaction(self):
        """
        вставить транзакцию в таблицу
        :param buyer_id: идентификатор покупателя
        :param product_id: идентификатор товара
        :param products_count: кол-во товара
        :param date_of_transaction: дата совершения транзакции
        :return:
        """
        date_buying = str(datetime.date(day=random.randint(1, 30),
                                    month=random.randint(3, 12),
                                    year=random.randint(2018, 2020)))

        command = """
            SELECT BuyerID
            FROM buyers;
        """
        df_buyers = pd.DataFrame(self.db_cursor.execute(command).fetchall(),
                            columns=['BuyerID'])

        command = """
                    SELECT ProductID
                    FROM products;
                """
        df_products= pd.DataFrame(self.db_cursor.execute(command).fetchall(),
                                 columns=['ProductID'])

        b_id = random.choice(df_buyers['BuyerID'])  # id покупателя
        p_id = random.choice(df_products['ProductID'])  # id товара

        command = """
                            SELECT Price
                            FROM products
                            WHERE ProductID = '""" + p_id + """';"""
        price = float(self.db_cursor.execute(command).fetchall()[0][0])

        products_in_backet = random.randint(1, 25)  # кол-во товаров в корзине покупателя
        total = price * products_in_backet
        tr_id = 'TR' + str(random.randint(1, 6_000_000))  # id транзакции
        ch_id = 'CH' + str(random.randint(1, 6_000_000))  # id транзакции

        command = """INSERT INTO transactions
            VALUES(?,?,?,?,?,?,?)
        """
        self.db_cursor.execute(command,
                               [
                                   tr_id,
                                   ch_id,
                                   b_id,
                                   p_id,
                                   products_in_backet,
                                   total,
                                   date_buying
                               ])

        self.db_connection.commit()

        print('Транзакция в БД добавлена: ', [
                                   tr_id,
                                   ch_id,
                                   b_id,
                                   p_id,
                                   products_in_backet,
                                   total,
                                   date_buying
                               ])

    def max_check(self):
        """
        Максимальный чек
        :return: сумма максимального чека
        """
        command = """
        SELECT MAX(Total) as max_check
        FROM transactions;
        """
        return float(self.db_cursor.execute(command).fetchall()[0][0])

    def min_check(self):
        """
        Минимальный чек
        :return: сумма минимального чека
        """
        command = """
                SELECT MIN(Total) as min_check
                FROM transactions;
                """
        return float(self.db_cursor.execute(command).fetchall()[0][0])

    def sales_by_days_of_week(self):
        """
        Кол-во продаж по дням недели
        :return:
        """
        command = """
            SELECT strftime('%w', DateOfTransaction) as DayOfWeek,
                    AVG(Total) as AverageInDay
            FROM transactions
            GROUP BY DayOfWeek;
        """

        return pd.DataFrame(self.db_cursor.execute(command).fetchall(), columns=['DayOfWeek', 'AverageInDay'])

    def sales_by_months(self):
        """
        Среднее количество продаж по месяцам
        :return:
        """
        command = """
                    SELECT strftime('%m', DateOfTransaction) as Month,
                            AVG(Total) as AverageInMonth
                    FROM transactions
                    GROUP BY Month;
                """

        return pd.DataFrame(self.db_cursor.execute(command).fetchall(), columns=['Month', 'AverageInMonth'])

    def get_random_buyer(self):
        """
        Получить случайного покупателя в виде словаря данных
        :return:
        """
        command = """
        SELECT BuyerID FROM buyers
        """
        df_buyers = pd.DataFrame(self.db_cursor.execute(command).fetchall(),
                                 columns=['BuyerID'])

        buyer_rnd_id = random.choice(df_buyers['BuyerID'])

        command = """
            SELECT * FROM buyers
            WHERE BuyerID = '""" + buyer_rnd_id + "';"

        result = self.db_cursor.execute(command).fetchall()

        buyer = {'BuyerName' : result[0][0],
                 'BuyerID' : result[0][1],
                 'Birthday' : result[0][2]}

        return buyer

    def most_popular_products_of_buyer(self, buyer_id, quantity):
        """
            Самые популярные товары покупателя
        :param self:
        :param buyer_id:
        :return:
        """
        command = """
            SELECT products.Title as product,
                SUM(transactions.ProductsCount) as popularity
            FROM transactions, products
            WHERE products.ProductID = transactions.ProductID AND
                  transactions.BuyerID = '""" + buyer_id + """'
            GROUP BY product
            ORDER BY popularity DESC
            LIMIT """ + str(quantity) + """;
        """

        return pd.DataFrame(self.db_cursor.execute(command).fetchall(),
                            columns=['Product', 'Popularity'])