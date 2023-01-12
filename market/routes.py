from market import app
from flask import render_template, redirect, url_for, flash, request
from market.models import Item, User
from market.forms import RegisterForm, LoginForm,PurchaseItemForm, SellItemForm
from market import db
from flask_login import login_user, logout_user, login_required, current_user


@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')


@app.route('/market', methods=['GET', 'POST'])
@login_required
def market_page():
    sell_item_form = SellItemForm()
    purchase_form = PurchaseItemForm()
    print(request.method)
    if request.method == "POST":
        purchased_item = request.form.get('purchased_item')
        p_item_object = Item.query.filter_by(name=purchased_item).first()
        if p_item_object:
            if current_user.can_purchase(p_item_object):
                p_item_object.buy_item(current_user)
                
                flash(f"Congratulations!, you have purchased {p_item_object.name} for price {p_item_object.price}", category="success")
            else:
                flash(f"Sorry, you don't have enough money to purchase {p_item_object.name}", category="danger")

        sold_item = request.form.get('sold_item')
        s_item_object = Item.query.filter_by(name=sold_item).first()
        if s_item_object:
            if current_user.can_sell(s_item_object):
                s_item_object.sell_item(current_user)
                flash(f"Congratulations!, you have sold {s_item_object.name} for price {s_item_object.price}", category="success")
            else:
                flash(f"Something went wrong!!", category="danger")
        return redirect(url_for('market_page'))


    if request.method == "GET":
        items = Item.query.filter_by(owner=None)
        owned_items = Item.query.filter_by(owner=current_user.id)
        return render_template('market.html', items=items, purchase_form=purchase_form, owned_items=owned_items, sell_item_form=sell_item_form)


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data, email=form.email.data,password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f'Account Created Successfully! You are logged in as: {user_to_create.username}', category="success")
        return redirect(url_for('market_page'))
        
    if form.errors != {}:
        for error in form.errors.values():
            flash(f"There is an error with creating a user: {error}", category='danger')

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(attempted_password=form.password.data):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category="success")
            return redirect(url_for('market_page'))
        else:
            flash(f'User name and password do not match!', category='danger')

    return render_template('login.html', form=form)


@app.route('/logout')
def logout_page():
    logout_user()
    flash(f'You are currently logged out!', category='info')
    return redirect(url_for('home_page'))


