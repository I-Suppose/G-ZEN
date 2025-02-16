from flask import Flask, render_template, session, redirect, url_for, request, flash, jsonify, abort
from functools import wraps
import os
from datetime import datetime
import json
import random
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# Initialize empty USERS dictionary
USERS = {}

def load_users_data():
    try:
        with open('users_data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        return {}

def save_users_data():
    try:
        with open('users_data.json', 'w') as f:
            json.dump(USERS, f, indent=4)
        print(f"Saved users data: {USERS}")  # Debug print
    except Exception as e:
        print(f"Error saving data: {str(e)}")

def update_existing_orders():
    try:
        for email, user_data in USERS.items():
            if 'orders' in user_data:
                customer_name = f"{user_data['first_name']} {user_data['last_name']}"
                for order in user_data['orders']:
                    if 'customer_name' not in order:
                        order['customer_name'] = customer_name
                    # Also update the items key to item_list if needed
                    if 'items' in order and 'item_list' not in order:
                        order['item_list'] = order['items']
                        del order['items']
        save_users_data()
        print("Updated existing orders with customer names and fixed item lists")
    except Exception as e:
        print(f"Error updating orders: {str(e)}")

# Load data at startup
USERS = load_users_data()
update_existing_orders()  # Now this will work since the function is defined above

PRODUCTS = {
    # Furniture (1-10)
    1: {
        'id': 1,
        'name': 'Bamboo Chair',
        'price': 299.99,
        'description': 'Eco-friendly chair crafted from sustainable bamboo. Features natural finishes and ergonomic design.',
        'category': 'furniture',
        'image': 'placeholder.jpg',
        'certifications': ['FSC Certified', 'Eco-Friendly']
    },
    2: {
        'id': 2,
        'name': 'Reclaimed Wood Dining Table',
        'price': 899.99,
        'description': 'Handcrafted dining table made from reclaimed wood, saving trees and giving new life to vintage materials.',
        'category': 'furniture',
        'image': 'placeholder.jpg',
        'certifications': ['FSC Certified', 'Recycled Materials']
    },
    3: {
        'id': 3,
        'name': 'Cork Coffee Table',
        'price': 449.99,
        'description': 'Sustainable coffee table made from cork oak bark, harvested without harming trees. Naturally water-resistant.',
        'category': 'furniture',
        'image': 'placeholder.jpg',
        'certifications': ['Eco-Friendly', 'Sustainable Harvest']
    },
    4: {
        'id': 4,
        'name': 'Hemp Fabric Sofa',
        'price': 1299.99,
        'description': 'Three-seater sofa upholstered with organic hemp fabric. Features recycled steel springs and natural latex cushioning.',
        'category': 'furniture',
        'image': 'placeholder.jpg',
        'certifications': ['GOTS Certified', 'Zero Waste']
    },
    5: {
        'id': 5,
        'name': 'Recycled Plastic Bookshelf',
        'price': 599.99,
        'description': 'Modern bookshelf made from recycled ocean plastics. Each piece helps remove 50kg of plastic from our oceans.',
        'category': 'furniture',
        'image': 'placeholder.jpg',
        'certifications': ['Ocean Friendly', 'Recycled Materials']
    },
    6: {
        'id': 6,
        'name': 'Sustainable Teak Bed Frame',
        'price': 1499.99,
        'description': 'Queen-size bed frame made from sustainably harvested teak wood. Features natural oil finish.',
        'category': 'furniture',
        'image': 'placeholder.jpg',
        'certifications': ['FSC Certified', 'Sustainable Harvest']
    },
    7: {
        'id': 7,
        'name': 'Mushroom Leather Ottoman',
        'price': 399.99,
        'description': 'Innovative ottoman covered in mushroom-based leather alternative. 100% biodegradable and cruelty-free.',
        'category': 'furniture',
        'image': 'placeholder.jpg',
        'certifications': ['Vegan', 'Biodegradable']
    },
    8: {
        'id': 8,
        'name': 'Recycled Metal Cabinet',
        'price': 799.99,
        'description': 'Storage cabinet crafted from recycled industrial metals. Each piece has unique patina patterns.',
        'category': 'furniture',
        'image': 'placeholder.jpg',
        'certifications': ['Recycled Materials', 'Zero Waste']
    },
    9: {
        'id': 9,
        'name': 'Bamboo Room Divider',
        'price': 349.99,
        'description': 'Elegant room divider made from sustainable bamboo. Features natural fiber rope details.',
        'category': 'furniture',
        'image': 'placeholder.jpg',
        'certifications': ['FSC Certified', 'Eco-Friendly']
    },
    10: {
        'id': 10,
        'name': 'Hemp Meditation Cushion',
        'price': 89.99,
        'description': 'Floor cushion made from organic hemp fabric and filled with organic buckwheat hulls.',
        'category': 'furniture',
        'image': 'placeholder.jpg',
        'certifications': ['GOTS Certified', 'Organic']
    },

    # Clothing (11-20)
    11: {
        'id': 11,
        'name': 'Organic Cotton T-Shirt',
        'price': 39.99,
        'description': 'Classic t-shirt made from 100% organic cotton. Dyed with natural, non-toxic colors.',
        'category': 'clothing',
        'image': 'placeholder.jpg',
        'certifications': ['Fair Trade']
    },
    12: {
        'id': 12,
        'name': 'Hemp Cargo Pants',
        'price': 89.99,
        'description': 'Durable cargo pants made from sustainable hemp fiber. Naturally resistant to UV and mold.',
        'category': 'clothing',
        'image': 'placeholder.jpg',
        'certifications': ['Eco-Friendly', 'Sustainable Fiber']
    },
    13: {
        'id': 13,
        'name': 'Recycled Ocean Plastic Jacket',
        'price': 159.99,
        'description': 'Waterproof jacket made from recycled ocean plastics. Each jacket recycles 50 plastic bottles.',
        'category': 'clothing',
        'image': 'placeholder.jpg',
        'certifications': ['Ocean Friendly', 'Recycled Materials']
    },
    14: {
        'id': 14,
        'name': 'Bamboo Fiber Socks',
        'price': 14.99,
        'description': 'Ultra-soft socks made from bamboo fiber. Naturally antibacterial and moisture-wicking.',
        'category': 'clothing',
        'image': 'placeholder.jpg',
        'certifications': ['Eco-Friendly', 'Sustainable Fiber']
    },
    15: {
        'id': 15,
        'name': 'Organic Linen Dress',
        'price': 129.99,
        'description': 'Elegant dress made from organic linen. Requires minimal water in production.',
        'category': 'clothing',
        'image': 'placeholder.jpg',
        'certifications': ['GOTS Certified', 'Water Conservative']
    },
    16: {
        'id': 16,
        'name': 'Cork Wallet',
        'price': 49.99,
        'description': 'Slim wallet made from sustainable cork. Water-resistant and durable.',
        'category': 'clothing',
        'image': 'placeholder.jpg',
        'certifications': ['Vegan', 'Sustainable Materials']
    },
    17: {
        'id': 17,
        'name': 'Recycled Wool Sweater',
        'price': 119.99,
        'description': 'Cozy sweater made from recycled wool garments. Each piece saves 2000 liters of water.',
        'category': 'clothing',
        'image': 'placeholder.jpg',
        'certifications': ['Recycled Materials', 'Water Conservative']
    },
    18: {
        'id': 18,
        'name': 'Organic Cotton Jeans',
        'price': 99.99,
        'description': 'Classic jeans made from organic cotton. Uses 91% less water than conventional denim.',
        'category': 'clothing',
        'image': 'placeholder.jpg',
        'certifications': ['GOTS Certified', 'Water Conservative']
    },
    19: {
        'id': 19,
        'name': 'Pineapple Leather Belt',
        'price': 59.99,
        'description': 'Stylish belt made from Piñatex - a leather alternative made from pineapple leaf fibers.',
        'category': 'clothing',
        'image': 'placeholder.jpg',
        'certifications': ['Vegan', 'Innovative Materials']
    },
    20: {
        'id': 20,
        'name': 'Bamboo Pajama Set',
        'price': 79.99,
        'description': 'Comfortable pajama set made from bamboo fiber. Naturally temperature-regulating.',
        'category': 'clothing',
        'image': 'placeholder.jpg',
        'certifications': ['Eco-Friendly', 'Sustainable Fiber']
    },

    # Toys (21-30)
    21: {
        'id': 21,
        'name': 'Bamboo Building Blocks',
        'price': 34.99,
        'description': 'Educational building blocks made from sustainable bamboo. Non-toxic finishes safe for children.',
        'category': 'toys',
        'image': 'placeholder.jpg',
        'certifications': ['Child Safe', 'Eco-Friendly']
    },
    22: {
        'id': 22,
        'name': 'Recycled Plastic Train Set',
        'price': 49.99,
        'description': 'Colorful train set made from recycled milk jugs. Each set recycles 8 plastic containers.',
        'category': 'toys',
        'image': 'placeholder.jpg',
        'certifications': ['Recycled Materials', 'Child Safe']
    },
    23: {
        'id': 23,
        'name': 'Organic Cotton Plush Bear',
        'price': 29.99,
        'description': 'Soft teddy bear made from organic cotton and stuffed with recycled materials.',
        'category': 'toys',
        'image': 'placeholder.jpg',
        'certifications': ['GOTS Certified', 'Child Safe']
    },
    24: {
        'id': 24,
        'name': 'Sustainable Wood Puzzle',
        'price': 24.99,
        'description': 'Educational puzzle made from sustainably harvested wood. Features non-toxic paints.',
        'category': 'toys',
        'image': 'placeholder.jpg',
        'certifications': ['FSC Certified', 'Child Safe']
    },
    25: {
        'id': 25,
        'name': 'Recycled Art Kit',
        'price': 39.99,
        'description': 'Creative art kit featuring supplies made from recycled materials. Includes natural dyes.',
        'category': 'toys',
        'image': 'placeholder.jpg',
        'certifications': ['Recycled Materials', 'Non-Toxic']
    },
    26: {
        'id': 26,
        'name': 'Cork Building Tiles',
        'price': 44.99,
        'description': 'Innovative building tiles made from cork. Naturally antimicrobial and safe for children.',
        'category': 'toys',
        'image': 'placeholder.jpg',
        'certifications': ['Child Safe', 'Sustainable Materials']
    },
    27: {
        'id': 27,
        'name': 'Bamboo Musical Set',
        'price': 54.99,
        'description': 'Set of musical instruments made from sustainable bamboo. Includes drum, xylophone, and shakers.',
        'category': 'toys',
        'image': 'placeholder.jpg',
        'certifications': ['Eco-Friendly', 'Child Safe']
    },
    28: {
        'id': 28,
        'name': 'Recycled Rubber Ball Set',
        'price': 19.99,
        'description': 'Set of play balls made from recycled rubber. Durable and safe for outdoor play.',
        'category': 'toys',
        'image': 'placeholder.jpg',
        'certifications': ['Recycled Materials', 'Child Safe']
    },
    29: {
        'id': 29,
        'name': 'Organic Play Dough Set',
        'price': 22.99,
        'description': 'Natural play dough made from organic ingredients. Safe if accidentally ingested.',
        'category': 'toys',
        'image': 'placeholder.jpg',
        'certifications': ['Organic', 'Non-Toxic']
    },
    30: {
        'id': 30,
        'name': 'Sustainable Wood Kitchen Set',
        'price': 69.99,
        'description': 'Play kitchen set made from sustainable wood. Features natural finishes.',
        'category': 'toys',
        'image': 'placeholder.jpg',
        'certifications': ['FSC Certified', 'Child Safe']
    },

    # Stationery (31-40)
    31: {
        'id': 31,
        'name': 'Recycled Paper Notebook',
        'price': 14.99,
        'description': 'Notebook made from 100% recycled paper. Features seed-infused cover that can be planted.',
        'category': 'stationery',
        'image': 'placeholder.jpg',
        'certifications': ['Recycled Materials', 'Zero Waste']
    },
    32: {
        'id': 32,
        'name': 'Bamboo Pen Set',
        'price': 29.99,
        'description': 'Set of refillable pens made from sustainable bamboo. Includes organic ink refills.',
        'category': 'stationery',
        'image': 'placeholder.jpg',
        'certifications': ['Eco-Friendly', 'Sustainable Materials']
    },
    33: {
        'id': 33,
        'name': 'Hemp Paper Sketchbook',
        'price': 24.99,
        'description': 'Artist sketchbook made from hemp paper. Acid-free and perfect for various media.',
        'category': 'stationery',
        'image': 'placeholder.jpg',
        'certifications': ['Sustainable Fiber', 'Acid Free']
    },
    34: {
        'id': 34,
        'name': 'Recycled Pencil Set',
        'price': 9.99,
        'description': 'Set of pencils made from recycled newspapers. Each pencil plants a tree when finished.',
        'category': 'stationery',
        'image': 'placeholder.jpg',
        'certifications': ['Recycled Materials', 'Tree Planting']
    },
    35: {
        'id': 35,
        'name': 'Cork Pencil Case',
        'price': 19.99,
        'description': 'Durable pencil case made from sustainable cork. Water-resistant and naturally antimicrobial.',
        'category': 'stationery',
        'image': 'placeholder.jpg',
        'certifications': ['Sustainable Materials', 'Vegan']
    },
    36: {
        'id': 36,
        'name': 'Organic Cotton Calendar',
        'price': 34.99,
        'description': 'Wall calendar printed on organic cotton. Can be reused as a tea towel after the year ends.',
        'category': 'stationery',
        'image': 'placeholder.jpg',
        'certifications': ['GOTS Certified', 'Zero Waste']
    },
    37: {
        'id': 37,
        'name': 'Recycled Binder Set',
        'price': 27.99,
        'description': 'Set of binders made from recycled plastic. Durable and water-resistant.',
        'category': 'stationery',
        'image': 'placeholder.jpg',
        'certifications': ['Recycled Materials', 'Durable Design']
    },
    38: {
        'id': 38,
        'name': 'Bamboo Desk Organizer',
        'price': 39.99,
        'description': 'Desk organizer made from sustainable bamboo. Features modular design.',
        'category': 'stationery',
        'image': 'placeholder.jpg',
        'certifications': ['FSC Certified', 'Eco-Friendly']
    },
    39: {
        'id': 39,
        'name': 'Seed Paper Cards Set',
        'price': 16.99,
        'description': 'Set of greeting cards made from seed paper. Plant after use to grow wildflowers.',
        'category': 'stationery',
        'image': 'placeholder.jpg',
        'certifications': ['Zero Waste', 'Plantable']
    },
    40: {
        'id': 40,
        'name': 'Natural Ink Set',
        'price': 44.99,
        'description': 'Set of inks made from natural pigments. Non-toxic and biodegradable.',
        'category': 'stationery',
        'image': 'placeholder.jpg',
        'certifications': ['Organic', 'Non-Toxic']
    }
}

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if email in USERS and USERS[email]['password'] == password:
            session['user'] = email
            flash('Successfully logged in!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials', 'error')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))


