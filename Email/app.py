from  flask import Flask, render_template, request,url_for,redirect,session
from flask_mail import Mail, Message
from pymongo import MongoClient
import hashlib
from Model import gpt,styl



message=""
reciever=""
subject=""
email={}
li=[]






#Initalizing App Instance
app=Flask(__name__)
app.secret_key = 'your_secret_key'

#database Configuration
client = MongoClient("mongodb://localhost:27017/")
db = client["mydatabase"]
users_collection = db["users"]
users_collection.create_index("email", unique=True)

 
#Home Page
@app.route('/')
def home():
    session.clear()
    return render_template('home.html')



#login Page
@app.route('/login')
def login():
    if 'username' in session:
        return redirect(url_for('dashboard'))

    return render_template('login.html')

@app.route('/authenticate', methods=['POST'])
def authenticate():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashed_password = hashlib.md5(password.encode('utf-8')).hexdigest()
        user = users_collection.find_one({"email": email, "password": hashed_password})
        if user is not None:
            session['username'] = user['name']
            session['designation'] = user['designation']
            session['email']=user['email']
            
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error=True)
    else:
        return render_template('login.html')
    


    

#User Dashboard Module    
@app.route('/dashboard', methods=['GET','POST'])
def dashboard():
    global subject,message,reciever,email,li
    message1=""
    content=""

    
    if 'username' in session and 'designation' in session:
        username = session['username']
        registering_as = session['designation']

        if request.method=='POST':
            
            if 'seabtn' in request.form:
                reciever=request.form['keyword']
                li = reciever.split(",")
                print(li)
                for item in li:
                    user = users_collection.find_one({'$or': [{'name': {'$regex': item.strip(), '$options': 'i'}}, {'designation': {'$regex': item.strip(), '$options': 'i'}}]})
                    if user:
                        email[user['name']] = user['email']
                    else:
                        nofound=f"No user found with name or designation matching {item.strip()}"
                        return nofound
                print(email)  
            elif 'gbtn' in request.form :
            
                message=request.form['area']
                message1=request.form['area']
                selected_engine = request.form['engine']
                reciever=request.form['keyword']
                print(reciever)
                print(selected_engine)

                if selected_engine=='1':
                    
                    content="Generate A Formal Mail on the below mentioned points. Dont include subject \n Points \n "+message+"\n Note: The Sender is:"+username+"Dont Include Any Reciepent Name field"
                    message=gpt.api(content)
             
                elif selected_engine=='2':
                    print(message)
                    message=styl.style(message)
                
                    if len(li)==1:
                        message="Dear "+li[0]+",\n"+message+"\nThanks & Regards"
                    else:
                        message="Dear All, \n"+message+"\nThanks & Regards"
                else:
                    print()
                print(content)
                subject=gpt.api("Suggest a subject for the following mail based on its content of body: "+message)
                print(subject)
            else:
                print()
                  
        else:
            print()
            message = ""
        return render_template('dashboard.html', username=username, registering_as=registering_as,message=message,message1=message1, reciever=reciever,subject=subject)
    else:
        return redirect(url_for('login'))
    

@app.route('/button',methods=['GET','POST'])

def button():
    global subject,message,reciever,email,li
    result = users_collection.find_one({"email": session['email']})
    shared_key = result['shared_key']

    print(shared_key)

    app.config['MAIL_SERVER']='smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = session['email']
    app.config['MAIL_PASSWORD'] = shared_key
    
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    mail = Mail(app)

    
    print(list(email.values()))
    recipients=list(email.values())

    msg = Message(subject, sender=session['email'], recipients=recipients)
    msg.body = message
    print(subject,message,reciever)

    mail.send(msg)
    
    return render_template("mail_sent.html")

    
   
    
    
#Dashboard Module: Logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('designation', None)
    return redirect(url_for('login'))

#Dashboard Module: Update Profile

@app.route("/edit", methods=['GET', 'POST'])
def display_profile():

    user_email = session['email'] # replace with code to get logged-in user's email
    user = users_collection.find_one({"email": user_email})
    return render_template("display_data.html", user=user)

@app.route("/update-profile/<email>", methods=["GET", "POST"])
def update_profile(email):
    user = users_collection.find_one({"email": email})
    
    if request.method == "POST":
        name = request.form["name"]
        designation = request.form["designation"]
        email = request.form["email"]
        shared_key = request.form["shared_key"]
        
        users_collection.update_one({"email": email}, {"$set": {"name": name, "designation": designation, "email":email, "shared_key":shared_key}})
        return redirect("/edit")
    return render_template("update_profile.html", user=user)

@app.route("/delete-profile/<email>", methods=["GET","POST"])
def delete_profile(email):
    users_collection.delete_one({"email": email})
    session.pop('username', None)
    session.pop('designation', None)
    return render_template('home.html')






#Registration Module
@app.route('/registration')
def registration():
    return render_template('registration.html')


#Registering User
@app.route('/submit', methods=['POST'])
def submit():
     name = request.form['name']
     password = hashlib.md5(request.form['password'].encode('utf-8')).hexdigest()
     email = request.form['email']
     
     shared_key = request.form['shared_key']
     #registering_as = request.form['registering_as']
     designation = request.form.get('designation', '') # Set default value to empty string

    # Check if the email already exists in the collection
     if users_collection.find_one({'email': email}) is not None:
        return render_template('registration.html', error=True)

    # Insert the new user into the collection
     user = {
        'name': name,
        'password': password,
        'email': email,
        'shared_key': shared_key,
        #'registering_as': registering_as,
        'designation': designation
    }
     users_collection.insert_one(user)
     return render_template('login.html',Smsg=True)

    




if __name__=='__main__':
    app.run(debug=True)
