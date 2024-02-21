from flask import  Flask,redirect,url_for,render_template,request, flash, session
from flask import current_app as app
from database import db
from passlib.hash import pbkdf2_sha256 as passhash
from models import db,User,Manager,Section,Product
from flask_migrate import Migrate
import os



def create_app():
    app=Flask(__name__)
    app.config['SECRET_KEY'] = "SECRETKEY"
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.sqlite3"
    db.init_app(app)
    # Initialize the Migrate object with your app and db
    migrate = Migrate(app, db)
    migrate.init_app(app, db)
    app.app_context().push()

    return app
app = create_app()

def save_uploaded_image(file, filename):
    file.save(os.path.join(app.root_path, 'static', filename))


@app.route('/',methods=['GET','POST'])
def home():
    if 'user' in session:
        username = session.get('user')
        return redirect("/user_home="+username)
    else:
        return render_template("Userlogin.html") 

@app.route('/registerUser', methods = ['GET', 'POST'])
def registerUser(): 
    if request.method == 'POST':
        username = request.form['username']
        passa = request.form['password']
        password = passhash.hash(passa)
        address = request.form['address']
        mobile = request.form['mobile']

        existing_user = User.query.filter_by(username = username).first()
        if existing_user:
            flash('Error: User already exists!', 'error')

            return render_template('registerUser.html', error = 'Username already exist')

        new_user = User(username = username, address = address, mobile = mobile, password = password )
        db.session.add(new_user)
        db.session.commit()

        return render_template("Userlogin.html")
    
    


    return render_template('registerUser.html')

@app.route('/Userlogin', methods = ['GET', 'POST'])
def Userlogin():
    if request.method == "POST":
        print("in post")
        username = request.form['username']
        password = request.form['password']
    
        user = User.query.filter_by(username = username).first()
        if user is None:
            flash('Invalid username or password!', 'error')
            return render_template('Userlogin.html')
        if not passhash.verify(password, user.password):
            flash('Invalid username or password!', 'error')
            return render_template('Userlogin.html')
        session['user'] = username
        return redirect("/user_home="+username) 
        
    return render_template('Userlogin.html')

@app.route('/manager_login', methods = ['GET', 'POST'])
def manager_login():
    if request.method == "POST":
        managername = request.form['managername']
        password = request.form['password']
        manager = Manager.query.filter_by(managername = managername).first()
        if manager is None:
            flash("Manager is NOT registered. PLease register first", 'error')
            return render_template('manager_login.html')
        if not passhash.verify(password, manager.password):
            flash("Incorrect Password !!", 'error')
            return render_template('manager_login.html')
        print("session is allocating")
        session['manager'] = managername
        return redirect('/manager_page='+managername)

    return render_template('manager_login.html')






@app.route('/manager_register', methods = ['GET', "POST"])
def manager_register():
    if request.method == "POST":
        managername = request.form['managername']
        store = request.form['store']
        passs= request.form['password']
        password = passhash.hash(passs)
        existing_manager = Manager.query.filter_by(managername = managername).first()
        if existing_manager:
            flash('Error: User already exists!', 'error')

            return render_template('manager_register.html', error = "Manager Name Already Exist")
        
        new_manager = Manager(managername = managername, store = store, password = password)
        db.session.add(new_manager)
        db.session.commit()
        return redirect('/manager_login')

    return render_template('manager_register.html')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    if 'manager' in session:
        session.pop('manager', None)
    if 'user' in session:
        session.pop('user', None)
    return redirect(url_for('Userlogin'))




@app.route('/user_home=<username>', methods = ['GET', 'POST'])
def user_home(username):
    if 'user' not in session or session['user'] != username:
        return redirect(url_for('Userlogin'))
    user = User.query.filter_by(username = username).first()
    sections = Section.query.all()

    products_by_section = {}
    for section in sections:
        products = Product.query.filter_by(section_id=section.id).all()
        products_by_section[section] = products

    return render_template('user_home.html', products_by_section=products_by_section, user = user, sections = sections)  


@app.route('/manager_page=<managername>', methods = ['GET', 'POST'])
def manager_page(managername):
    if 'manager' not in session or session['manager'] != managername:
        return redirect(url_for('manager_login'))

    manager = Manager.query.filter_by(managername = managername).first()

    sections = Section.query.all()
    products = Product.query.filter_by(manager_id=manager.id).all()


    return render_template('manager.html', sections = sections, products = products, manager = manager)


@app.route("/add_sec", methods = ["POST"])
def add_sec():
    if 'manager' in session:
        return render_template('add_section.html')
        

@app.route("/edit_sec", methods = ["POST"])
def edit_sec():
    if 'manager' in session:
        sections = Section.query.all()

        return render_template('edit_section.html', sections =sections)
    