@app.route('/category/<category>')
def category(category):
    products = [p for p in PRODUCTS.values() if p['category'] == category]
    # Add default image if missing
    for product in products:
        if 'image' not in product:
            product['image'] = 'placeholder.jpg'
    return render_template('category.html', category=category, products=products)


@app.route('/product/<int:product_id>')
def product(product_id):
    product = PRODUCTS.get(product_id)
    if not product:
        abort(404)
    success = request.args.get('success', False)
    return render_template('product.html', product=product, success=success)


@app.route('/cart')
def cart():
    cart_items = session.get('cart', [])
    # Create a list of cart items with product details
    cart_details = []
    total = 0
    for item in cart_items:
        product = PRODUCTS.get(item['id'])
        if product:
            item_total = product['price'] * item['quantity']
            total += item_total
            cart_details.append({
                'id': item['id'],
                'quantity': item['quantity'],
                'name': product['name'],
                'price': product['price'],
                'total': item_total,
                'image': product.get('image', 'placeholder.jpg')  # Default to placeholder if no image
            })
    
    return render_template('cart.html', cart_items=cart_details, total=total)


@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    product_id = int(request.form.get('product_id'))
    quantity = int(request.form.get('quantity', 1))

    cart = session.get('cart', [])
    
    # Check if product already in cart
    for item in cart:
        if item['id'] == product_id:
            item['quantity'] += quantity
            break
    else:
        cart.append({'id': product_id, 'quantity': quantity})
    
    session['cart'] = cart
    
    flash('Item added to cart successfully!', 'success')
    return redirect(request.referrer or url_for('index'))


