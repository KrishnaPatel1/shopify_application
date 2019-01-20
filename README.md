# shopify_application
### Shopify backend developer intern challenge Summer 2019

Hey there! Looks like you've found my awesome application for Shopify!

So setting up the project is fairly simple:
* Have python installed (version 3.X)
* Run `pip install -r requirements.txt`
* Set shop.py as the flask app (`export FLASK_APP=shop.py`)
* Run the app! (`flask run`)
* Get on your browser, go to `http://127.0.0.1:5000` (default) and check out my store! ;)

I've also set up a really basic unit test and integrated it with Travis CI to execute at every commit!

### Available endpoints:
            
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

### DB Schema

![alt text](https://github.com/KrishnaPatel1/shopify_application/blob/master/DB%20Shema.jpeg)
