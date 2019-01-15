from flask import Flask, request, Response
import sqlite3
import json

app = Flask(__name__)

@app.route('/')
def welcome_message():
    return 'Welcome to my Shopify Application! :) Try an endpoint out!'

# CRUD operations on product
@app.route('/product', methods=["GET","POST", "DELETE"])
def product():
    #Begin database connection
    with sqlite3.connect('database.db') as conn:

        # GET REQUEST
        if request.method == "GET":
            # Reqest params
            productId = request.args.get("productid")
            isAvailable = request.args.get("isavailable", type=bool)
            print(isAvailable)
            cur = conn.cursor()

            if isAvailable:
                if isAvailable is True:
                    cur.execute("SELECT * FROM product WHERE NOT inventoryCount=0")
                    result = cur.fetchall()
                    
                    if result is not None:
                        return json.dumps(result), 200, {'ContentType':'application/json'} 
                    else:
                        return json.dumps({'success': False}), 500, {'ContentType': 'application/json'}

            elif productId:
                cur.execute("SELECT * FROM product WHERE productId = ?", [productId])
                result = cur.fetchall()
                
                if result is not None:
                    return json.dumps(result), 200, {'ContentType':'application/json'}
                else:
                    return json.dumps({'success': False}), 500, {'ContentType': 'application/json'}
            
            cur.execute("SELECT * FROM product")
            result = cur.fetchall()
            return json.dumps(result), 200, {'ContentType':'application/json'}

        # POST REQUEST
        if request.method == "POST":
            productId = request.args.get('productid')
            title = request.args.get('title', type=str)
            price = request.args.get('price')
            inventoryCount = request.args.get('inventorycount')

            cur = conn.cursor()
            cur.execute("SELECT * FROM product WHERE productId = ?", [productId])
            result = cur.fetchall()
            try:
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
def checkout():
    #Begin database connection
    with sqlite3.connect('database.db') as conn:

        # POST REQUEST
        if request.method == "POST":
            productIds = request.args.get('productids').split(",")
            print(productIds)

            cur = conn.cursor()
            results = []
            for ids in productIds:

                cur.execute("SELECT * FROM product WHERE productId=?", [ids])
                result = cur.fetchall()[0]
                results.append(result)
            print(results)
            try:
                counter = 0
                for item in results:
                    print(item)
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

if __name__ == '__main__':
    app.run(debug=True)