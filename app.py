import base64
import datetime
import time
import os
import matplotlib.image as mpimg
import csv
import mail as ml
import cv2
import recog
import pandas as pd
from flask import Flask,render_template,request,Response,redirect,session
import pymysql  #使用mysql数据库，dbpwd为密码，dbname为数据库名称,测试用户名a，密码123
dbpwd=''
dbname=''

app = Flask(__name__)
app.config['SECRET_KEY']=os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME']=1000
name=None

def saveimg(img, landmarks, name):
    # save image and info to ./dataset/face/user/
    fname = 'png/user/' + name + '.png'
    cv2.imwrite(fname, img)
    with open('png/user/' + name+'.txt', 'a') as file:
        file.write(str(landmarks))#.strip('[').strip(']') + '\n')

def writelog(param):
    df=pd.DataFrame(param,index=[0])
    df.to_csv('log/login.csv',index=None,mode='a',header=False)
    # with open('log/login.csv','a')as f:
    #     names = {'uid','name','time','ip','result','type'}
    #     writer = csv.DictWriter(f,names)
    #     #writer.writeheader()
    #     writer.writerow(param)  #登陆后识别：

@app.route('/', methods=['GET'])
def home():
    print(session.get('name'))
    if (session.get('name')!=None):
        return render_template('index1.html',uid=session.get('name'))
        print('!!!!!')
    else:
        return render_template('index.html')

@app.route('/', methods=['POST'])
def signin():
    type = request.form.get('type')
    print('type',type)
    imdata = request.form.get('img')
    ip=request.remote_addr
    fname='png/tmp/{}.png'.format(time.strftime('%Y%m%d %H %M %S',time.localtime()))
    fout = open(fname, 'wb')
    fout.write(base64.b64decode(imdata)) #base64解码，写入图片
    fout.close()
    img = cv2.imread(fname)
    mark=recog.get_landmarks(img)
    if (int(type)==1):      
        if(session.get('name')!=None):
            uid=session.get("name")
            img1=cv2.imread('png/user/'+session['name']+'.png')
            mark1=recog.get_landmarks(img1)
            distance=recog.compare(img,mark,img1,mark1)
            if(distance>=0.3):
                t=time.strftime('%Y%m%d %H:%M:%S',time.localtime())
                data = {'uid':uid,'name':' ','time':t,'ip':ip,'result':'1','type':'Uid'}
                writelog(data)
                return 'OK'
            else:
                return 'failed'
        else:
            for root, dirs, files in os.walk('png/user/'):
                for f in files:
                    if(f.find('.png')!=-1):
                        img1=cv2.imread('png/user/'+f)
                        mark1=recog.get_landmarks(img1)
                        distance=recog.compare(img,mark,img1,mark1)
                        if(distance>=0.3):
                            t=time.strftime('%Y%m%d %H:%M:%S',time.localtime())
                            uid=f.split('.')[0]
                            df = pd.read_csv('log/login.csv')                            
                            z = df[df['time']==t[:8]]
                            z = [z['uid']==uid]
                            #if(z):
                            #f = csv.reader(open(fname,'r'))
                            # for i in f:
                            #     if i[0]==uid and i[]==t[0:9]:
                            #         return "alreadyloged"
                            #f = pd.read_csv('log/login.csv')
                            #f = f[f['uid']==uid]
                            data = {'uid':uid,'name':' ','time':t,'ip':ip,'result':'1','type':'Face'}
                            writelog(data)
                            session['name']=uid
                            return 'OK'
            return "failed"
    else:
        if (session.get('name')!=None):
            if(any(mark)==None):
                return "noface"
            saveimg(img,mark,session["name"])
            return 'OK'
        else:
            return  'login'

@app.route('/login', methods=['POST'])
def login():
    ip=request.remote_addr
    if (session.get('name')==None):
        uid=request.form.get('uid')
        pwd=request.form.get('pwd')
        db = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd=dbpwd, db=dbname, charset='utf8')
        cursor = db.cursor()
        #print(uid)
        #print(pwd)
        if(cursor.execute("select * from users where uid='"+uid+"' && pwd='"+pwd+"';")==0):
            cursor.close()
            db.close()
            return  'wrong'
        session['name']=uid
        name=uid
        uid = session.get('name')
        tim=time.strftime('%Y%m%d',time.localtime())
        fname='log/{}.scv'.format(tim);
        data = {'uid':uid,'name':' ','time':tim,'ip':ip,'result':'1','type':'Uid'}
        writelog(data)
        return 'logok'
    else:
        return 'loged'

@app.route('/logout', methods=['POST'])
def logout():
    # data = {'uid':uid,'name':' ','time':tim,'ip':ip,'result':'1','type':'Uid'}
    # writelog(data)
    session.pop('name')
    name=None
    return redirect('/')

@app.route('/register', methods=['GET'])
def regpage():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    uid=request.form.get('uid')
    pwd=request.form.get('pwd')
    mail=request.form.get('mail')
    sd=request.form.get('sd')
    code=request.form.get('vcode')
    if sd=='1':
        if not mail:
            return 'checkmail'
        rt=ml.sendcode(mail)
        session['code']=rt
        session['codet']=time.time()
        return 'sent'
    else:
        t=time.time()
        if(code!=session.get('code') or session.get('codet')==None or (t-session.get('codet')>=120)):
            return 'resend'
        if (mail and uid and pwd):
            db = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd=dbpwd, db=dbname, charset='utf8')
            cursor = db.cursor()
            if(cursor.execute("select * from users where uid='"+uid+"'")==1):
                cursor.close()
                db.close()
                return  'exist'
            else:
                cursor.execute("insert into users values('"+uid+"','"+pwd+"','"+mail+"')")
                db.commit()
                cursor.close()
                db.close()
                return 'regok'
        else:
            return 'null'
   
@app.route('/findpass', methods=['POST','GET'])
def findpass():
    uid=request.form.get('uid')
    if(uid):
        db = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd=dbpwd, db=dbname, charset='utf8')
        cursor = db.cursor()
        if(cursor.execute("select * from users where uid='"+uid+"'")!=1):
            cursor.close()
            db.close()
            return  'wronguid'
        else:
            cursor.execute("select pwd,email from users where uid='"+uid+"'")
            res = cursor.fetchone()
            pwd = res[0]
            email = res[1]
            rt=ml.send('Your password:'+pwd,email,'Password')
            if(rt):
                return "sent"
            else:
                return "sendfail"
    else:
        return 'wronguid'

@app.route('/user', methods=['POST','GET'])
@app.route('/user/<string:user_id>')
def user():
    uid = session.get('name')
    if(request.method=='GET'):
        f = pd.read_csv('log/login.csv')
        f = f[f['uid']==uid].values
        return render_template('user.html',logs=f)
    else:
        fpwd=request.form.get('fpwd')
        pwd=request.form.get('pwd')
        db = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd=dbpwd, db=dbname, charset='utf8')
        cursor = db.cursor()
        if(cursor.execute("select * from users where uid='"+uid+"' and pwd='"+fpwd+"'")!=1):
            cursor.close()
            db.close()
            return  'wrong'
        else:
            cursor.execute("UPDATE users SET pwd = '"+pwd+"' WHERE uid = '"+uid+"'")
            db.commit()
            cursor.close()
            db.close()
            return  'OK'
    #UPDATE user SET pwd = ' ' WHERE uid = 'Wilson' 

if __name__ == '__main__':
    app.run()
