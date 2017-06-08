#!/usr/bin/env python
# coding: utf-8

from wxbot import *
import os, shutil, datetime, re, jieba
import scheduleTask

RECORD_FOLDER = "records"
TEXT_NAME = "record_base"

stopwordsArray = ['a', 'about', 'above', 'above', 'across', 'after', 'afterwards', 'again',
                  'against', 'all', 'almost', 'alone', 'along', 'already', 'also', 'although',
                  'always', 'am', 'among', 'amongst', 'amoungst', 'amount', 'an', 'and', 'another',
                  'any', 'anyhow', 'anyone', 'anything', 'anyway', 'anywhere', 'are', 'around', 'as',
                  'at', 'back', 'be', 'became', 'because', 'become', 'becomes', 'becoming', 'been',
                  'before', 'beforehand', 'behind', 'being', 'below', 'beside', 'besides',
                  'between', 'beyond', 'bill', 'both', 'bottom', 'but', 'by', 'call', 'can',
                  'cannot', 'cant', 'co', 'con', 'could', 'couldnt', 'cry', 'de', 'describe',
                  'detail', 'do', 'done', 'down', 'due', 'during', 'each', 'eg', 'eight',
                  'either', 'eleven', 'else', 'elsewhere', 'empty', 'enough', 'etc', 'even',
                  'ever', 'every', 'everyone', 'everything', 'everywhere', 'except', 'few',
                  'fifteen', 'fify', 'fill', 'find', 'fire', 'first', 'five', 'for', 'former',
                  'formerly', 'forty', 'found', 'four', 'from', 'front', 'full', 'further', 'get',
                  'give', 'go', 'had', 'has', 'hasnt', 'have', 'he', 'hence', 'her', 'here',
                  'hereafter', 'hereby', 'herein', 'hereupon', 'hers', 'herself', 'him',
                  'himself', 'his', 'how', 'however', 'hundred', 'ie', 'if', 'in', 'inc',
                  'indeed', 'interest', 'into', 'is', 'it', 'its', 'itself', 'keep', 'last',
                  'latter', 'latterly', 'least', 'less', 'ltd', 'made', 'many', 'may', 'me',
                  'meanwhile', 'might', 'mill', 'mine', 'more', 'moreover', 'most', 'mostly',
                  'move', 'much', 'must', 'my', 'myself', 'name', 'namely', 'neither', 'never',
                  'nevertheless', 'next', 'nine', 'no', 'nobody', 'none', 'noone', 'nor', 'not',
                  'nothing', 'now', 'nowhere', 'of', 'off', 'often', 'on', 'once', 'one', 'only',
                  'onto', 'or', 'other', 'others', 'otherwise', 'our', 'ours', 'ourselves', 'out',
                  'over', 'own', 'part', 'per', 'perhaps', 'please', 'put', 'rather', 're', 'same',
                  'see', 'seem', 'seemed', 'seeming', 'seems', 'serious', 'several', 'she',
                  'should', 'show', 'side', 'since', 'sincere', 'six', 'sixty', 'so', 'some',
                  'somehow', 'someone', 'something', 'sometime', 'sometimes', 'somewhere',
                  'still', 'such', 'system', 'take', 'ten', 'than', 'that', 'the', 'their',
                  'them', 'themselves', 'then', 'thence', 'there', 'thereafter', 'thereby',
                  'therefore', 'therein', 'thereupon', 'these', 'they', 'thickv', 'thin', 'third',
                  'this', 'those', 'though', 'three', 'through', 'throughout', 'thru', 'thus',
                  'to', 'together', 'too', 'top', 'toward', 'towards', 'twelve', 'twenty', 'two',
                  'un', 'under', 'until', 'up', 'upon', 'us', 'very', 'via', 'was', 'we', 'well',
                  'were', 'what', 'whatever', 'when', 'whence', 'whenever', 'where', 'whereafter',
                  'whereas', 'whereby', 'wherein', 'whereupon', 'wherever', 'whether', 'which',
                  'while', 'whither', 'who', 'whoever', 'whole', 'whom', 'whose', 'why', 'will',
                  'with', 'within', 'without', 'would', 'yet', 'you', 'your', 'yours', 'yourself',
                  'yourselves', 'the', ',', ' ', '.', '-']