@app.route("/del_sec", methods = ["POST"])
def del_sec():
    if 'manager' in session:
        sections = Section.query.all()

        return render_template('confirm_delete_section.html', sections = sections)

@app.route("/add_section", methods = ["POST"])
def add_section():
    if 'manager' not in session:
        return render_template("manager_login.html")
    if request.method == 'POST':
        section_name = request.form['section_name']

        # Check if the section with the given name already exists
        existing_section = Section.query.filter_by(name=section_name).first()
        if existing_section:
            flash('Section with the same name already exists!', 'error')
        else:
            new_section = Section(name=section_name)
            db.session.add(new_section)
            db.session.commit()
            flash('Section added successfully!', 'success')

    return render_template('add_section.html')

@app.route('/edit_section', methods=['GET', 'POST'])
def edit_section():
    if 'manager' not in session:
        return render_template("manager_login.html")

    all_sections = Section.query.all()

    if request.method == 'POST':
        section_id = int(request.form['section_id'])
        new_section_name = request.form['new_section_name']

        section = Section.query.get(section_id)

        if section:
            existing_section = Section.query.filter_by(name=new_section_name).first()
            if existing_section and existing_section.id != section_id:
                flash('Section with the same name already exists!', 'error')
            else:
                section.name = new_section_name
                db.session.commit()
                flash('Section updated successfully!', 'success')
        else:
            flash('Invalid section selected!', 'error')
        return redirect(url_for('manager_page', managername=session['manager']))

    return render_template('edit_section.html', all_sections=all_sections, section=None)

@app.route('/confirm_delete_section', methods=['GET', 'POST'])
def confirm_delete_section():
    if 'manager' not in session:
        return render_template("manager_login.html")

    all_sections = Section.query.all()

    if request.method == 'POST':
        section_id = int(request.form['section_id'])

        section = Section.query.get(section_id)

        if section:
            db.session.delete(section)
            db.session.commit()
            flash('Section deleted successfully!', 'success')
        else:
            flash('Invalid section selected!', 'error')
        return redirect(url_for('manager_page', managername=session['manager']))


    return render_template('confirm_delete_section.html', all_sections=all_sections)



@app.route('/add_product', methods=['POST'])
def add_product():
    if request.method == 'POST':
        product_name = request.form['product_name']
        product_price = float(request.form['product_price'])
        product_category = int(request.form['product_category'])
        stock = int(request.form['stock'])
        product_description = request.form['product_description']

        managername = session.get('manager')
        manager = Manager.query.filter_by(managername=managername).first()
        if manager is None:
            return render_template('manager_not_found.html')

        new_product = Product(
            name=product_name,
            price=product_price,
            stock=stock,
            section_id=product_category,
            manager_id=manager.id,
            description=product_description
        )
        db.session.add(new_product)
        db.session.commit()

        flash("Product Added Successfully !!", "success")

        product_image = request.files['product_image']
        if product_image:
            image_filename = str(new_product.id) + ".png"
            save_uploaded_image(product_image, image_filename)

    return redirect(url_for('manager_page', managername=managername))


@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    sections = Section.query.all()


    if request.method == 'POST':
        product.name = request.form['product_name']
        product.price = float(request.form['product_price'])
        product.stock = int(request.form['stock'])
        product.description = request.form['product_description']
        product.session_id = int(request.form['product_category'])
        db.session.commit()

        return redirect(url_for('manager_page', managername=session['manager']))

    return render_template('edit_product.html', product=product,sections=sections)


@app.route('/confirm_delete_product/<int:product_id>', methods=['GET', 'POST'])
def confirm_delete_product(product_id):
    product = Product.query.get_or_404(product_id)

    if request.method == 'POST':
        db.session.delete(product)
        db.session.commit()

        return redirect(url_for('manager_page', managername=session['manager']))

    return render_template('confirm_delete_product.html', product=product)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if 'user' not in session:
        flash('Please log in first to add items to your cart.', 'error')
        return redirect(url_for('Userlogin'))

    if request.method == 'POST':
        product_id = int(request.form['product_id'])
        user = User.query.filter_by(username=session['user']).first()
        if not user:
            flash('User not found!', 'error')
            return redirect(url_for('Userlogin'))

        product = Product.query.get(product_id)
        if not product:
            flash('Product not found!', 'error')
            return redirect(url_for('user_home', username=session['user']))

        cart = user.cart
        products_in_cart = cart.cart_products

        quantity = int(request.form.get('quantity', 1))

        if quantity < 1:
            flash('Invalid quantity! Please select at least 1 item.', 'error')
            return redirect(url_for('user_home', username=session['user']))
        if product.stock < 1:
            flash(f'{product.name} is out of stock!', 'danger')
            return redirect(url_for('user_home', username=session['user']))

        if product in products_in_cart:
            product_in_cart = [p for p in products_in_cart if p.id == product.id][0]
            product_in_cart.quantity += quantity
            db.session.commit()
            flash(f'Updated quantity of {product.name} in your cart!', 'info')
        else:
            cart.cart_products.append(product)
            product.quantity = quantity

            db.session.commit()
            flash(f'Added {quantity} {product.name}(s) to your cart!', 'success')


        return redirect(url_for('user_home', username=session['user']))

    flash('Invalid request!', 'error')
    return redirect(url_for('user_home', username=session['user']))



  

