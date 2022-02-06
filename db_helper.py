import sqlite3

con = sqlite3.connect('coins.db')
con.row_factory = sqlite3.Row


def insert_position_db(data):
    try:
        with con:
            cur = con.cursor()

            sql = "insert into position_table(ticker, order_type, order_time, order_price, volume) values(?, ?, ?, ?, ?)"
            cur.execute(sql, data)

            con.commit()
    except Exception as e:
        print("insert_position_db", e)


def insert_target_db(data):
    try:
        with con:
            cur = con.cursor()

            sql = "insert into target_table(ticker, target, op_mode) values(?,?)"
            cur.execute(sql, data)

            con.commit()
    except Exception as e:
        print("insert_db", e)


def select_db(table, ticker):
    try:
        with con:
            cur = con.cursor()

            sql = "select * from {0} where ticker = ?".format(table)
            cur.execute(sql, (ticker,))
            row = cur.fetchone()

            return dict(row)
    except Exception as e:
        print("select_db", e)


def select_all_db(table, ticker):
    try:
        with con:
            cur = con.cursor()

            sql = "select * from {0} where ticker = ?".format(table)
            cur.execute(sql, (ticker,))
            rows = cur.fetchall()

            result = []
            for row in rows:
                result.append(dict(row))

            return result
    except Exception as e:
        print("select_all_db", e)


def delete_db(table, ticker):
    try:
        with con:
            cur = con.cursor()

            sql = "delete from {0} where ticker = ?".format(table)
            cur.execute(sql, (ticker,))

            con.commit()
    except Exception as e:
        print("delete_db", e)


def delete_all_db(table):
    try:
        with con:
            cur = con.cursor()

            sql = "delete from {0}".format(table)
            cur.execute(sql).rowcount

            con.commit()
    except Exception as e:
        print('delete_all_db', e)


def update_target_db(ticker, target, op_mode):
    try:
        with con:
            cur = con.cursor()

            sql = "update target_table set target = ?, op_mode =? where ticker = ?, op_mode = 0"
            cur.execute(sql, (target, op_mode, ticker))

            con.commit()
    except Exception as e:
        print("update_target_db", e)
