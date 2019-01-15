from flask import Flask, request, Response
import sqlite3
import json

app = Flask(__name__)

def view_product(productId, title, price, inventoryCount):
    d = dict()
    d['productId'] = productId
    d['title'] = title
    d['price'] = price
    d['inventoryCount'] = inventoryCount
    return d

def view_cart(cartId, cartValue, product):
    d = dict()
    d['cartId'] = cartId
    d['cartValue'] = cartValue
    d['product'] = product
    return d

def view_cartItem(cartItemId, productId, title, price, inventoryCount):
    d = dict()
    d['cartItemId'] = cartItemId
    d['productId'] = productId
    d['title'] = title
    d['price'] = price
    d['inventoryCount'] = inventoryCount
    return d

@app.route('/')
def welcome_message():
    return '''Welcome to my Shopify Application! :) Try an endpoint out!
           
            The database already contains some data, so entering '1' as an Id for anything will return data.
            I highly suggest starting off with the /product [GET] endpoint with no params to see what my store is packing!

            Also, having a JSON-viewer plugin for your browser would make life a lot, lot easier ;)

            Available endpoints:
            
            To get, create, or delete products
            /product            GET         params: productid(int, optional), available(bool, optional)
            /product            POST        params: productid(int, required), title(string, required), price(real, required), inventorycount(int, required)        
            /product            DELETE      params: productid(int, required) OR title(string, required)

            To checkout products (purchase them)
            /checkout           POST        params: productids(int, required)

            To create a new cart
            /cart               POST        params: cartid(int, required)

            To get, add, or remove cart items
            /cart/[cartid]      GET         params: cartid(int, required)
            /cart/[cartid]      POST        params: cartid(int, required), cartitemid(int, required), productid(int, required)
            /cart/[cartid]      DELETE      params: cartid(int, required), productid(int, required)
            '''

# CRUD operations on product
@app.route('/product', methods=["GET","POST", "DELETE"])
def product_tdg():
    #Begin database connection
    with sqlite3.connect('database.db') as conn:

        # GET REQUEST
        if request.method == "GET":
            # Reqest params
            productId = request.args.get("productid")
            available = request.args.get("available", type=bool)
            cur = conn.cursor()

            if available:
                cur.execute("SELECT * FROM product WHERE NOT inventoryCount=0")
                result = cur.fetchall()
                
                # Create viewable object for product(s) 
                products = []
                for product in result:
                    products.append(view_product(product[0], product[1], product[2], product[3]))
                return json.dumps(products), 200, {'ContentType':'application/json'} 

            elif productId:
                cur.execute("SELECT * FROM product WHERE productId = ?", [productId])
                result = cur.fetchall()
                
                # Create viewable object for product(s) 
                products = []
                for product in result:
                    products.append(view_product(product[0], product[1], product[2], product[3]))
                return json.dumps(products), 200, {'ContentType':'application/json'} 
            
            cur.execute("SELECT * FROM product")
            result = cur.fetchall()
            products = []
            for product in result:
                products.append(view_product(product[0], product[1], product[2], product[3]))
            return json.dumps(products), 200, {'ContentType':'application/json'} 

        # POST REQUEST
        if request.method == "POST":
            productId = request.args.get('productid')
            title = request.args.get('title', type=str)
            price = request.args.get('price')
            inventoryCount = request.args.get('inventorycount')

            cur = conn.cursor()
            # Get product from database it it exists
            cur.execute("SELECT * FROM product WHERE productId = ?", [productId])
            result = cur.fetchall()
            try:
                # Update if it exists, insert if not
                if not len(result) == 0:
                    cur.execute("UPDATE product SET inventoryCount = ? WHERE productId = ?", [inventoryCount, productId])
                    conn.commit()
                    print("Updated Sucessfully")

                else:
                    cur.execute("INSERT INTO product (productId, title, price, inventoryCount) VALUES (?, ?, ?, ?)", [productId, title, price, inventoryCount])
                    conn.commit()
                    print("Inserted Sucessfully")
            except Exception as e:
                print(e)
                conn.rollback()
                return json.dumps({'success': False, 'description': 'cannot UPDATE/INSERT record'}), 500, {'ContentType': 'application/json'}

            return json.dumps({'success':True, 'description': 'record updated/inserted'}), 200, {'ContentType':'application/json'}

        # DELETE REQUEST (BY ID OR TITLE)
        if request.method == "DELETE":

            productId = request.args.get('productid')
            title = request.args.get('title', type=str)

            # Check if record exists
            cur = conn.cursor()
            if title:
                cur.execute("SELECT * FROM product WHERE title = ?", [title])
            else:
                cur.execute("SELECT * FROM product WHERE productId = ?", [productId])
            
            result = cur.fetchall()[0]
            # Get Id of the record that is to be deleted
            productId = result[0]
            try: 
                if result:
                    cur.execute("DELETE FROM product WHERE productId = ?", [productId])
                    conn.commit()
                    print("Deleted Sucessfully")
                else:
                    return json.dumps({'success': False, 'description': 'record does not exist'}), 400, {'ContentType': 'application/json'}
            
            except Exception as e:
                print(e)
                conn.rollback()
                return json.dumps({'success': False, 'description': 'cannot DELETE record'}), 500, {'ContentType': 'application/json'}
        
            return json.dumps({'success':True, 'description': 'record deleted'}), 200, {'ContentType':'application/json'}

        conn.close()
        return json.dumps({'success': False, 'description': 'cannot process request'}), 405, {'ContentType': 'application/json'}