@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    try:
        cart_items = session.get('cart', [])
        if not cart_items:
            flash('Your cart is empty', 'error')
            return redirect(url_for('cart'))

        email = session['user']
        user = USERS[email]
        
        cart_details = []
        total = 0
        
        for item in cart_items:
            product = PRODUCTS.get(item['id'])
            if product:
                item_total = product['price'] * item['quantity']
                total += item_total
                cart_details.append({
                    'id': item['id'],
                    'name': product['name'],
                    'price': product['price'],
                    'quantity': item['quantity'],
                    'total': item_total
                })

        return render_template('checkout.html', 
                             cart_items=cart_details, 
                             total=total,
                             user=user)
    except Exception as e:
        print(f"Error in checkout route: {str(e)}")
        flash('An error occurred during checkout', 'error')
        return redirect(url_for('cart'))


@app.route('/orders')
@login_required
def orders():
    try:
        email = session['user']
        user = USERS.get(email)
        
        if not user:
            flash('User not found', 'error')
            return redirect(url_for('login'))
            
        # Get user's orders, create empty list if none exist
        user_orders = user.get('orders', [])
        
        # Debug prints
        print("Email:", email)
        print("User:", user)
        print("Orders type:", type(user_orders))
        print("Orders content:", user_orders)
        
        return render_template('orders.html', orders=user_orders)
    except Exception as e:
        print(f"Error in orders route: {str(e)}")
        # Return an empty list if there's an error
        return render_template('orders.html', orders=[])


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    email = session['user']
    user = USERS[email]
    
    if request.method == 'POST':
        user['first_name'] = request.form.get('first_name')
        user['last_name'] = request.form.get('last_name')
        save_users_data()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    
    # Ensure orders list exists
    if 'orders' not in user:
        user['orders'] = []
        save_users_data()
    
    # Debug print
    print(f"User orders type: {type(user.get('orders'))}")
    print(f"User orders content: {user.get('orders')}")
    
    return render_template('profile.html', 
                         user=user,
                         orders=user.get('orders', []))  # Pass orders separately


