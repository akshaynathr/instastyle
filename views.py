from flask import Flask,jsonify,request,render_template,url_for, redirect,flash,session,flash
from werkzeug import secure_filename
 
import rethinkdb as r
import json
import sys
import os
app=Flask(__name__)
app.config['SECRET_KEY']='2312ghas'
from models import dbSetUp

# starts database
dbSetUp()
 
conn=r.connect(host='localhost',port='28015')

@app.route('/',methods=['GET','POST'])
@app.route('/home',methods=['GET','POST'])
def home():
    return render_template('home/index.html')



@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='GET':
        if 'apiKey' in session:
            return redirect(url_for('discover'))
        return render_template('login/index.html')
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']

        count=r.db('instastyle').table('user').filter({'username':username,'password':password}).count().run(conn)
        user=list(r.db('instastyle').table('user').filter({'username':username,'password':password}).run(conn))

        if count>0:
            session['apiKey']=user[0]['apiKey']
            return redirect(url_for('discover'))
        else :
            flash("Login error")
            return render_template('login/index.html')
    



@app.route('/signup',methods=['GET','POST'])
def signup_form():
    
    if request.method=='GET':
        return render_template('login/signup.html')
    if request.method=='POST':
        username=request.form['username']
        password=request.form['password']
        email=request.form['email']
        name=request.form['name']
        gender=request.form['gender']
        college=request.form['college']


    # Get the name of the uploaded file
         
        count=r.db('instastyle').table('user').filter({'username':username}).count().run(conn)
        if count >0:
            flash("username already taken")
            return render_template('login/signup.html')
        else :
            try:
                user=r.db('instastyle').table('user').insert({'username':username,'college':college,
                    'email':email ,'gender':gender,'user_image':'profile.png','image_set':0,'password':password,'name':name,'apiKey':r.random(1000000),'follow':[],'date':r.now()}).run(conn)
                user_data=list(r.db('instastyle').table('user').filter((r.row['username']==username) & (r.row['password']==password)).run(conn))
                session['apiKey']=user_data[0]['apiKey']
            except BaseException as e:
                result="Error in saving data:"+str(e)
                flash(result)
                return render_template('login/signup.html')
                
            return  redirect(url_for('discover')) 
 

@app.route('/discover_my_feed',methods=['GET','POST'])
def discover_my_feed():
    #add session here
    if request.method=='GET':
        if 'apiKey' in session:
            apiKey=int(session['apiKey'])
            feed_url='/feed/'+str(session['apiKey'])
            profile_url='/profile/'+str(session['apiKey'])
            my_feed='/myfeed/'+str(session['apiKey'])       
            user=list(r.db('instastyle').table('user').filter({'apiKey':apiKey}).run(conn))       
            return render_template('profile.html',user=user[0],myfeed=my_feed,feed=feed_url,profile=profile_url,apiKey=session['apiKey'])

        else :
            return "Not logged in"

    if request.method=='POST':
        image_url=''
        
        apiKey=int(request.form['user'])
        image=request.files['image']
        title=request.form['title']
        desc=request.form['desc']
        print("ApiKey:")
        print(apiKey)

        user=list(r.db('instastyle').table('user').filter({'apiKey':apiKey}).run(conn))
        print user
        r.db('instastyle').table('post').insert({'apiKey':int(apiKey),'name':user[0]['name'],'image':image_url,'user_image':user[0]['user_image'],'title':title,'desc':desc,'date':r.now()}).run(conn)
        img=list(r.db('instastyle').table('post').filter((r.row['apiKey']==int(apiKey)) & (r.row['title']==title) & (r.row['desc']==desc) ).run(conn))
        image_url=img[0]['id']+'.'+image.filename.rsplit('.',1)[1]

        print image_url
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_url))
        r.db('instastyle').table('post').filter((r.row['apiKey']==int(apiKey)) & (r.row['title']==title) & (r.row['desc']==desc) ).update({'image':image_url}).run(conn)
        return redirect('discover_my_feed')


@app.route('/discover_page')
def discover():
    #add session here
    if 'apiKey' in session:
        apiKey=int(session['apiKey'])
        feed_url='/feed/'+str(session['apiKey'])
        profile_url='/profile/'+str(session['apiKey'])
        my_feed='/myfeed/'+str(session['apiKey'])  
        user=list(r.db('instastyle').table('user').filter(lambda doc:doc['apiKey']!=apiKey).run(conn) )
        print user
        return render_template('feeds.html',friends=user,profile='/discover_my_feed',apiKey=session['apiKey'])

    else :
        flash('Not logged in')
        return redirect(url_for('login'))