# Checkout product
@app.route('/checkout', methods=["POST"])
def checkout_tdg():
    #Begin database connection
    with sqlite3.connect('database.db') as conn:

        # POST REQUEST
        if request.method == "POST":
            productIds = request.args.get('productids').split(",")

            cur = conn.cursor()
            results = []

            # Iterate over Ids, fetch each record, and append to results object
            for ids in productIds:

                cur.execute("SELECT * FROM product WHERE productId=?", [ids])
                result = cur.fetchall()[0]
                results.append(result)
            try:
                ## Record update counter
                counter = 0

                # Iterate over Ids, update inventory count of each record
                for item in results:
                    itemId = item[0]
                    itemCount = item[3]

                    if itemCount != 0:
                        cur.execute("UPDATE product SET inventoryCount = ? WHERE productId = ?", [itemCount-1, itemId])
                        conn.commit()
                        counter = counter + 1

                print("Updated Sucessfully")

            except Exception as e:
                print(e)
                conn.rollback()
                return json.dumps({'success': False, 'description': 'cannot UPDATE inventory count'}), 500, {'ContentType': 'application/json'}

            return json.dumps({'success':True, 'description': '%d record updated' %(counter)}), 200, {'ContentType':'application/json'}

        conn.close()
        return json.dumps({'success': False, 'description': 'cannot process request'}), 405, {'ContentType': 'application/json'}

# Create cart
@app.route('/cart', methods=["POST"])
def cart_tdg():
    #Begin database connection
    with sqlite3.connect('database.db') as conn:
    
        # POST REQUEST
        if request.method == "POST":
            cartId = request.args.get('cartid')
            cartValue = 0
            cur = conn.cursor()
            try:
                if cartId is None:
                    raise Exception('Cart Id is not set')
                cur.execute("INSERT INTO cart (cartId, cartValue) VALUES (?, ?)", [cartId, cartValue])
                conn.commit()

            except Exception as e:
                print(e)
                conn.rollback()
                return json.dumps({'success': False, 'description': 'cannot create cart'}), 500, {'ContentType': 'application/json'}
                        
            return json.dumps({'success':True, 'description': 'cart created'}), 200, {'ContentType':'application/json'}
    
    conn.close()
    return json.dumps({'success': False, 'description': 'cannot process request'}), 405, {'ContentType': 'application/json'}

