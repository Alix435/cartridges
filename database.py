import sqlite3
import pandas
import config


class Database:
    def __init__(self):
        self.conn = sqlite3.connect(config.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()


    def _create_tables(self):
        self.conn.execute(
            '''
            CREATE TABLE IF NOT EXISTS cartridges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_code TEXT,
            color_name TEXT NOT NULL CHECK(color_name IN ('black', 'cyan', 'magenta', 'yellow')),
            quantity INTEGER DEFAULT 0,
            printer_model TEXT NOT NULL,
            UNIQUE(printer_model, color_name)  -- ← КЛЮЧЕВОЕ: запрет дублей по модели+цвету
    )
            ''')

    def read_tab_cart(self):
        data_cartridges = []
        cur = self.conn.execute('SELECT * FROM cartridges')
        rows = cur.fetchall()
        for row in rows:
            tmp = {
                'id': row['id'],
                'model_code': row['model_code'],
                'color_name': row['color_name'],
                'quantity': row['quantity'],
                'printer_model': row['printer_model']
            }
            data_cartridges.append(tmp)

        return data_cartridges

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
        # Формируем SET часть динамически
        fields = []
        values = []
        for key, value in data.items():
            if key in ('model_code', 'color_name', 'quantity'):  # разрешённые поля
                fields.append(f"{key} = ?")
                values.append(value)

        if not fields:
            return  # нечего обновлять

        values.append(id_cartridge)
        query = f"UPDATE cartridges SET {', '.join(fields)} WHERE id = ?"
        self.conn.execute(query, values)
        self.conn.commit()

    def export_cartridges_data(self):
        query = 'SELECT * FROM cartridges'
        data = pandas.read_sql(query, f'sqlite:///{config.db_path}')

        data.to_excel(config.export_file, index=False, sheet_name='Cartridges')
        print('Done!')

    def close(self):
        self.conn.close()

