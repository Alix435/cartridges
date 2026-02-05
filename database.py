import sqlite3
from config import db_path

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()


    def _create_tables(self):
        self.conn.execute(
            '''
            CREATE TABLE IF NOT EXISTS cartridges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_code TEXT,
            color_name TEXT NOT NULL CHECK(color_name IN ('black', 'cyan', 'magenta', 'yellow')),
            quantity INTEGER DEFAULT NULL,
            printer_model TEXT NOT NULL,
            UNIQUE(printer_model, color_name)  -- ← КЛЮЧЕВОЕ: запрет дублей по модели+цвету
    )
            ''')

    def read_tab_cart(self):
        cur = self.conn.execute('SELECT * FROM cartridges')
        return cur.fetchall()

    def add_data(self, cartridge_data):
        with self.conn:
            self.conn.execute("""
                INSERT INTO cartridges (model_code, color_name, printer_model)
                VALUES (?, ?, ?)
            """, (
                cartridge_data['model_code'],
                cartridge_data['color_name'],
                cartridge_data['printer_model']
            ))
        self.conn.commit()

    def update_cartridges(self, id_cartridge, data):
        self.conn.execute('''
            UPDATE cartridges
            SET quantity = ?
            WHERE id = ?
        ''', (data['quantity'], id_cartridge))
        self.conn.commit()

    def close(self):
        self.conn.close()
