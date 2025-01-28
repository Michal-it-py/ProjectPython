import os
from flask import Flask,render_template,request,redirect, url_for
from flask_security import Security, UserMixin, RoleMixin, SQLAlchemyUserDatastore,current_user,login_required
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sell.db'
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY','lalalala')
app.config['SECURITY_PASSWORD_SALT'] = os.environ.get('SECURITY_PASSWORD_SALT','solsol')
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_SEND_REGISTER_EMAIL'] = False

db = SQLAlchemy(app)

roles_user = db.Table(
    'roles_users',
    db.Column('user_id',db.ForeignKey('user.id')),
    db.Column('role_id',db.ForeignKey('role.id')),
)

class Item(db.Model):
    id=db.Column(db.Integer, primary_key = True)
    tittle = db.Column(db.String(100), nullable = False)
    description = db.Column(db.Text, nullable = False)
    price = db.Column(db.Float, nullable = False)
    user_id = db.Column(db.String(255), db.ForeignKey('user.fs_uniquifier'))
    category_id = db.Column(db.Integer,db.ForeignKey('category.id'))
    image_path = db.Column(db.String, nullable = True)

    category = db.relationship('Category', backref = db.backref('items'))

class Category(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), nullable=False)
    
class Role(db.Model,RoleMixin):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(32), unique = True, nullable = False)
    description = db.Column(db.String(128))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(255), unique = True, nullable = False)
    password = db.Column(db.String(255), nullable = False)
    active = db.Column(db.Boolean, default = True)
    confirmed_at = db.Column(db.DateTime)
    fs_uniquifier = db.Column(db.String(255), unique = True, nullable = False)
    roles = db.relationship('Role',secondary = roles_user, backref = db.backref('users'))

    def __init__(self,**kwargs) -> None:  
        super().__init__(**kwargs)
        if not self.fs_uniquifier:
            import uuid
            self.fs_uniquifier = str(uuid.uuid4())

user_datastore = SQLAlchemyUserDatastore(db,User,Role)
security = Security(app, user_datastore)


@app.route("/")
@login_required  
def home():
    return render_template("main.html")

@app.route("/index", methods = ['GET', 'POST'])
@login_required
def index():

    items = Item.query.filter_by(user_id = current_user.get_id())
    categories = Category.query.all() 
    return render_template("add.html",items=items,categories=categories)

@app.route("/add", methods = ['POST'])
@login_required  
def add():
    if(request.method =='POST'):
        tittle = request.form["item_text"]
        description = request.form["description_text"]
        price = float(request.form["price_tekst"])
        user_id = current_user.get_id()
        category_id=int(request.form["category_name"])
        img = request.files.get("img")
        path = None

        if img:
            img.save(os.path.join("static/userimages", img.filename))
            path = os.path.join("static/userimages", img.filename)

        new_item = Item(
            tittle = request.form["item_text"],
            description = request.form["description_text"],
            price = request.form["price_tekst"],
            user_id = current_user.get_id(),
            category_id=request.form["category_name"],
            image_path = path
        )   
    
        db.session.add(new_item)
        db.session.commit()


        return redirect("/index")


@app.route("/lookfor")
def look():
    category_id = request.args.get("category_id")  # Pobierz kategorię z zapytania
    if category_id:
        items = Item.query.filter_by(category_id=category_id).all()
    else:
        items = Item.query.all()

    categories = Category.query.all()
    return render_template("lookfor.html", items=items, categories=categories)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        
        if Category.query.count() == 0:
            db.session.add(Category(name="Elektronika"))
            db.session.add(Category(name="Ubrania"))
            db.session.add(Category(name="Dom"))
            db.session.commit()

    app.run(host ='127.0.0.1',port=5001, debug = True)

