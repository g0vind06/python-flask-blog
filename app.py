from flask import Flask,render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask import session
import json
import os
import math
from werkzeug.utils import secure_filename
from datetime import datetime

with open("config.json", 'r') as c:
        params = json.load(c)['params']

local_server = True
app = Flask("Tech Blog") 
app.secret_key='super-secret-key'

app.config['UPLOAD_FOLDER']=params['upload_location']

# app.config.update(
#         EMAIL_SERVER = 'smtp.gmail.com',
#         EMAIL_PORT = '465',
#         EMAIL_USE_SSL = True,
#         EMAIL_HOST_USERNAME = params["gmail-user"],
#         EMAIL_HOST_PASSWORD = params["gmail-password"]
# )
# mail = Mail(app)

if (local_server):
        app.config['SQLALCHEMY_DATABASE_URI'] = params["local_uri"]
else:
        app.config['SQLALCHEMY_DATABASE_URI'] = params["prod_uri"]

db = SQLAlchemy(app)

class Contact(db.Model):
        Sno = db.Column(db.Integer, primary_key=True)
        Name = db.Column(db.String(80), nullable=False)
        Email = db.Column(db.String(120), nullable=False)
        Phone = db.Column(db.String, nullable=False)
        Message = db.Column(db.String, nullable=False)
        Date = db.Column(db.String, nullable=True)

class Post(db.Model):
        Sno = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(80), nullable=False)
        content = db.Column(db.String(120), nullable=False) 
        tagline = db.Column(db.String(120), nullable=False) 
        slug = db.Column(db.String, nullable=False)
        img_file = db.Column(db.String, nullable=False)
        datetime = db.Column(db.String, nullable=True)


@app.route("/")
def home():
        posts = Post.query.filter_by().all()
        # [0:params['no_of_posts']]

        #Pagination
        last=math.ceil(len(posts)/params['no_of_posts'])
        page = request.args.get('page')
        if(not str(page).isnumeric()):
               page = 1

        page=int(page)
        posts = posts[(page-1)*int(params['no_of_posts']):(page-1)*int(params['no_of_posts'])+ int(params['no_of_posts'])]

        if page==1:
               prev='#'
               next='/?page='+str(page+1)
        elif page==last:
               next='#'
               prev='/?page='+str(page-1)
        else:
               prev='/?page='+str(page-1)
               next='/?page='+str(page+1)

        return render_template('index.html',params = params, posts=posts, prev=prev, next=next)

@app.route("/home")
def home1():
        return redirect("/")

@app.route("/about")
def about():
        return render_template('about.html',params = params)

@app.route("/post/<string:post_slug>",methods = ['GET'])         #post_slug is variable name
def post_route(post_slug):
        post = Post.query.filter_by(slug=post_slug).first()
        return render_template('post.html',params = params ,post=post)

@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    if 'user' in session and session['user'] == params['admin_user']:
        print('User already logged in')
        posts=Post.query.all()
        return render_template('dashboard.html', params=params,posts=posts)

    if request.method == "POST":
        username = request.form.get('uname')
        userpass = request.form.get('pass')
        if username == params['admin_user'] and userpass == params['admin_password']:
            session['user'] = username
            print('User logged in successfully')
            posts=Post.query.all()
            return render_template('dashboard.html', params=params, posts=posts)
       
    return render_template('login.html', params=params)

@app.route("/edit/<string:Sno>", methods = ['GET','POST'])
def edit(Sno):
       if 'user' in session and session['user'] == params['admin_user']:
                if(request.method=='POST'):
                     box_title = request.form.get('title')
                     tagline = request.form.get('tagline')
                     slug = request.form.get('slug')
                     content = request.form.get('content')
                     img_file = request.form.get('img_file')
                     
                     if Sno == '0':
                        post = Post(title = box_title, tagline = tagline, slug = slug, content = content, datetime = datetime.now(),img_file = img_file )
                        db.session.add(post)
                        db.session.commit()

                     else:
                        post=Post.query.filter_by(Sno=Sno).first()
                        post.title = box_title
                        post.tagline = tagline
                        post.slug = slug
                        post.content = content
                        post.img_file = img_file
                        db.session.commit()
                        return redirect('/edit/'+Sno)
       
       post = Post.query.filter_by(Sno=Sno).first()              
       return render_template('edit.html', params=params, post=post,Sno=Sno)
                            
@app.route("/uploader", methods = ['GET','POST'])
def uploader():
        if 'user' in session and session['user'] == params['admin_user']:
                if(request.method=='POST'):
                       f=request.files['file1']
                       f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
                       return "Uploaded Successfully!"
       
@app.route("/logout")
def logout():
       session.pop('user')
       return redirect('/dashboard')

@app.route("/delete/<string:Sno>", methods = ['GET','POST'])
def delete(Sno):
       if 'user' in session and session['user'] == params['admin_user']:
              post = Post.query.filter_by(Sno=Sno).first()
              db.session.delete(post)
              db.session.commit()
       return redirect('/dashboard')
       

@app.route("/contact", methods = ['GET','POST'])
def contact():
        if(request.method=='POST'):
                '''Add entry to the database'''
                name = request.form.get('name')
                email = request.form.get('email')
                phone = request.form.get('phone')
                message = request.form.get('message')
                entry = Contact(Name = name, Phone = phone, Message = message, Date = datetime.now(),Email = email )
                db.session.add(entry)
                db.session.commit()
                # mail.send_message(
                #         'New message from'+name,
                #         sender = email,
                #         recipients = [params["gmail-user"]],
                #         body = message + '\n' + phone
                # )
        return render_template('contact.html', params = params)

if __name__ == "__main__":
        app.run(debug=True)
