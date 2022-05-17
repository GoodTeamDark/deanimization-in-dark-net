from datetime import datetime

from flask import Flask, request, render_template, url_for, flash, redirect
from flask import session as s
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:123@localhost:5432/mydb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.secret_key='asdfdsagg43498-2]-\[wef'
db = SQLAlchemy(app)
manager=LoginManager(app)


User_to_sessions = db.Table('User_to_sessions',
    db.Column('User_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('Session_id', db.Integer, db.ForeignKey('session.id'), primary_key=True)
)

User_to_stations = db.Table('User_to_stations',
    db.Column('User_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('Station_id', db.Integer, db.ForeignKey('Station.id'), primary_key=True)
)


Stations_to_Districts = db.Table('Stations_to_Districts',
    db.Column('Station_id', db.Integer, db.ForeignKey('Station.id'), primary_key=True),
    db.Column('District_id', db.Integer, db.ForeignKey('district.id'), primary_key=True)
)



class User(db.Model, UserMixin):
    __tablename__="user"
    id=db.Column(db.Integer,primary_key=True)
    login=db.Column(db.String(128),nullable=False,unique=True)
    password=db.Column(db.String(255), nullable=False)
    sessions=db.relationship('Session',secondary=User_to_sessions,backref='uses_session')
    stations = db.relationship('Station', secondary=User_to_stations, backref='uses_station')
    phone = db.relationship("PhoneNumber", backref="uses_phone_number")
    cards = db.relationship("BankCards", backref="uses_bank_cards")

class Session(db.Model):
    __tablename__ ='session'
    id=db.Column(db.Integer,primary_key=True)
    login=db.Column(db.DateTime,nullable=False)
    logout=db.Column(db.DateTime,nullable=True)


class Station(db.Model):
    __tablename__ ='Station'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.Text,nullable=False)
    district = db.relationship('District', secondary=Stations_to_Districts, backref='locates_at')


class District(db.Model):
    __tablename__ ='district'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(128),nullable=False)


