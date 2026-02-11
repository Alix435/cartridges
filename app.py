from flask import Flask, render_template, request, redirect, url_for, flash
from collections import defaultdict
from database import Database 

app = Flask(__name__)
app.secret_key = 'super-secret-key-for-cartridges-app-2026'
db = Database()

@app.route('/', methods=['GET', 'POST'])
def cartridges_page():
    if request.method == 'POST':
        return handle_cartridge_update()

    raw_data = db.read_tab_cart()
    grouped = defaultdict(list)
    for item in raw_data:  # ← ИСПРАВЛЕНО
        grouped[item['printer_model']].append(item)
    return render_template('cartridges.html', grouped_cartridges=dict(grouped))

def handle_cartridge_update():
    # try:
    cartridge_id = int(request.form['id'])
    current_qty = get_current_quantity(cartridge_id)
    if current_qty is None:
        flash("Картридж не найден", "error")
        return redirect(url_for('cartridges_page'))

    action = request.form.get('action')

    if action == 'decrement':
        new_qty = current_qty - 1
        if new_qty < 0:
            flash("Остаток не может быть отрицательным", "warning")
            return redirect(url_for('cartridges_page'))

    else:
        # Этот блок — для других операций (например, из формы редактирования)
        # Но в текущей форме его нет → лучше его убрать или защитить
        amount = int(request.form['amount'])  # ← теперь точно будет ошибка, если нет 'amount'
        mode = request.form.get('mode', 'add')
        if mode == 'add':
            new_qty = current_qty + amount
        elif mode == 'set':
            if amount < 0:
                flash("Количество не может быть отрицательным", "error")
                return redirect(url_for('cartridges_page'))
            new_qty = amount
        else:
            flash("Неверный режим", "error")
            return redirect(url_for('cartridges_page'))

    db.update_cartridges(cartridge_id, {'quantity': new_qty})
    flash("Количество обновлено", "success")

    return redirect(url_for('cartridges_page'))

def get_current_quantity(cartridge_id):
    data = db.read_tab_cart()
    for item in data:  # ← ИСПРАВЛЕНО
        if item['id'] == cartridge_id:
            return item['quantity']
    return None

@app.route('/export')
def export():
    db.export_cartridges_data()
    flash("Экспорт в Excel выполнен", "success")
    return redirect(url_for('cartridges_page'))

@app.route('/edit_cartridge/<int:cartridge_id>', methods=['GET', 'POST'])
def edit_cartridge(cartridge_id):
    # Получаем данные картриджа
    cartridges = db.read_tab_cart()
    cartridge = None
    for c in cartridges:
        if c['id'] == cartridge_id:
            cartridge = c
            break

    if not cartridge:
        flash("Картридж не найден", "error")
        return redirect(url_for('cartridges_page'))

    if request.method == 'POST':
        try:
            model_code = request.form['model_code'].strip()
            color_name = request.form['color_name']
            quantity = int(request.form['quantity'])

            if quantity < 0:
                flash("Количество не может быть отрицательным", "error")
                return render_template('edit_cartridge.html', cartridge=cartridge)

            # Обновляем в БД
            db.update_cartridges(cartridge_id, {
                'model_code': model_code,
                'color_name': color_name,
                'quantity': quantity
            })
            flash("Данные сохранены", "success")
            return redirect(url_for('cartridges_page'))

        except ValueError:
            flash("Некорректное количество", "error")
        except Exception as e:
            flash(f"Ошибка: {e}", "error")

    return render_template('edit_cartridge.html', cartridge=cartridge)

if __name__ == '__main__':
    try:
        app.run(debug=True, host='127.0.0.1', port=5000)
        # app.run(host='0.0.0.0', port=8000)
    finally:
        db.close()
