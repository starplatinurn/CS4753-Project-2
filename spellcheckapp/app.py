from flask import Flask,render_template,request,redirect,flash,url_for,session
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime
from sqlalchemy import desc
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.secret_key = b'few9i04tjjvp0:id9022'
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
csrf = CSRFProtect(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    twofa = db.Column(db.String(128), nullable=False)
    pword_hash = db.Column(db.String(128))
    def __repr__(self):
        return '<User %r>' % self.username

class Query(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(128), nullable=False)
    results = db.Column(db.String(128), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    #user = db.relationship('User',backref=db.backref('queries', lazy=True))
    def __repr__(self):
        return '<Query %r>' % self.id

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(128), nullable=False, default='N/A')
    logout = db.Column(db.String(128), nullable=False, default='N/A')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    def __repr__(self):
        return '<Log %r>' % self.id

if User.query.filter_by(username='admin').first() is None:
    db.session.add(User(username='admin', twofa='12345678901', pword_hash=bcrypt.generate_password_hash('Administrator@1')))
    db.session.commit()

@app.route('/')
def index():
    if 'uname' in session:
        return redirect(url_for('spell_check'))
    return render_template('index.html')

@app.route('/login', methods = ['GET','POST'])
def login():
    if 'uname' in session:
        return redirect(url_for('spell_check'))
    result = "unknown"
    if request.method == 'POST':
        uname = request.form['uname']
        pword = request.form['pword']
        twofa = request.form['2fa']
        if User.query.filter_by(username=uname).first() is None:
            result = "Incorrect username or password"
        elif not bcrypt.check_password_hash(User.query.filter_by(username=uname).first().pword_hash, pword):
            result = "Incorrect username or password"
        else:
            if User.query.filter_by(username=uname).first().twofa == twofa:
                result = "success"
                session['uname'] = uname
                db.session.add(Log(login = str(datetime.utcnow()), user_id = User.query.filter_by(username=session['uname']).first().id))
                db.session.commit()
            else:
                result = "Two-factor authentication failure"
    return render_template('login.html', result = result)

@app.route('/register', methods = ['GET','POST'])
def register():
    if 'uname' in session:
        return redirect(url_for('spell_check'))
    if request.method == 'POST':
        uname = request.form['uname']
        pword = request.form['pword']
        twofa = request.form['2fa']
        if User.query.filter_by(username=uname).first() is not None:
            return render_template('regresult.html', success = "failure")
        else:
            db.session.add(User(username=uname, twofa=twofa, pword_hash=bcrypt.generate_password_hash(pword)))
            db.session.commit()
            return render_template('regresult.html', success = "success")
    return render_template('register.html')

@app.route('/spell_check', methods = ['GET','POST'])
def spell_check():
    if 'uname' in session:
        if request.method == 'POST':
            inputtext = request.form['inputtext']
            with open('input.txt', 'w') as input:
                input.write(inputtext)
            #make sure terminal is in right dir (and not one above) when running cmd
            cmd = './a.out input.txt wordlist.txt'
            out = os.popen(cmd).read()
            res = ', '.join(out.split())
            db.session.add(Query(text=inputtext, results=res, user_id=User.query.filter_by(username=session['uname']).first().id))
            db.session.commit()
            return render_template('spllchkresult.html', User = session['uname'], supplied_text = inputtext, output = res)
        return render_template('spell_check.html', User = session['uname'], guest = False)
    else:
        return render_template('spell_check.html', User = 'guest', guest = True)

@app.route('/history', methods = ['GET','POST'])
def history():
    if 'uname' not in session:
        return render_template('no_access.html')
    user_id = User.query.filter_by(username=session['uname']).first().id
    queries = Query.query.filter_by(user_id=user_id).all()
    if session['uname'] == 'admin':
        if request.method == 'POST':
            username = request.form['username']
            user_id = User.query.filter_by(username=username).first().id
            queries = Query.query.filter_by(user_id=user_id).all()
            return render_template('history.html', User = username, queries = queries)
    return render_template('history.html', User = session['uname'], queries = queries)

@app.route('/history/query<id>')
def query(id):
    query = Query.query.filter_by(id=id).first()
    username = User.query.filter_by(id=query.user_id).first().username
    if session['uname'] == username or session['uname'] == 'admin':
        return render_template('query.html', id= id, username = username, text = query.text, results = query.results)
    return render_template('no_access.html')

@app.route('/login_history', methods = ['GET','POST'])
def login_history():
    if 'uname' not in session or session['uname'] != 'admin':
        return render_template('no_access.html')
    if request.method == 'POST':
        username = request.form['username']
        user_id = User.query.filter_by(username=username).first().id
        logs = Log.query.filter_by(user_id=user_id).all()
        return render_template('login_history.html', User = session['uname'], logs = logs)
    return render_template('login_history.html', User = session['uname'], logs = None)

@app.route('/logout')
def logout():
    if 'uname' in session:
        user_id = User.query.filter_by(username=session['uname']).first().id
        log = Log.query.filter_by(user_id=user_id).order_by(desc('login')).first()
        log.logout = str(datetime.utcnow())
        db.session.commit()
        session.pop('uname', None)
        return render_template('logout.html')
    return redirect(url_for('index'))

if __name__ == '__main__':
    #set debug to false to avoid security issues
    app.run(debug=False)