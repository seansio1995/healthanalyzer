from flask import Flask, render_template, request, redirect, url_for, session
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import smtplib
from email.mime.text import MIMEText
from math import *

app = Flask(__name__)
app.secret_key = "super secret key"
POSTGRES = {
    'user': 'postgres',
    'pw': '',
    'db': 'healthanalyzer',
    'host': 'localhost',
    'port': '5433',
}
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///healthanalyzer.db'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:@localhost/healthanalyzer'
db = SQLAlchemy(app)

# Create our database model
db.create_all()
# db.session.commit()
def send_email(email, height, weight, age,average_height_value, average_weight_value,average_age_value, count):
    FROM_EMAIL='healthanalyzer2017@gmail.com' #healthanalyzer
    FROM_PASSWORD=''   #
    message="Hey there, your height is <strong> %s</strong>. <br> \
    Your weight is <strong> %s </strong>. <br> \
    Your age is <strong> %s </strong>. <br> \
    Among <strong> %s </strong> users in our survey <br> \
    Average height of users is <strong>%s</strong>. <br> \
    Average weight of users is <strong>%s</strong>. <br> \
    Average age of users is <strong>%s</strong>. <br> \
    Thanks!" \
    % (height, weight, age, count, average_height_value, average_weight_value, average_age_value)
    print("e: ",email)
    #print("m: ",message)
    subject="Your Health Statistics"
    #toList=[email]
    toList=email


    gmail = smtplib.SMTP('smtp.gmail.com',587)
    gmail.ehlo()
    gmail.starttls()
    gmail.login(FROM_EMAIL,FROM_PASSWORD)

    msg=MIMEText(message, 'html')
    msg['Subject']=subject
    #msg['To']=','.join(toList)
    msg['To']=toList
    msg['From']=FROM_EMAIL

    gmail.send_message(msg)


class User(db.Model):

    __tablename__ = "myusers"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    height = db.Column(db.Integer)
    weight= db.Column(db.Integer)
    age = db.Column(db.Integer)

    def __init__(self, email, height, weight, age):
        self.email = email
        self.height = height
        self.weight = weight
        self.age = age

def bmi_calculator(height,weight):
    height=int(height)
    weight=int(weight)
    scaled_height=height/100
    result=weight/pow(scaled_height,2)
    return result

#    def __repr__(self):
#        return '<E-mail %r>' % self.email

# Set "homepage" to index.html
@app.route('/')
def index():
    return render_template('index.html')

# Save e-mail to database and send to success page
@app.route('/stats',methods=['POST'])
def stats():
    email_ = None
    height_ = None
    weight_ = None
    age_ = None
    if request.method == 'POST':
        email_ = request.form['email_name']
        print("Email is: ",email_)
        height_ = request.form['height_name']
        weight_ = request.form['weight_name']
        age_= request.form['age_name']

        # Check that email does not already exist (not a great query, but works)
        if not db.session.query(User).filter(User.email == email_).count():
            reg = User(email_, height_, weight_, age_)
            db.session.add(reg)
            db.session.commit()
            average_height_query=db.session.query(func.avg(User.height))
            average_weight_query=db.session.query(func.avg(User.weight))
            average_age_query=db.session.query(func.avg(User.age))
            average_height_value=round(average_height_query.scalar(),1)
            average_weight_value=round(average_weight_query.scalar(),1)
            average_age_value=round(average_age_query.scalar(),1)
            count=db.session.query(User.height).count()

            #print(float(average.all()[0]))
            #print(type(average))
            #print(average.value(User.height))
        if request.form['submit']=="STAT":
            send_email(email_, height_, weight_, age_,average_height_value, average_weight_value, average_age_value,count)
            return render_template('success.html', email=email_)
        elif request.form['submit']=="OVERWEIGHT?":
            bmi_ratio=bmi_calculator(height_,weight_)
            if bmi_ratio > 30:
                res="obese"
            elif bmi_ratio > 25:
                res="overweight"
            else:
                res="underweight"
            session['res']=res
            return redirect(url_for('overweight',res=res))
    return render_template('index.html', text="Seems like we've got something from that email already!")

@app.route('/overweight',methods=['GET'])
def overweight():
    res=session['res']
    return render_template("overweight.html",res=res)


if __name__ == '__main__':
    app.debug = True
    app.run(port=5000)