@app.route('/feed/<apiKey>/<int:no>')
def feed(apiKey,no):
    count=r.db('instastyle').table('user').filter({'apiKey':int(apiKey)}).count().run(conn)
    skip_no=no*8
    if count>0:
	try:
		post_feed=list(r.db('instastyle').table('user').filter({'apiKey':int(apiKey)})['follow'][0].eq_join(lambda x:x,r.db('instastyle').table('post'),index='apiKey').zip().order_by(r.desc('date')).skip(skip_no).limit(8).run(conn))
        #post_feed=list(r.db('instastyle').table('post').filter({'apiKey':int(apiKey)}).order_by(r.desc('date')).run(conn))
		return jsonify({'feed':post_feed})
	except Exception as e:
		return jsonify({'feed':str(e)}),400
    else :
        return jsonify({'feed':'error'}),400


@app.route('/myfeed/<apiKey>/<int:no>')
def myfeed(apiKey,no):
    try:
	    count=r.db('instastyle').table('user').filter({'apiKey':int(apiKey)}).count().run(conn)
	    if count>0:

		#post_feed=list(r.db('instastyle').table('user').filter({'apiKey':int(apiKey)})['follow'][0].eq_join(lambda x:x,r.db('instastyle').table('post'),index='apiKey').run(conn))
		skip_no=no*8	
		post_feed=list(r.db('instastyle').table('post').filter({'apiKey':int(apiKey)}).order_by(r.desc('date')).skip(skip_no).limit(8).run(conn))

		return jsonify({'feed':post_feed})
	    else :
		return jsonify({'feed':'not authenticated'}),400
    except Exception as e:
	    return jsonify({'error':str(e)}),406



@app.route('/feed_entry/<postId>/<apiKey>')
def feed_entry(postId,apiKey):
    count=r.db('instastyle').table('user').filter({'apiKey':int(apiKey)}).count().run(conn)
    if count>0:
        post_feed=list(r.db('instastyle').table('post').filter({'id':(postId)}).run(conn))
        post_count=r.db('instastyle').table('post').filter({'id':(postId)}).update({'views':r.row['views']+1}).run(conn)

        return jsonify({'feed':post_feed})
    else :
        return jsonify({'feed':'error'})




def authenticate(apiKey):
    count=(r.db('instastyle').table('user').filter({'apiKey':int(apiKey)}).count().run(conn))
    if count>0:
        return 1
    else :
        return 0

@app.route('/profile/<apiKey>')
def profile(apiKey):
    if 'apiKey' in session:
        print apiKey
        access=authenticate(apiKey)
        if access ==1:
            user=list(r.db('instastyle').table('user').filter({'apiKey':int(apiKey)}).run(conn))
            print user
            img='uploads/'+user[0]['img']
            return render_template('profile.html',img=img,user=user[0])
        else:
            return "Not logged in "
    else:
        return "Not logged in"


#this profile is same as the profile above . Profile2 is used to connect users

@app.route('/profile2/<apiKey>')
def profile2(apiKey):
    if 'apiKey' in session:
        print apiKey

	flag=False
        access=authenticate(apiKey)
	friends_key=int(session['apiKey'])
	followers=list(r.db('instastyle').table('user').filter({'apiKey':friends_key})['follow'].run(conn))
	current_user_key=int(apiKey)
	if current_user_key in followers[0]:
		flag=True
        if access ==1:
            user=list(r.db('instastyle').table('user').filter({'apiKey':int(apiKey)}).run(conn))
            print user
            img=user[0]['user_image']
            return render_template('profile2.html',img=img,user=user[0],profile_user=int(apiKey),current_user=session['apiKey'],flag=flag)
        else:
            return "Not logged in "
    else:
        return "Not logged in"


@app.route('/addProfile',methods=['GET','POST'])
def addProfile():
    if request.method=='GET':
        if 'apiKey' in session:
            return render_template('addProfile.html')
    if request.method=='POST':
        image_url=''
        
        apiKey=int(session['apiKey'])
        image=request.files['image']
         

        user=list(r.db('instastyle').table('user').filter({'apiKey':apiKey}).run(conn))
        print user
        image_url=user[0]['id']+'.'+image.filename.rsplit('.',1)[1]

        r.db('instastyle').table('user').filter({'apiKey':apiKey}).update({'user_image':image_url}).run(conn)
        

        print image_url
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_url))
        return redirect('discover_my_feed')



