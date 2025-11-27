from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit():
    user_name = request.form.get('username', '').strip()
    print(f"=== FLASK DEBUG: Получено имя '{user_name}' ===")

    if user_name:
        print(f"Перенаправляем на /result с name={user_name}")
        return redirect(url_for('result', name=user_name))
    else:
        print("Пустое имя, возвращаем на главную")
        return redirect(url_for('index'))


@app.route('/result')
def result():
    name = request.args.get('name', 'Гость')
    print(f"=== FLASK DEBUG: Отображаем result.html с name='{name}' ===")
    return render_template('result.html', name=name)


@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)