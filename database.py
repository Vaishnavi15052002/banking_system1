import mysql.connector
from decimal import Decimal

# --- Database connection ---
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",               # <-- your MySQL username
        password="Vaishnavi@8431",  # <-- your MySQL password
        database="bankdb"
    )

# --- Create a new customer ---
def create_customer(fname, lname, email, phone, acc_type):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.callproc("AddCustomer", [fname, lname, email, phone, acc_type])
        conn.commit()
    finally:
        cursor.close()
        conn.close()

# --- Get all accounts ---
def get_accounts():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT a.account_id, a.account_number, c.first_name, c.last_name, a.account_type, a.balance
            FROM accounts a
            JOIN customers c ON a.customer_id = c.customer_id
        """)
        data = cursor.fetchall()
        # Convert balance to Decimal
        for acc in data:
            acc['balance'] = Decimal(acc['balance'])
        return data
    finally:
        cursor.close()
        conn.close()

# --- Get balance of account ---
def get_balance(account_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT balance FROM accounts WHERE account_id=%s", (account_id,))
        result = cursor.fetchone()
        if result:
            return Decimal(result[0])
        return Decimal('0.0')
    finally:
        cursor.close()
        conn.close()

# --- Update account balance ---
def update_balance(account_id, new_balance):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        # Ensure new_balance is converted to string to avoid float precision issues
        cursor.execute("UPDATE accounts SET balance=%s WHERE account_id=%s", (str(new_balance), account_id))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

# --- Record transaction ---
def record_transaction(account_id, txn_type, amount):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO transactions (account_id, type, amount) VALUES (%s, %s, %s)",
            (account_id, txn_type, str(amount))  # store as string to match DECIMAL
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()
