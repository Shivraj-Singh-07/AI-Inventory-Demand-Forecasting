import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", 3306)),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )

        print("Database Connected Successfully!")
        return conn

    except mysql.connector.Error as error:
        print("Connection Failed:", error)
        return None


if __name__ == "__main__":
    conn = get_connection()

    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products")

        records = cursor.fetchall()

        print("\nProduct Records:")

        for record in records:
            print(record)

        cursor.close()
        conn.close()