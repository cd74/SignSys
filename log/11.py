import csv
import time
with open('login.csv','a',newline='')as f:
    fieldnames =  {'uid','name','time','ip','result','type'}
    uid='11'
    tim=time.strftime('%Y%m%d %H %M %S',time.localtime())
    data = {'uid':uid,'name':' ','time':tim,'result':'1'}
    writer = csv.DictWriter(f,fieldnames=fieldnames)
    writer.writeheader()
    writer.writerow(data)