@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out")
    return redirect(url_for('home'))


@app.route('/followers/<int:apiKey>')
def followers(apiKey):
    access=authenticate(apiKey)
    if access==1:
        followers=r.db('instastyle').table('user').filter({'apiKey':apiKey})['follow'][0].eq_join(lambda x: x,r.db('instastyle').table('user'),index='apiKey').zip().run(conn)
        count=len(followers)
        return jsonify({'followers':followers,'count':count})
    else:
        return 0


@app.route('/connect',methods=['GET','POST'])
def connect():
    if 'apiKey' in session:
        if request.method=='GET': 
            apiKey=session['apiKey']
            
            profile='/profile/'+str(session['apiKey'])
            user=list(r.db('instastyle').table('user').filter(lambda doc:doc['apiKey']!=apiKey).limit(4).run(conn) )
                
            return render_template('friendList/index.html',people=user,msg='',profile='/discover_my_feed')
  #       if request.method=='POST':
  #           apiKey=session['apiKey']
            
  #           profile='/profile/'+str(session['apiKey'])
  #           name=request.form['search']
  #           matchkey="(?i)^"+name+"$"
  #           count=r.db('instastyle').table('user').filter((lambda doc:(doc['name'].match(name.title())) & (doc['apiKey']!=apiKey))).count().run(conn) 
  #           #count=r.db('instastyle').table('user').filter({'email':email}).count().run(conn)
  #           if count >0:
  #               print "Entered"
		# #st(r.db('instastyle').table('user').filter(lambda x: r.expr(t[0]['follow']).contains(x['apiKey']).not_() ).run(conn))
  #               user=list(r.db('instastyle').table('user').filter(lambda doc:(doc['name'].match(name.title())) & (doc['apiKey']!=apiKey)).run(conn) )
				
  #               #user=list(r.db('instastyle').table('user').filter({'name':name}).run(conn))
  #               msg=str(count)+' users found'
  #               profile='/profile/'+str(session['apiKey'])
  #               return render_template('friendList/index.html',user=user,msg='',profile=profile,apiKey=session['apiKey'])

  #           else :
  #               return render_template('friendList/index.html',user=None,msg="No user found",profile=profile,apiKey=session['apiKey'])
  #   
    else:
        return "Not logged in"
 


#############IMAGE UPLOAD @@@@@@@@@@@@@@@@@@@@ 
# This is the path to the upload directory
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = set([ 'png', 'jpg', 'jpeg'])

# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and  filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

####################### follower################################
#apiKey1 => current user
#apiKey2 => user to be followed
@app.route('/addFollowers/<int:apiKey1>/<int:apiKey2>',methods=['POST'])
def addFollower(apiKey1,apiKey2):
    access=authenticate(apiKey1)
    if access==1:
        access2=authenticate(apiKey2)
        if access2==1:
	    current_user=list(r.db('instastyle').table('user').filter({'apiKey':apiKey1}).run(conn))
	    if apiKey2 in current_user[0]['follow']:
		return jsonify({'result':'Already following'}) 	 
	    else:
		    user=list(r.db('instastyle').table('user').filter({'apiKey':apiKey1}).update({'follow':r.row['follow'].append(apiKey2)}).run(conn))
		    return jsonify({'result':'success'})
        else:
            return 0
    else:
        return 0
 

############################search###########################
@app.route('/search/<int:apiKey>',methods=['POST'])
def search(apiKey):
    data=json.loads(request.data)
    key=data['key']
    print key
    access=authenticate(apiKey)
    if access==1:
        try:
            post=list(r.db('instastyle').table('post').filter(lambda post: post['keywords'].contains(key)).run(conn))
            return jsonify({'feed':post})
        except Exception as e:
            return jsonify({'error':str(e)})

    else :
        return "No access"


###################################################################

########################users list ##################################
@app.route('/allusers/<int:apiKey>')
def allusers(apiKey):
    users=list(r.db('instastyle').table('user').filter(r.row['apiKey']!=apiKey).run(conn))
    return jsonify({'users':users})
 