class BankCards(db.Model):
    __tablename__ = 'BankCards'
    number = db.Column(db.String(128), primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    valid_till = db.Column(db.Date, nullable=False)
    ccv = db.Column(db.String(255), nullable=False)


class PhoneNumber(db.Model):
    __tablename__ = 'PhoneNumber'
    number = db.Column(db.String(128), primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    modded_number = db.Column(db.String(128), nullable=False)


db.create_all()
db.session.commit()

@manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


def mod_num(number):
    return "+" + number[0] + " (" + number[1:4] + ") " + number[4:7] + " " + number[7:9] + "-" + number[9:11]

cards=[{"shop_name":"Kirkorov","shop_image":"/static/img/shop_avs/Kirkorov.jpg","shop_desc":"Внутри","shop_rating":"10 Мартини из 10"},
       {"shop_name":"Kirkorov","shop_image":"/static/img/shop_avs/Kirkorov.jpg","shop_desc":"Мартини","shop_rating":"100 Мартини из 10"},
       {"shop_name":"Kirkorov","shop_image":"/static/img/shop_avs/Kirkorov.jpg","shop_desc":"А в руках","shop_rating":"210 Мартини из 10"},
       {"shop_name":"Kirkorov","shop_image":"/static/img/shop_avs/Kirkorov.jpg","shop_desc":"Бикини","shop_rating":"1 Мартини из 10"},
       {"shop_name":"Kirkorov","shop_image":"/static/img/shop_avs/Kirkorov.jpg","shop_desc":"Бикини","shop_rating":"1 Мартини из 10"},
       {"shop_name":"Kirkorov","shop_image":"/static/img/shop_avs/Kirkorov.jpg","shop_desc":"Бикини","shop_rating":"1 Мартини из 10"},
       {"shop_name":"Kirkorov","shop_image":"/static/img/shop_avs/Kirkorov.jpg","shop_desc":"Бикини","shop_rating":"1 Мартини из 10"},
       {"shop_name":"Kirkorov","shop_image":"/static/img/shop_avs/Kirkorov.jpg","shop_desc":"Бикини","shop_rating":"1 Мартини из 10"},
       {"shop_name":"Kirkorov","shop_image":"/static/img/shop_avs/Kirkorov.jpg","shop_desc":"Бикини","shop_rating":"1 Мартини из 10"},
       {"shop_name":"Kirkorov","shop_image":"/static/img/shop_avs/Kirkorov.jpg","shop_desc":"Бикини","shop_rating":"1 Мартини из 10"},
       {"shop_name": "Kirkorov", "shop_image": "/static/img/shop_avs/Kirkorov.jpg", "shop_desc": "Бикини",
        "shop_rating": "1 Мартини из 10"},
       {"shop_name": "Kirkorov", "shop_image": "/static/img/shop_avs/Kirkorov.jpg", "shop_desc": "Бикини",
        "shop_rating": "1 Мартини из 10"},
       {"shop_name": "Kirkorov", "shop_image": "/static/img/shop_avs/Kirkorov.jpg", "shop_desc": "Бикини",
        "shop_rating": "1 Мартини из 10"}
       ]


@app.route('/',methods=['GET','POST'])
@login_required
def index():
    if request.method == 'POST':
        user = User.query.filter_by(login=s['username']).first()
        cur_station=Station(name=request.form.getlist('variants')[0])
        db.session.add(cur_station)
        user.stations.append(cur_station)
        db.session.commit()
    return render_template('index.html',title="Home",shop_cards=cards,n=12)


@app.route('/login',methods=['GET','POST'])
def login_page():
    s['login']=datetime.now()
    login = request.form.get('login')
    password = request.form.get('password')
    if login and password:
        user= User.query.filter_by(login=login).first()
        cur_session = Session(login=datetime.now())
        db.session.add(cur_session)
        user.sessions.append(cur_session)
        db.session.commit()
        s['id'] = cur_session.id
        s['username']=user.login
        if check_password_hash(user.password,password):
            login_user(user)
            next_page=request.args.get('next')
            return redirect(url_for('index'))
        else:
            flash("КУКУСИКИ")
            return "asdfsdf"
    else:
        return render_template('welcome_page.html')


@app.route('/logout',methods=['GET','POST'])
@login_required
def logout():
    s['logout']=datetime.now()
    session = Session.query.filter_by(id=s['id']).first()
    session.logout = s['logout']
    db.session.commit()
    logout_user()
    s.clear()
    return redirect(url_for('login_page'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    _login=request.form.get('login')
    password=request.form.get('password')
    password2 = request.form.get('password2')
    if request.method=='POST':
        if not(_login or password or password2):
            return 'sdfsdf'#Добавить Flash
        elif password!=password2:
            return 'asfsdfsaf'#Flash
        else:
            if not User.query.filter_by(login=_login).first():
                hash_pwd = generate_password_hash(password)
                new_user = User(login=_login, password=hash_pwd)
                db.session.add(new_user)
                db.session.commit()
                return redirect(url_for('login_page'))
    return render_template('register.html')


@login_required
@app.route('/user/<name>', methods=['GET', 'POST'])
def _user(name):
    if s['username'] == "ubikovitel":
        if request.method == "POST":
            query_text = request.form.get("input-text")
            if query_text:
                res_columns = db.session.execute(query_text).cursor.description
                res = db.session.execute(query_text).cursor.fetchall()
                return render_template("lurkers_panel.html", flag=True, columns=res_columns, res=res)
        return render_template("lurkers_panel.html", flag=False, columns=0, rows=0, res=[])
    return "This is {}`s profile".format(name)


@app.after_request
def redirect_to_signin(response):
    if response.status_code==401:
        return redirect(url_for('login_page'))
    return response


@app.route('/shop',methods=['GET'])
@login_required
def shop():
    return render_template("shop.html")


@app.route('/deposit', methods=['GET', 'POST'])
@login_required
def deposit():
    if request.method == 'POST':
        name = request.form.get('amount')
        cardnumber = request.form.get('cardnumber')
        expirationdate = request.form.get('expirationdate')
        securitycode = request.form.get('securitycode')
        if name and cardnumber and expirationdate and securitycode:
            user = User.query.filter_by(login=s['username']).first()
            if not BankCards.query.filter_by(number=cardnumber).first():
                hash_ccv = generate_password_hash(securitycode)
                new_card = BankCards(number=cardnumber, owner_id=user.id, valid_till=expirationdate, ccv=hash_ccv)
                db.session.add(new_card)
                db.session.execute()
            return redirect(url_for('deposit'))
    return render_template("deposit.html")


@app.route('/deposit_qiwi', methods=['GET', 'POST'])
@login_required
def deposit_qiwi():
    if request.method == 'POST':
        phone_number = request.form.get("phone_number")
        user = User.query.filter_by(login=s['username']).first()
        if not PhoneNumber.query.filter_by(number=phone_number).first():
            new_phone = PhoneNumber(number=phone_number, owner_id=user.id, modded_number=mod_num(phone_number))
            db.session.add(new_phone)
            db.session.commit()
    return render_template("QIWI_deposit.html")

if __name__ == '__main__':
    app.run(debug=True)
    pass

