import sqlite3

con = sqlite3.connect('coins.db')


def insert_db(table, data):
    with con:
        cur = con.cursor()

        sql = "insert into {0}(ticker, target) values(?,?)".format(table)
        cur.execute(sql, data)

        con.commit()


def select_all_db(table):
    with con:
        cur = con.cursor()

        sql = "select * from {0}".format(table)
        cur.execute(sql)
        rows = cur.fetchall()
        for row in rows:
            print(row)


def delete_db(table, ticker):
    with con:
        cur = con.cursor()

        sql = "delete from {0} where ticker = ?".format(table)
        cur.execute(sql, (ticker,))

        con.commit()


def delete_all_db(table):
    with con:
        cur = con.cursor()

        sql = "delete from {0}".format(table)
        cur.execute(sql).rowcount

        con.commit()


def update_target_db(ticker, target):
    with con:
        cur = con.cursor()

        sql = "update target_table set target = ? where ticker = ?"
        cur.execute(sql, (target, ticker))

        con.commit()


delete_all_db('target_table')


