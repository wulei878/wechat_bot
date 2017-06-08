#! /usr/bin/env python
# coding=utf-8
import time
import os
import sched
import datetime
import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header

SECONDS_PER_DAY = 24 * 60 * 60

schedule = sched.scheduler(time.time, time.sleep)
mailto_list = ['shiran@aiztone.com', 'huqitong@aiztone.com', 'zhangzhiliang@aiztone.com']
mail_host = "smtp.exmail.qq.com"  # 设置服务器
mail_user = "wulei"  # 用户名
mail_pass = "Wulei8701"  # 口令
mail_postfix = "aiztone.com"  # 发件箱的后缀


def perform_command(cmd, inc):
    # 安排inc秒后再次运行自己，即周期运行
    schedule.enter(inc, 0, perform_command, (cmd, inc))
    scheduleJob()


def timming_exe(cmd, inc=60):
    # enter用来安排某事件的发生时间，从现在起第n秒开始启动
    schedule.enter(inc, 0, perform_command, (cmd, inc))
    # 持续运行，直到计划时间队列变成空为止
    schedule.run()


def traverseFolder(rootdir):
    # 三个参数：分别返回1.父目录 2.所有文件夹名字（不含路径） 3.所有文件名字
    for parent, dirnames, filenames in os.walk(rootdir):
        # 输出文件夹信息
        for dirname in dirnames:
            if dirname == 'unknown':
                continue
            inputFile = open(reportFileName, 'a')
            inputFile.write('\n' + '--------------' +
                            dirname + '--------------' + '\n')
            for subParent, subDirnames, subFilenames in os.walk(os.path.join(rootdir, dirname)):
                for subFilename in subFilenames:
                    if subFilename == 'share_link' + yesterday + '.txt':
                        inputFile.write(
                            '\n' + '----' + 'sharedLinks' + '----' + '\n')
                        outputFile = open(os.path.join(
                            subParent, subFilename), 'r')
                        allLines = outputFile.readlines()
                        for eachLine in allLines:
                            inputFile.write(eachLine)
                        outputFile.close()
                    elif subFilename == 'hot_keyword' + yesterday + '.txt':
                        inputFile.write(
                            '\n' + '----' + 'keyword' + '----' + '\n')
                        outputFile = open(os.path.join(
                            subParent, subFilename), 'r')
                        allLines = outputFile.readlines()
                        allKeywords = ''
                        for eachLine in allLines:
                            allKeywords += eachLine
                        allKeywords = removePrepositions(allKeywords)
                        inputFile.write(allKeywords)
                        outputFile.close()
            inputFile.close()


def send_mail(to_list, sub, content):
    me = "吴磊" + "<" + mail_user + "@" + mail_postfix + ">"
    msg = MIMEMultipart()
    msg['Subject'] = sub
    msg['From'] = me
    msg['To'] = ";".join(to_list)
    msg.attach(MIMEText(content, 'plain', 'utf-8'))
    # 构造附件
    att = MIMEText(open(reportFileName, 'rb').read(), 'base64', 'utf-8')
    att["Content-Type"] = 'application/octet-stream'
    fileName = 'wechat_report' + yesterday + '.txt'
    att["Content-Disposition"] = 'attachment; filename="' + fileName + '"'
    msg.attach(att)
    try:
        server = smtplib.SMTP()
        server.connect(mail_host)
        server.login(mail_user + "@" + mail_postfix, mail_pass)
        server.sendmail(me, to_list, msg.as_string())
        server.close()
        return True
    except Exception as e:
        print('' + str(e))
        return False


def send_mail_with_image(to_list, sub, fileName):
    me = "微信机器人" + "<" + mail_user + "@" + mail_postfix + ">"
    msg = MIMEMultipart()
    msg['Subject'] = sub
    msg['From'] = me
    msg['To'] = ";".join(to_list)
    mail_msg = """
	<p>请扫描下方二维码登录：</p>
	<p><img src="cid:image1"></p>
	"""
    msg.attach(MIMEText(mail_msg, 'html', 'utf-8'))
    fp = open(fileName, 'rb')
    msgImage = MIMEImage(fp.read())
    fp.close()
    msgImage.add_header('Content-ID', '<image1>')
    msg.attach(msgImage)
    try:
        server = smtplib.SMTP()
        server.connect(mail_host)
        server.login(mail_user + "@" + mail_postfix, mail_pass)
        server.sendmail(me, to_list, msg.as_string())
        server.close()
        return True
    except Exception as e:
        print('' + str(e))
        return False


def timeToSleep():
    from datetime import datetime, timedelta
    curTime = datetime.now()
    desTime = curTime.replace(hour=10, minute=0, second=0, microsecond=0)
    delta = (desTime - curTime).total_seconds()
    skipSeconds = 0
    if delta > 0:
        skipSeconds = delta
    else:
        skipSeconds = SECONDS_PER_DAY + delta
    hour = skipSeconds / 60 / 60
    minute = skipSeconds % 3600 / 60
    seconds = skipSeconds % 3600 % 60
    print(skipSeconds)
    print("Must sleep %d hour %d minute %d second" % (hour, minute, seconds))
    return skipSeconds


def scheduleJob(cmd, inc):
    # print 'do the job'
    congfigParam()
    traverseFolder(os.getcwd() + '/records')
    send_mail(mailto_list, 'wechat_report' + yesterday, 'wechat_report' + yesterday)
    schedule.enter(inc, 0, scheduleJob, (cmd, inc))
    schedule.run()


def congfigParam():
    global yesterday
    yesterday = (datetime.datetime.now() -
                 datetime.timedelta(days=1)).strftime('%Y_%m_%d')
    folderPath = os.path.join(os.getcwd(), 'report')
    if not os.path.exists(folderPath):
        os.makedirs(folderPath)
    global reportFileName
    reportFileName = os.path.join(
        folderPath, 'wechat_report' + yesterday + '.txt')


def removePrepositions(content):
    segs = content[:-1].split(',')
    segs = {}.fromkeys(segs).keys()
    final = ','.join(segs)
    return final


def main():
    time.sleep(timeToSleep())
    scheduleJob('', SECONDS_PER_DAY)


if __name__ == '__main__':
    main()
