import os
import time
from flask import Flask, redirect, render_template, request, url_for
import psycopg2

app = Flask(__name__)


def get_db_connection():
  while True:
    try:
      conn = psycopg2.connect(
          host=os.environ.get('DB_HOST', 'db'),
          database=os.environ.get('DB_NAME', 'cloudshop'),
          user=os.environ.get('DB_USER', 'clouduser'),
          password=os.environ.get('DB_PASSWORD', 'cloudpassword'),
      )
      return conn
    except psycopg2.OperationalError:
      print('База данных пока недоступна, ожидание...')
      time.sleep(2)


def init_db():
  conn = get_db_connection()
  cur = conn.cursor()
  cur.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            price NUMERIC NOT NULL
        );
    ''')
  cur.execute('SELECT COUNT(*) FROM products;')
  count = cur.fetchone()[0]
  if count == 0:
    sample_products = [
        ('Laptop Lenovo', 750000),
        ('Mouse Logitech', 25000),
        ('Keyboard Logitech', 45000),
        ('Monitor Samsung', 180000),
        ('SSD 1TB', 70000),
    ]
    cur.executemany(
        'INSERT INTO products (name, price) VALUES (%s, %s);', sample_products
    )
    conn.commit()
  cur.close()
  conn.close()


@app.route('/')
def index():
  conn = get_db_connection()
  cur = conn.cursor()
  cur.execute('SELECT id, name, price FROM products ORDER BY id;')
  products = cur.fetchall()
  cur.close()
  conn.close()
  return render_template('index.html', products=products)


@app.route('/add', methods=['GET', 'POST'])
def add_product():
  if request.method == 'POST':
    name = request.form['name']
    price = request.form['price']

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO products (name, price) VALUES (%s, %s);', (name, price)
    )
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('index'))

  return render_template('add.html')


@app.route('/about.html')
def about():
  return render_template('about.html')


@app.route('/contacts.html')
def contacts():
  return render_template('contacts.html')


@app.route('/author.html')
def author():
  return render_template('author.html')


if __name__ == '__main__':
  init_db()
  app.run(host='0.0.0.0', port=5000)