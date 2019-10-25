from flask import Flask,render_template,request,redirect,flash,url_for,session

usr_list = []

class usr_info:
    def __init__(self,username,password,two_factor):
        self.uname = username
        self.pword = password
        self.twofa = two_factor

app = Flask(__name__)

app.secret_key = b'few9i04tjjvp0:id9022'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods = ['GET','POST'])
def login():
    result = "unknown"
    if request.method == 'POST':
        uname = request.form['uname']
        pword = request.form['pword']
        twofa = request.form['2fa']
        if not any(user.uname == uname and user.pword == pword for user in usr_list):
            result = "Incorrect username or password"
        else:
            for user in usr_list:
                if user.uname == uname and user.pword == pword:
                    if user.twofa == twofa:
                        result = "success"
                        return render_template('login.html', result = result)
                    else:
                        result = "Two-factor authentication failure"
                        return render_template('login.html', result = result)
    return render_template('login.html', result = result)

@app.route('/register', methods = ['GET','POST'])
def register():
    if request.method == 'POST':
        uname = request.form['uname']
        pword = request.form['pword']
        twofa = request.form['2fa']
        if any(user.uname == uname for user in usr_list):
            return render_template('regresult.html', success = "failure")
        else:
            user = usr_info(uname,pword,twofa)
            usr_list.append(user)
            return render_template('regresult.html', success = "success")
    return render_template('register.html')

@app.route('/spell_check')
def spell_check():
    return 'Enter text to spell check'

if __name__ == '__main__':
    app.run(debug=True)#set to false to avoid security issues