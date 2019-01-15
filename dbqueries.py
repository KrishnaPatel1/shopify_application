import sqlite3

conn = sqlite3.connect('database.db')

conn.execute('''CREATE TABLE product
                (productId INTEGER PRIMARY KEY,
                title TEXT,
                price REAL,
                inventoryCount INTEGER
                )''')

conn.execute('''CREATE TABLE cart
                (cartId INTEGER PRIMARY KEY,
                cartValue REAL)''')

conn.execute('''CREATE TABLE cartItem
                (cartItemId INTEGER PRIMARY KEY,
                cartId INTEGER,
                productId INTEGER,
                FOREIGN KEY(cartId) REFERENCES cart(cartId),
                FOREIGN KEY(productId) REFERENCES product(productId)
                )''')