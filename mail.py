import smtplib
import random
from email.mime.text import MIMEText
from email.header import Header
 
# 第三方 SMTP 服务
mail_host="smtp.qq.com"  #设置服务器
mail_user=" "    #用户名
mail_pass=" "   #口令 
 
def send(msg,receiver,sub):
    message = MIMEText(msg, 'plain', 'utf-8')
    message['From'] = Header(mail_user, 'utf-8')
    message['To'] =  Header(receiver, 'utf-8')
    message['Subject'] = Header(sub, 'utf-8')
    
    try:
        smtpObj = smtplib.SMTP() 
        smtpObj.connect(mail_host, 25)    # 25 为 SMTP 端口号
        smtpObj.login(mail_user,mail_pass)
        smtpObj.sendmail(mail_user, receiver, message.as_string())
        return 1
    except smtplib.SMTPException:
        return 0

def sendcode(receiver):
    s=""
    for i in range(1,5): 
        a=random.randint(0,9)
        s+=(str(a))
    if(send(s,receiver,"Registration Confirmation")):
        return s
    else:
        return 0
    
def sendpwd(receiver):
    if():
        sub="Your password"
        send(msg,receiver,sub)
        return 1
    else:
        return 0


if __name__ == "__main__":
    sendcode(" ")
    