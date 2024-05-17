from flask import render_template,url_for, flash, redirect, request
from flask_mail import Message
from facial import app,bcrypt, db, mail
from facial.form import RegistrationForm,LoginForm, RequestResetForm, ResetPasswordForm, UpdateAccountForm, UpdatePasswordForm, ContactForm, BuyForm, SellForm
from facial.models import User, Consumer, Producer
from flask_login import login_user, current_user, logout_user, login_required

forgot = False

@app.route('/home')
@app.route('/')
def home():
    # consumer = Consumer.query.first()
    consumers = Consumer.query.order_by(Consumer.id).all()

    return render_template('index.html',title='Home',consumers=consumers)
    

@app.route('/login',methods=('GET','POST'))
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user)
            flash(f'Welcome back {user.username}!','success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login failed! Invalid credentials!','fail')
    return render_template('login.html',title='Log In',forgot = True,form=form)

@app.route('/contact',methods=('GET','POST'))
def contact():
    form = ContactForm()
    return render_template('contact.html',form=form)

@app.route('/buy',methods=('GET','POST'))
def buy():
    form = BuyForm()
    print('on buy route')

    # if form.validate_on_submit():
    if request.method == 'POST' and form.validate():
        print('validated form')
        try:
            consumers =  Consumer(email=form.email.data,
                                    phone_number=form.phone_number.data,
                                    quantity=form.quantity.data,
                                    postal_code=form.postal_code.data,
                                    user_id=current_user.get_id())
            db.session.add(consumers)
            db.session.commit()
            return redirect('home')
        except Exception as e:
            print(e)
            flash('an error occurred','danger')

        flash(f'Operation Successful','success')
        # return redirect('home')
    return render_template('buy.html',form=form)

@app.route('/sell',methods=('GET','POST'))
def sell():
    form = SellForm()
    if form.validate_on_submit():
        producers =  Producer(full_name=form.full_name.data,email=form.email.data,phone_number=form.phone_number.data,postal_code=form.postal_code.data,user_id=current_user.get_id())
        db.session.add(producers)
        db.session.commit()
        flash(f'Operation Successful','success')  
        return redirect('home')
    return render_template('sell.html',form=form)

@app.route('/register',methods=('GET','POST'))
@app.route('/sign-up',methods=('GET','POST'))
@app.route('/signup',methods=('GET','POST'))
def register():
    if  current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password=bcrypt.generate_password_hash(form.password.data)
        user = User(username=form.username.data,email=form.email.data,password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created for {form.username.data}!','success')
        return redirect(url_for('login'))
    return render_template('sign-up.html',title='Sign Up',forgot = False,form=form)

def print_user_data(form):
    if request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

@app.route('/account',methods=['POST'])
@app.route('/settings',methods=['POST'])
@app.route('/profile',methods=['POST'])
def delete_account():
    user = User.query.first_or_404(current_user.username)
    db.session.delete(user)
    db.session.commit()
    flash('Your Account has been deleted successfully!','success')
    return redirect(url_for('home'))

@app.route('/account',methods=('GET','POST'))
@app.route('/settings',methods=('GET','POST'))
@app.route('/profile',methods=('GET','POST'))
@login_required
def account():
    form = UpdateAccountForm()
    print_user_data(form)
    password_form = UpdatePasswordForm()
    if form.validate_on_submit():    
            if current_user.username==form.username.data and current_user.email==form.email.data:
                return redirect(url_for('account'))
            else:
                current_user.username = form.username.data
                current_user.email = form.email.data
                db.session.commit()
                flash("Your account has been updated successfully!",'success')
                print("test if in profile")
                return redirect(url_for('account'))

    if password_form.validate_on_submit():    
        hashed_password=bcrypt.generate_password_hash(password_form.password.data)
        current_user.password = hashed_password
        db.session.commit()
        flash("Your account has been updated successfully!",'success')
        print("test if in password")

        return redirect(url_for('account'))
    else:
        print("test else in password")
        render_template('account.html',title='Profile',form=form,password_form=password_form)


    return render_template('account.html',title='Profile',form=form,password_form=password_form)    

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',sender='noreply@demo.com',recipients=[user.email])

    msg.body = f'''Visit the following link to reset your password:
{url_for('reset_token',token=token,_external= True)}
If you did not make this request then simply ignore this email and no changes will be made.
     '''
    mail.send(msg)

@app.route('/reset_password',methods=('GET','POST'))
def request_reset():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent to you with the reset instructions!','info')
        return redirect(url_for('login'))
    return render_template('request_reset.html',title='Reset Password',form=form)

@app.route('/reset_password/<token>',methods=('GET','POST'))
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    user = User.verify_reset_token(token)
    if not user:
        flash('Invalid or expired token! Please re-try again.','warning')
        return redirect(url_for('request_reset'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Password successfully updated! You can now log in!','success')
        return redirect(url_for('login'))
    return render_template('reset_token.html',title='Reset Password',form=form)

#custom error handling pages
@app.errorhandler(404)
def error_404(error):
    return render_template('errors/404.html',title='404'),404

@app.errorhandler(401)
def error_403(error):
    return render_template('errors/401.html',title='401'),401


@app.errorhandler(403)
def error_403(error):
    return render_template('errors/403.html',title='403'),403

@app.errorhandler(500)
def error_500(error):
    return render_template('errors/500.html',title='500'),500



@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))