class MyWXBot(WXBot):
    def handle_msg_all(self, msg):
        # print (msg)
        self.checkRecordFolder()
        if msg['msg_type_id'] == 3:
            if msg['content']['type'] == 0:
                self.handleGroupTextMessage(msg)
            elif msg['content']['type'] == 4:
                self.handleGroupVoiceMessage(msg)
            elif msg['content']['type'] == 5:
                self.handleGroupCardMessage(msg)
            elif msg['content']['type'] == 7:
                self.handleGroupShareMessage(msg)
            # 被拉入群聊时接收到的消息类型
            elif msg['content']['type'] == 12:
                print(msg['content'])
        # 接收到添加好友的请求时的消息类型
        elif msg['msg_type_id'] == 37:
            self.apply_useradd_requests(msg['content']['data'])
        # self.add_friend_to_group(msg['content']['data']['UserName'],'三人行')
        # 接收到对方同意添加好友的消息类型
        elif msg['msg_type_id'] == 99:
            if msg['content']['type'] == 0:
                pass
            # self.add_friend_to_group(msg['user']['id'],'三人行')
        elif msg['msg_type_id'] == 5:
            print(msg['content']['type'])

    def sendQRCodeEmail(self, content):
        scheduleTask.send_mail_with_image(['296636138@qq.com'], '请重新登录微信机器人账号', content)

    def getRecordFolder(self, msg):
        record_folder = os.path.join(RECORD_FOLDER, msg['user']['id'])
        if not os.path.exists(record_folder):
            os.makedirs(record_folder)
        return record_folder

    def checkRecordFolder(self):
        record_folder = RECORD_FOLDER
        if not os.path.exists(RECORD_FOLDER):
            record_folder = os.makedirs(RECORD_FOLDER)
        return record_folder

    def checkGroupFolder(self, msg):
        if msg['user']['name']:
            groupName = msg['user']['name']
        else:
            groupName = msg['user']['id']
        folderPath = os.path.join(RECORD_FOLDER, groupName)
        if not os.path.exists(folderPath):
            os.makedirs(folderPath)
        return folderPath

    def handleGroupTextMessage(self, msg):
        content = msg['content']['data']
        # print content
        linkMatch = re.search(r'(http|https)://', content, re.IGNORECASE)
        # print linkMatch
        filterResult = re.sub(r'<span[ "=\w]*></span>', '', content)
        keywordMatch = re.search(r'[a-zA-Z]+', filterResult)
        if linkMatch:
            contentPath = os.path.join(self.checkGroupFolder(msg),
                                       'share_link' + datetime.date.today().strftime('%Y_%m_%d') + '.txt')
            f = open(contentPath, 'a')
            f.write(content + '\n')
            f.close()
        elif keywordMatch:
            contentPath = os.path.join(self.checkGroupFolder(msg),
                                       'hot_keyword' + datetime.date.today().strftime('%Y_%m_%d') + '.txt')
            f = open(contentPath, 'a')
            f.write(removePrepositions(filterResult))
            f.close()
        contentPath = os.path.join(self.checkGroupFolder(msg), datetime.date.today().strftime('%Y_%m_%d') + '.txt')
        f = open(contentPath, 'a')
        f.write(msg['content']['user']['name'] + ':\n')
        f.write(content + '\n')
        f.close()

    def handleGroupVoiceMessage(self, msg):
        msg_id = msg['msg_id']
        folderPath = os.path.join(self.temp_pwd, self.get_voice(msg_id))
        timeStamp = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M')
        newName = msg['content']['user']['name'] + '_' + timeStamp + '.mp3'
        os.rename(folderPath, os.path.join(self.temp_pwd, newName))
        shutil.move(os.path.join(self.temp_pwd, newName), self.checkGroupFolder(msg))

    def handleGroupShareMessage(self, msg):
        title = msg['content']['data']['title']
        # desc = msg['content']['data']['desc']
        url = msg['content']['data']['url']
        # webFrom = msg['content']['data']['from']
        contentPath = os.path.join(self.checkGroupFolder(msg),
                                   'share_link' + datetime.date.today().strftime('%Y_%m_%d') + '.txt')
        f = open(contentPath, 'a')
        f.write('title: ' + title + '\n')
        # f.write('desc: '+convertToUTF8(desc) +'\n')
        f.write('link: ' + url + '\n\n')
        # f.write('from: '+convertToUTF8(webFrom)+'\n\n')
        f.close()

    def handleGroupCardMessage(self, msg):
        nickname = msg['content']['data']['nickname']
        alias = msg['content']['data']['alias']
        province = msg['content']['data']['province']
        city = msg['content']['data']['city']
        gender = msg['content']['data']['gender']
        contentPath = os.path.join(self.checkGroupFolder(msg),
                                   'public_card' + datetime.date.today().strftime('%Y_%m_%d') + '.txt')
        f = open(contentPath, 'a')
        f.write('nickname: ' + nickname + '\n')
        f.write('alias: ' + alias + '\n')
        f.write('province: ' + province + '\n')
        f.write('city: ' + city + '\n')
        f.write('gender: ' + gender + '\n\n')
        f.close()

    def get_group_members(self, gid):
        theGroup = {}
        for group in self.group_list:
            if group['NickName'] == gid:
                theGroup = group
                break
        # print (theGroup)
        # print (self.group_members)
        for user in self.group_members[theGroup['UserName']]:
            self.add_groupuser_to_friend_by_uid(user['UserName'], '我是Major')


def removePrepositions(content):
    stopwords = {}.fromkeys(stopwordsArray)
    segs = jieba.cut(content.lower(), cut_all=False)
    final = ''
    for seg in segs:
        if re.search(r'^[^a-zA-Z]*$', seg):
            continue
        # seg = seg.encode('utf-8')
        if seg not in stopwords and len(seg) > 1:
            final += seg + ','
    print(final)
    return final


def convertToUTF8(string):
    return string.encode('utf-8')


def main():
    argv = sys.argv
    isRemoteControl = True
    for i in range(1, len(argv)):
        if i == 1 and argv[i] == '-r':
            isRemoteControl = False
    bot = MyWXBot()
    bot.DEBUG = True
    bot.conf['qr'] = 'png'
    bot.isRemoteControl = isRemoteControl
    bot.run()


# bot.removePrepositions('In Hong Kong, in the 90s, there are 4 heavenly Gods<span class="emoji emoji1f4aa"></span> - Jacky Cheung, Leon Lai, Andy Lau and Aaron Kwok. In the blockchain world, there will be 4 heavenly Blockchains - Bitcoin, Ethereum, ZCash and Qtum lol.')


if __name__ == '__main__':
    main()