@app.route('/cart', methods=['GET'])
def cart():
    if 'user' not in session:
        flash('Please log in first to view your cart.', 'error')
        return redirect(url_for('Userlogin'))

    user = User.query.filter_by(username=session['user']).first()
    first = False

    total_price = sum(product.price * product.quantity for product in user.cart.cart_products)
    if user.first_order:
        first = total_price *0.2 
        total_price *= 0.8

    return render_template('cart.html', user=user, total_price = total_price, first = first)


@app.route('/remove_product_from_cart/<int:product_id>', methods=['GET'])
def remove_product_from_cart(product_id):
    if 'user' not in session:
        flash('Please log in first to view your cart.', 'error')
        return redirect(url_for('Userlogin'))

    user = User.query.filter_by(username=session['user']).first()
    product = Product.query.get_or_404(product_id)

    if product in user.cart.cart_products:
        product_in_cart = [p for p in user.cart.cart_products if p.id == product.id][0]
        user.cart.cart_products.remove(product)

        product_in_cart.quantity = 0
        db.session.commit()
        flash(f'Removed {product.name} from your cart!', 'info')

    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET','POST'])
def checkout():
    user = User.query.filter_by(username=session['user']).first()

    if not user.cart.cart_products:
            flash('Your cart is empty!', 'danger')
            return redirect(url_for('cart'))
    
    total_price = sum(product.price * product.quantity for product in user.cart.cart_products)

    first = False
    if user.first_order:
        first = total_price  *0.2
        total_price *= 0.8

           



    if request.method == 'POST':
        user = User.query.filter_by(username=session['user']).first()
        if not user:
            flash('User not found!', 'error')
            return redirect(url_for('Userlogin'))

        total_price = sum(product.price * product.quantity for product in user.cart.cart_products)
        if not user.cart.cart_products:
            flash('Your cart is empty!', 'error')
            return redirect(url_for('cart'))

        products_in_cart = user.cart.cart_products.copy()

        for product in products_in_cart:
            manager = product.manager

            if manager:
                if product.stock >= product.quantity:
                    product.stock -= product.quantity

                else:
                    flash(f'Insufficient stock for {product.name}!', 'error')
        for product in user.cart.cart_products:
            product.frequency += product.quantity

        db.session.commit()

        user.cart.cart_products.clear()
        user.first_order = False
        db.session.commit()
        flash('Order placed successfully!', 'success')
        return redirect(url_for('user_home', username=session['user']))



    return render_template('checkout.html', total_price=total_price, user = user, first = first)


@app.route('/search_products', methods=['POST'])
def search_products():
    if 'user' not in session:
        flash('Please log in first to search for products.', 'error')
        return redirect(url_for('Userlogin'))

    section_id = int(request.form.get('section_id', 0))
    section = Section.query.get(section_id)

    if section:
        products = section.product 
        return render_template('products_by_category.html', section=section, products=products)

    return redirect(url_for('user_home', username=session['user']))

@app.route('/filter_products', methods=['POST'])
def filter_products():
    if 'user' not in session:
        flash('Please log in first to filter products.', 'error')
        return redirect(url_for('Userlogin'))

    section_id = int(request.form.get('section_id', 0))
    section = Section.query.get(section_id)

    price_range = request.form.get('price_range', '0-100')
    min_price, max_price = map(float, price_range.split('-'))

    products = Product.query.filter(Product.price.between(min_price, max_price))
    if section:
        products = products.filter_by(section_id=section_id)

    return render_template('filter_products.html', section=section, products=products)

@app.route('/search_products_by_name', methods=['POST'])
def search_products_by_name():
    if 'user' not in session:
        flash('Please log in first to search for products.', 'error')
        return redirect(url_for('Userlogin'))

    search_name = request.form.get('search_name', '')

    products = Product.query

    if search_name:
        products = products.filter(Product.name.ilike(f"%{search_name}%"))

    return render_template('search_results.html', search_name=search_name, products=products)

@app.route('/frequently_bought', methods=['GET'])
def frequently_bought():
    most_frequent_products = Product.query.order_by(Product.frequency.desc()).limit(5).all()

    return render_template('frequently_bought.html', products=most_frequent_products)




if __name__ == '__main__':
    db.create_all()
    app.run(port=5000,debug=True)