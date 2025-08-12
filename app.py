import sqlite3
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for

app1 = Flask(__name__)

# Load data from Excel
def load_data_from_excel():
    df = pd.read_excel('customer.xlsx', usecols=['customer_name', 'address', 'packages', 'network_connections', 'prior_booking'])
    return df

def init_db():
    schema = '''
    DROP TABLE IF EXISTS customer;
    CREATE TABLE IF NOT EXISTS customer (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name TEXT NOT NULL,
        address TEXT NOT NULL,
        packages INTEGER NOT NULL,
        network_connections TEXT NOT NULL,
        prior_booking TEXT NOT NULL
    );
    '''
    with sqlite3.connect("customers1.db") as conn:
        conn.executescript(schema)
        data = load_data_from_excel()
        print(f"Number of rows to insert into database: {len(data)}")
        
        try:
            data.to_sql('customer', conn, if_exists='append', index=False)
        except Exception as e:
            print(f"Error inserting data: {e}")
        
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM customer")
        row_count = cur.fetchone()[0]
        print(f"Number of rows in database after insertion: {row_count}")

def check_database_content():
    with sqlite3.connect("customers1.db") as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM customer")
        all_rows = cur.fetchall()
        print(f"Total rows in database: {len(all_rows)}")
        for row in all_rows[:10]:
            print(row)

@app1.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        customer_name = request.form['customer_name']
        address = request.form['address']
        packages = int(request.form['packages'])
        network_connections = request.form['network_connections']
        prior_booking = request.form['prior_booking']

        with sqlite3.connect("customers1.db") as conn:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO customer (customer_name, address, packages, network_connections, prior_booking)
                VALUES (?, ?, ?, ?, ?)
            """, (customer_name, address, packages, network_connections, prior_booking))
            conn.commit()

        return redirect(url_for('dashboard'))

    return render_template('home.html')

@app1.route('/dashboard')
def dashboard():
    print("Dashboard route accessed")
    with sqlite3.connect("customers1.db") as conn:
        cur = conn.cursor()

        cur.execute("SELECT customer_name FROM customer WHERE packages=400")
        package_400_customers = cur.fetchall()
        cur.execute("SELECT COUNT(*) FROM customer WHERE packages=400")
        package_400_count = cur.fetchone()[0]

        cur.execute("SELECT customer_name FROM customer WHERE packages=350")
        package_350_customers = cur.fetchall()
        cur.execute("SELECT COUNT(*) FROM customer WHERE packages=350")
        package_350_count = cur.fetchone()[0]

        cur.execute("SELECT customer_name, address, packages, prior_booking FROM customer WHERE network_connections='yes'")
        network_yes_customers = cur.fetchall()

        cur.execute("""
            SELECT address, GROUP_CONCAT(customer_name, ', ') as customer_names, COUNT(customer_name) as customer_count
            FROM customer
            GROUP BY address
        """)
        addresses = cur.fetchall()

    return render_template(
        'dashboard.html',
        package_400_customers=package_400_customers,
        package_400_count=package_400_count,
        package_350_customers=package_350_customers,
        package_350_count=package_350_count,
        network_yes_customers=network_yes_customers,
        addresses=addresses
    )

if __name__ == '__main__':
    init_db()
    check_database_content()
    app1.run(debug=True, port=8080)