@app.route('/wishlist')
def wishlist():
    if 'wishlist' not in session:
        session['wishlist'] = []
    
    # Get the wishlist items from the PRODUCTS dictionary
    wishlist_items = []
    total = 0  # Initialize total
    
    for product_id in session['wishlist']:
        if product_id in PRODUCTS:  # Make sure product exists
            product = PRODUCTS[product_id]
            wishlist_items.append(product)
            total += product['price']  # Add product price to total
    
    # Get user data if logged in
    user = None
    if 'user' in session:
        email = session['user']
        user = USERS.get(email)
    
    return render_template('wishlist.html', 
                         items=wishlist_items, 
                         total=total,
                         user=user)  # Pass user to template


@app.route('/add-to-wishlist', methods=['POST'])
def add_to_wishlist():
    product_id = int(request.form.get('product_id'))
    wishlist = session.get('wishlist', [])
    
    if product_id in wishlist:
        wishlist.remove(product_id)
        flash('Item removed from wishlist!', 'success')
    else:
        wishlist.append(product_id)
        flash('Item added to wishlist!', 'success')
    
    session['wishlist'] = wishlist
    return redirect(request.referrer or url_for('index'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        
        if email in USERS:
            flash('Email already registered', 'error')
            return redirect(url_for('signup'))
        
        # Initialize user with empty orders list
        USERS[email] = {
            'password': password,
            'first_name': first_name,
            'last_name': last_name,
            'addresses': [],
            'orders': []  # Initialize empty orders list
        }
        save_users_data()
        
        session['user'] = email
        flash('Account created successfully!', 'success')
        return redirect(url_for('profile'))
        
    return render_template('signup.html')


@app.route('/update-cart', methods=['POST'])
def update_cart():
    product_id = int(request.form.get('product_id'))
    quantity = int(request.form.get('quantity', 0))
    cart = session.get('cart', [])
    
    if quantity > 0:
        # Update quantity
        for item in cart:
            if item['id'] == product_id:
                item['quantity'] = quantity
                break
    else:
        # Remove item if quantity is 0
        cart = [item for item in cart if item['id'] != product_id]
    
    session['cart'] = cart
    return redirect(url_for('cart'))


@app.route('/remove-from-cart', methods=['POST'])
def remove_from_cart():
    product_id = int(request.form.get('product_id'))
    cart = session.get('cart', [])
    cart = [item for item in cart if item['id'] != product_id]
    session['cart'] = cart
    return redirect(url_for('cart'))


@app.route('/certifications')
def certifications():
    certification_info = {
        'FSC Certified': {
            'description': 'Forest Stewardship Council certification ensures products come from responsibly managed forests that provide environmental, social and economic benefits.'
        },
        'Eco-Friendly': {
            'description': 'Products designed to minimize environmental impact throughout their lifecycle, from production to disposal.'
        },
        'Recycled Materials': {
            'description': 'Made from previously used materials, reducing waste and conserving natural resources.'
        },
        'Organic': {
            'description': 'Produced without synthetic pesticides, fertilizers, or other artificial agents, promoting environmental sustainability.'
        },
        'Vegan': {
            'description': 'Contains no animal products or by-products and involves no animal testing.'
        },
        'Child Safe': {
            'description': 'Meets strict safety standards for children, free from harmful chemicals and choking hazards.'
        },
        'Zero Waste': {
            'description': 'Designed to be reused, recycled, or composted, with minimal to no waste going to landfills.'
        },
        'Sustainable Materials': {
            'description': 'Made from materials that can be produced long term without depleting natural resources.'
        },
        'GOTS Certified': {
            'description': 'Global Organic Textile Standard certification ensures organic status and socially responsible manufacturing.'
        },
        'Water Conservative': {
            'description': 'Produced using methods that minimize water consumption and protect water resources.'
        },
        'Sustainable Fiber': {
            'description': 'Made from renewable and environmentally responsible fiber sources.'
        },
        'Ocean Friendly': {
            'description': 'Products that help reduce ocean pollution and protect marine ecosystems.'
        },
        'Innovative Materials': {
            'description': 'Using cutting-edge sustainable materials and technologies.'
        },
        'Fair Trade': {
            'description': 'Ensures fair wages and good working conditions for producers.'
        },
        'Biodegradable': {
            'description': 'Capable of being decomposed by bacteria or other living organisms, reducing environmental impact.'
        },
        'Sustainable Harvest': {
            'description': 'Materials sourced using methods that maintain long-term ecosystem health and productivity.'
        }
    }
    return render_template('certifications.html', certifications=certification_info)


@app.route('/add-address', methods=['POST'])
@login_required
def add_address():
    user = USERS[session['user']]
    new_address = {
        'street': request.form.get('street'),
        'line2': request.form.get('line2'),
        'unit': request.form.get('unit'),
        'postal': request.form.get('postal')
    }
    
    if 'addresses' not in user:
        user['addresses'] = []
    
    user['addresses'].append(new_address)
    save_users_data()
    flash('Address added successfully!', 'success')
    return redirect(url_for('profile'))


@app.route('/edit-address/<int:address_id>', methods=['POST'])
@login_required
def edit_address(address_id):
    user = USERS[session['user']]
    if 0 <= address_id < len(user['addresses']):
        user['addresses'][address_id] = {
            'street': request.form.get('street'),
            'line2': request.form.get('line2'),
            'unit': request.form.get('unit'),
            'postal': request.form.get('postal')
        }
        save_users_data()
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error'})


@app.route('/delete-address/<int:address_id>', methods=['POST'])
@login_required
def delete_address(address_id):
    user = USERS[session['user']]
    if 0 <= address_id < len(user['addresses']):
        user['addresses'].pop(address_id)
        save_users_data()
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error'})


import random

@app.route('/debug/users')
def debug_users():
    if app.debug:
        return jsonify(USERS)
    return "Debug endpoint disabled"

@app.route('/debug/data')
def debug_data():
    if app.debug:
        try:
            with open('users_data.json', 'r') as f:
                data = json.load(f)
            return jsonify({
                'users': data,
                'current_user': session.get('user'),
                'current_user_data': data.get(session.get('user', ''), {})
            })
        except Exception as e:
            return jsonify({'error': str(e)})
    return "Debug endpoint disabled"

@app.route('/debug/check_data')
def check_data():
    if app.debug:
        email = session.get('user')
        return jsonify({
            'session_user': email,
            'user_data': USERS.get(email),
            'all_users': USERS,
            'cart': session.get('cart', [])
        })
    return "Debug endpoint disabled"

@app.route('/process-payment', methods=['POST'])
@login_required
def process_payment():
    try:
        email = session['user']
        user = USERS[email]
        address_index = int(request.form.get('shipping_address', 0))
        
        # Process the order
        process_order(user, address_index)
        
        # Clear cart after successful order
        session['cart'] = []
        
        flash('Order placed successfully!', 'success')
        return redirect(url_for('orders'))
        
    except Exception as e:
        flash(f'Error processing order: {str(e)}', 'error')
        return redirect(url_for('checkout'))

def process_order(user, address_index):
    if 0 <= address_index < len(user['addresses']):
        shipping_address = user['addresses'][address_index]
        cart_items = session.get('cart', [])
        
        if not cart_items:
            raise ValueError('Cart is empty')

        # Calculate totals and create item list
        total = 0
        item_list = []
        
        for item in cart_items:
            product = PRODUCTS.get(item['id'])
            if product:
                item_total = product['price'] * item['quantity']
                total += item_total
                item_list.append({
                    'id': item['id'],
                    'quantity': item['quantity'],
                    'name': product['name'],
                    'price': product['price'],
                    'total': item_total,
                    'image': product.get('image', 'placeholder.jpg')
                })

        # Create new order
        order = {
            'order_id': f'ORD-{datetime.now().strftime("%Y%m%d%H%M%S")}',
            'item_list': item_list,
            'total': total,
            'shipping_address': shipping_address,
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'status': 'Placed',
            'customer_name': f"{user['first_name']} {user['last_name']}"
        }
        
        # Initialize orders list if it doesn't exist
        if 'orders' not in user:
            user['orders'] = []
        
        # Add order to user's orders
        user['orders'].insert(0, order)
        save_users_data()
        
        # Clear cart
        session['cart'] = []

if __name__ == '__main__':
    random_port = random.randint(5000, 9999)
    app.run(debug=True, port=random_port)