# CRUD operations on cart items
@app.route('/cart/<cartId>', methods=["GET", "POST", "DELETE"])
def cart_item_tdg(cartId):
    #Begin database connection
    with sqlite3.connect('database.db') as conn:
    
        # GET REQUEST
        if request.method == "GET":
            cur = conn.cursor()

            # Verify that the Cart is valid
            cur.execute('SELECT * FROM cart WHERE cartId = ?', [cartId])
            cartResult = cur.fetchall()[0]
            if cartResult is None:
                return json.dumps({'success': False, 'description': 'cart does not exist'}), 400, {'ContentType': 'application/json'}

            # Get all products in cart
            cur.execute('''SELECT * FROM cartItem ci
                        LEFT JOIN product p USING(productId)
                        WHERE ci.cartId = ?''', [cartId])
            productResult = cur.fetchall()
            # No products in cart so return nothing
            if productResult is None:
                return json.dumps(productResult), 200, {'ContentType':'application/json'} 

            # Create view_cartItem object for viewing in frontend
            products = []
            for product in productResult:
                products.append(view_cartItem(product[0], product[2], product[3], product[4], product[5]))

            # Create view_cart object for viewing in frontend
            cartView = view_cart(cartResult[0], cartResult[1], products)
            return json.dumps(cartView), 200, {'ContentType':'application/json'} 

        # POST REQUEST
        if request.method == "POST":
            cartItemId = request.args.get('cartitemid')
            productId = request.args.get('productid')

            if cartItemId is None or productId is None:
                return json.dumps({'success': False, 'description': 'cartItem Id or product Id is not provided'}), 400, {'ContentType': 'application/json'}

            cur = conn.cursor()

            # Verify that the Cart is valid and get its value if it is
            cur.execute('SELECT * FROM cart WHERE cartId = ?', [cartId])
            cartResult = cur.fetchall()[0]
            if cartResult is None:
                return json.dumps({'success': False, 'description': 'cart does not exist'}), 400, {'ContentType': 'application/json'}
            cartValue = cartResult[1]

            # Verify that the Product is valid and get the price if it is
            cur.execute('SELECT * FROM product WHERE productId = ?', [productId])
            productResult = cur.fetchall()[0]
            if productResult is None:
                return json.dumps({'success': False, 'description': 'product does not exist'}), 400, {'ContentType': 'application/json'}
            productValue = productResult[2]

            try:
                cur.execute('INSERT INTO cartItem (cartItemId, cartId, productId) VALUES (?, ?, ?)', [cartItemId, cartId, productId])
                cur.execute('UPDATE cart SET cartValue = ? WHERE cartId = ?', [cartValue + productValue, cartId])
                conn.commit()
                print('Item sucessfully added to cart')

            except Exception as e:
                print(e)
                conn.rollback()
                return json.dumps({'success': False, 'description': 'cannot add item to cart'}), 500, {'ContentType': 'application/json'}
                
            return json.dumps({'success':True, 'description': 'cart item added'}), 200, {'ContentType':'application/json'}

        # DELETE REQUEST
        if request.method == "DELETE":
            productId = request.args.get('productid')

            if productId is None:
                return json.dumps({'success': False, 'description': 'cartItem Id or product Id is not provided'}), 400, {'ContentType': 'application/json'}

            cur = conn.cursor()

            # Verify that the Cart is valid and get its value if it is
            cur.execute('SELECT * FROM cart WHERE cartId = ?', [cartId])
            cartResult = cur.fetchall()[0]
            if cartResult is None:
                return json.dumps({'success': False, 'description': 'cart does not exist'}), 400, {'ContentType': 'application/json'}
            cartValue = cartResult[1]

            # Verify that the Product is valid and get the price if it is
            cur.execute('SELECT * FROM product WHERE productId = ?', [productId])
            productResult = cur.fetchall()[0]
            if productResult is None:
                return json.dumps({'success': False, 'description': 'product does not exist'}), 400, {'ContentType': 'application/json'}
            productValue = productResult[2]

            try:
                cur.execute('DELETE FROM cartItem WHERE productId = ?', [productId])
                cur.execute('UPDATE cart SET cartValue = ? WHERE cartId = ?', [cartValue - productValue, cartId])
                conn.commit()
                print('Item sucessfully removed from cart')

            except Exception as e:
                print(e)
                conn.rollback()
                return json.dumps({'success': False, 'description': 'cannot remove item from cart'}), 500, {'ContentType': 'application/json'}
                
            return json.dumps({'success':True, 'description': 'item removed from cart'}), 200, {'ContentType':'application/json'}

    conn.close()
    return json.dumps({'success': False, 'description': 'cannot process request'}), 405, {'ContentType': 'application/json'}

if __name__ == '__main__':
    app.run(debug=True)