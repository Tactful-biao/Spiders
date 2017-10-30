import smtplib
import time
import datetime
from email.mime.text import MIMEText
from email.utils import formataddr

my_sender = '×××××××××'  # 你的邮箱
my_pass = '×××××××××' # 你邮箱的授权码
my_user = '××××××××××' # 你要发送的目的邮箱
# myuser2 = '××××××××××'  # 可以同时发送给多个用户，只需要添加多个用户即可

# content 是邮件正文内容，subject是邮件主题，time是发送邮件的频率
def sentmail(content, subject, times):  
    ret = True
    try:
        msg = MIMEText(content, 'plain', 'utf-8')
        msg['From'] = formataddr(['BiaoBiao', my_sender])  # 你的发送昵称
        msg['To'] = formataddr(['Biao', my_user])  # 你的接收人昵称
        msg['Subject'] = subject   # 邮件主题
        server = smtplib.SMTP_SSL('smtp.qq.com', 465)
        server.login(my_sender, my_pass)
        server.sendmail(my_sender, [my_user, ], msg.as_string()) # 如果有多个目的邮箱， 只需要在my_user后面添加my_user2即可
        server.quit()
    except Exception:
        ret = False
    with open('./maillog', 'a+') as f:
        if ret:
            f.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')+":邮件发送成功！\n")
        else:
            f.write(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')+":邮件发送失败！\n")
    time.sleep(times)
