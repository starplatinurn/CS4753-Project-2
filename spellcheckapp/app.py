from flask import Flask,render_template,request,redirect,flash,url_for,session
import os

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
        if not any(user.uname == uname and user.pword == pword for user in usr_list):
            result = "Incorrect username or password"
        else:
            for user in usr_list:
                if user.uname == uname and user.pword == pword:
                    if user.twofa == twofa:
                        result = "success"
                        session['uname'] = uname
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
        if any(user.uname == uname for user in usr_list):
            return render_template('regresult.html', success = "failure")
        else:
            user = usr_info(uname,pword,twofa)
            usr_list.append(user)
            return render_template('regresult.html', success = "success")
    return render_template('register.html')

@app.route('/spell_check', methods = ['GET','POST'])
def spell_check():
    if 'uname' in session:
        if request.method == 'POST':
            inputtext = request.form['inputtext']
            with open('input.txt', 'w') as input:
                input.write(inputtext)
            cmd = './a.out input.txt wordlist.txt'
            out = os.popen(cmd).read()
            res = ', '.join(out.split())
            return render_template('spllchkresult.html', User = session['uname'], supplied_text = inputtext, output = res)
        return render_template('spell_check.html', User = session['uname'], guest = False)
    else:
        return render_template('spell_check.html', User = 'guest', guest = True)

@app.route('/logout')
def logout():
    if 'uname' in session:
        session.pop('uname', None)
        return render_template('logout.html')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)#set to false to avoid security issues