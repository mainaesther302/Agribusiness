# from itsdangerous import TimedJSONWebSignatureSerializer as  Serializer
from facial import db
from facial import db,login_manager, app
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(15),unique=True,nullable=False)
    email = db.Column(db.String(120),unique=True,nullable=False)
   # image_file = db.Column(db.String(20),default='default.jpg',nullable=False)
    password = db.Column(db.String(60),nullable=False)
    consumers = db.relationship('Consumer',lazy=True)
    producers = db.relationship('Producer',lazy=True)

    # Generate a unique password reset token
    def get_reset_token(self,expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id':self.id}).decode('utf-8')

    # Validate the token is not invalid or expired
    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self) -> str:
        return f"User('{self.username}','{self.email}')"

class Consumer(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    email = db.Column(db.String(120),unique=True,nullable=False)
    phone_number = db.Column(db.Integer,unique=True,nullable=False)
    quantity = db.Column(db.Integer,nullable=False)
    postal_code = db.Column(db.Integer,unique=True,nullable=False)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    def __repr__(self) -> str:
        return f"Consumer('{self.email}','{self.phone_number}')"


class Producer(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    full_name = db.Column(db.String(45),unique=True,nullable=False)
    email = db.Column(db.String(120),unique=True,nullable=False)
    phone_number = db.Column(db.Integer,unique=True,nullable=False)
    postal_code = db.Column(db.Integer,unique=True,nullable=False)
    product_name = db.Column(db.String(30),nullable=False)
    product_description = db.Column(db.String(100),nullable=False)
    price = db.Column(db.Integer,nullable=False)
    quantity = db.Column(db.Integer,nullable=False)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    def __repr__(self) -> str:
        return f"Producer('{self.full_name}','{self.email}')"
