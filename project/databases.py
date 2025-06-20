import sqlite3
from aiogram.types import User

class Database:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            id TEXT UNIQUE PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            username TEXT UNIQUE,
            phone TEXT UNIQUE,
            location TEXT,
            address TEXT,
            registered INTEGER DEFAULT 0
        )''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            category_id INTEGER,
            price REAL,
            description TEXT,
            FOREIGN KEY (category_id) REFERENCES categories(id)
        )''')
        self.conn.commit()

    def add_user(self, user: dict) -> bool:
        try:
            self.cursor.execute(
                "INSERT INTO users(id, username, first_name, last_name) VALUES (?, ?, ?, ?)",
                (user['id'], user['username'], user['first_name'], user['last_name'])
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def has_user(self, user_id: str) -> bool:
        try:
            self.cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
            return self.cursor.fetchone() is not None
        except Exception as e:
            print(e)
            return False

    def is_registered(self, user_id: str) -> bool:
        try:
            self.cursor.execute("SELECT registered FROM users WHERE id = ?", (user_id,))
            result = self.cursor.fetchone()
            return result and result[0] == 1
        except Exception as e:
            print(e)
            return False

    def set_registered(self, user_id: str) -> bool:
        try:
            self.cursor.execute("UPDATE users SET registered = 1 WHERE id = ?", (user_id,))
            self.conn.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def update_any_col(self, col_name: str, new_value: str, user_id: str) -> bool:
        try:
            self.cursor.execute(
                f"UPDATE users SET {col_name} = ? WHERE id = ?",
                (str(new_value), user_id)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def add_category(self, name: str) -> bool:
        try:
            self.cursor.execute("INSERT INTO categories (name) VALUES (?)", (name,))
            self.conn.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def get_categories(self) -> list:
        try:
            self.cursor.execute("SELECT id, name FROM categories")
            return self.cursor.fetchall()
        except Exception as e:
            print(e)
            return []

    def delete_category(self, category_id: int) -> bool:
        try:
            self.cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            print(e)
            return False

    def add_product(self, name: str, category_id: int, price: float, description: str) -> bool:
        try:
            self.cursor.execute(
                "INSERT INTO products (name, category_id, price, description) VALUES (?, ?, ?, ?)",
                (name, category_id, price, description)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(e)
            return False

    def search_products(self, query: str) -> list:
        try:
            self.cursor.execute(
                "SELECT p.id, p.name, c.name, p.price, p.description FROM products p JOIN categories c ON p.category_id = c.id WHERE p.name LIKE ?",
                (f'%{query}%',)
            )
            return self.cursor.fetchall()
        except Exception as e:
            print(e)
            return []

    def delete_product(self, product_id: int) -> bool:
        try:
            self.cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            print(e)
            return False

    def update_product(self, product_id: int, name: str = None, category_id: int = None, price: float = None, description: str = None) -> bool:
        try:
            updates = []
            values = []
            if name:
                updates.append("name = ?")
                values.append(name)
            if category_id:
                updates.append("category_id = ?")
                values.append(category_id)
            if price is not None:
                updates.append("price = ?")
                values.append(price)
            if description:
                updates.append("description = ?")
                values.append(description)
            if updates:
                values.append(product_id)
                query = f"UPDATE products SET {', '.join(updates)} WHERE id = ?"
                self.cursor.execute(query, values)
                self.conn.commit()
                return self.cursor.rowcount > 0
            return False
        except Exception as e:
            print(e)
            return False