import sqlite3
from astra.exceptions import QuoteAddError

def _connect():
    con = sqlite3.connect('data/astra.db')
    cur = con.cursor()
    return con, cur

class AstraDBConnection:

    @staticmethod
    def initialize():
        con, cur = _connect()
        cur.execute(
            """CREATE TABLE IF NOT EXISTS quotes(
                id INTEGER PRIMARY KEY,
                user INTEGER NOT NULL,
                msg TEXT NOT NULL
            )"""
        )
        cur.execute(
            """CREATE TABLE IF NOT EXISTS jar(
                user INTEGER NOT NULL,
                swears INTEGER NOT NULL
            )
            """
        )
        con.commit()
        con.close()
    
    @staticmethod
    def add_quote(user: int, msg: str):
        con, cur = _connect()
        cur.execute('insert into quotes values(NULL, ?, ?)', (user, msg))
        con.commit()
        new_id = cur.execute('SELECT id FROM quotes WHERE user = ? AND msg = ?', (user, msg)).fetchall()
        if len(new_id) == 0:
            raise QuoteAddError
        con.close()
        return new_id[0][0]
        
    @staticmethod
    def search_quote(fromUser: int, withMsg: str):
        con, cur = _connect()
        res = cur.execute('select id from quotes where user = ? and msg = ?', (fromUser, withMsg)).fetchall()
        con.close()
        return res
    
    @staticmethod
    def read_quotes(fromUser: int):
        con, cur = _connect()
        res = cur.execute('select msg, id from quotes where user=? order by id desc', (fromUser,)).fetchall()
        con.close()
        return res
    
    @staticmethod
    def delete_quote(withId: int):
        con, cur = _connect()
        cur.execute('delete from quotes where id = ?', (withId,))
        con.commit()
        con.close()
        
    @staticmethod
    def query_all():
        con, cur = _connect()
        res = cur.execute('select msg from quotes').fetchall()
        con.close()
        return [v[0] for v in res]
    
    @staticmethod
    def get_jar(forUser: int):
        con, cur = _connect()
        res = cur.execute('SELECT swears FROM jar WHERE user=?', (forUser,)).fetchall()
        con.close()
        if len(res) == 0:
            return 0
        else:
            return res[0][0]
        
    @staticmethod
    def incr_jar(*, forUser: int, byAmount: int=1):
        con, cur = _connect()
        current_swears = cur.execute('SELECT swears FROM jar WHERE user=?', (forUser,)).fetchall()
        if len(current_swears) == 0:
            cur.execute('INSERT INTO jar VALUES(?, ?)', (forUser, byAmount))
        else:
            cur.execute('UPDATE jar SET swears=? WHERE user=?', (current_swears[0][0]+byAmount,forUser))
        con.commit()
        con.close()
        
    @staticmethod
    def query_leaderboard(forUsers: list[int]):
        con, cur = _connect()
        q = ', '.join(['?']*len(forUsers))
        query = f"""
        SELECT *
        FROM jar
        WHERE user IN ({q})
        ORDER BY swears DESC
        LIMIT 20"""
        list = cur.execute(query, forUsers).fetchall()
        con.close()
        return list