import config
from database import Database

db = Database()

def data_add(items):
    for item in items:
        db.add_data(item)

def read_file_txt():
    tmp = []
    with open(config.file_data, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip(',')
            if not line:
                continue
            parts = [part.strip() for part in line.split(',', 2)]
            if len(parts) != 3:
                continue

            model_code, color_name, printer_model = parts
            tmp.append({'model_code': str(model_code), 'color_name': color_name, 'printer_model': printer_model})
    return tmp

def command_center():
    data = read_file_txt()
    data_add(data)

    tmp = db.read_tab_cart()
    for items in tmp:
        for item in items:
            print(item)
        print()

if __name__ == '__main__':
    command_center()
