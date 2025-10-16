import mysql.connector

try:
    # Connect to MySQL
    conn = mysql.connector.connect(
        host="localhost",
        user="root",              # change if your MySQL username is different
        password="Vaishnavi@8431",   # <-- replace this with your real password
        database="bankdb"
    )

    if conn.is_connected():
        print("✅ Connected to MySQL database successfully!")

        # Get cursor and list all tables
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES;")

        print("\n📋 Tables in bankdb:")
        for table in cursor.fetchall():
            print(table)

except mysql.connector.Error as err:
    print(f"❌ Error: {err}")

finally:
    if 'conn' in locals() and conn.is_connected():
        cursor.close()
        conn.close()
        print("\n🔒 Connection closed.")
