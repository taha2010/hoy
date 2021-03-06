#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import sys
import os
import telepot
from telepot.delegate import per_chat_id, create_open
import re
from random import choice
import BeautifulSoup
#from hazm import *
import urllib2
import subprocess
from time import sleep
from peewee import *
import ast

db = SqliteDatabase(os.environ['OPENSHIFT_DATA_DIR']+'chat.db')
#db = SqliteDatabase('chat.db')
#db = MySQLDatabase('hoy', user=os.environ['OPENSHIFT_MYSQL_DB_USERNAME'],password=os.environ['OPENSHIFT_MYSQL_DB_PASSWORD'], host=os.environ['OPENSHIFT_MYSQL_DB_HOST'])

class User(Model):
    user = CharField()

    class Meta:
        database = db
        
class Hoy(Model):
    hoy = CharField()
    
    class Meta:
        database = db
        
class Chat(Model):
    user = ForeignKeyField(User)
    hoy = ForeignKeyField(Hoy)
    
    class Meta:
        database = db
        
#db.connect()
#db.create_tables([User, Hoy, Chat])

class Babilo(telepot.helper.ChatHandler):
    def __init__(self, seed_tuple, timeout):
        super(Babilo, self).__init__(seed_tuple, timeout)
        
    def on_chat_message(self, msg):
        #if msg.has_key(u'document'):
            #self.sender.downloadFile(msg[u'document'][u'file_id'], file_path="~/dl")
        m = msg['text'].split(' ')
        mr = msg['text']
        fn = msg['from']['first_name']
        chat_type = msg['chat']['type']
        r = ''
        if m[0] == u'/start':
            r = u'سلام به تو که اسمتو گذاشتی ' + unicode(fn)
        elif m[0] == u'mojose':
            r = msg
        if chat_type == 'private' and mr[:3] != u'حوی':
            mr = u'حوی ' + mr 
            m = mr.split(' ')
        
        #TODO merge same outputs
        if '\n' in mr and u'\nبگو\n' in mr:
            mrc = mr[4:]
            mc = mrc.split('\n')
            say_index = mc.index(u'بگو')
            user_inputs = mc[:say_index]
            hoy_outputs = mc[say_index+1:]
            #add outputs > old to new
            hoy_outputs_new = []
            for user_input in user_inputs:
                try:
                    H = (Hoy.select().join(Chat).join(User).where(User.user==user_input))
                    hoy_outputs_old = H[0].hoy
                    h_id = H[0].id
                    #at first add old to new
                    hoy_outputs_new = ast.literal_eval(hoy_outputs_old)
                    del user_input
                except:
                    pass
            if hoy_outputs_new == []:
                h = Hoy.create(hoy=hoy_outputs)
                h.save()
            else:
                for hoy_output in hoy_outputs:
                    if hoy_output not in hoy_outputs_new:
                        hoy_outputs_new.append(hoy_output)
                update_query = Hoy.update(hoy=hoy_outputs_new).where(Hoy.id==h_id)
                update_query.execute()
                h = Hoy.get(Hoy.id==h_id)
            for user_input in user_inputs:
                u = User.create(user=user_input)
                u.save()
                r = Chat.create(user=u, hoy=h)
                r.save()
        elif '\n' in mr and u'\nنگو\n' in mr:
            mrc = mr[4:]
            mc = mrc.split('\n')
            say_index = mc.index(u'نگو')
            user_input = mc[:say_index]
            hoy_output = mc[say_index+1:]
            hoy_outputs_new = []
            try:
                H = (Hoy.select().join(Chat).join(User).where(User.user==user_input))
                hoy_outputs_old = H[0].hoy
                h_id = H[0].id
                #at first add old to new
                hoy_outputs_new = ast.literal_eval(hoy_outputs_old)
            except:
                r = u'چنین چیزی وجود ندارد!'
            del hoy_outputs_new[hoy_outputs_new.index(hoy_output[0])]
            update_query = Hoy.update(hoy=hoy_outputs_new).where(Hoy.id==h_id)
            update_query.execute()
        elif '\n' in mr and u'\nنفهم\n':
            mrc = mr[4:]
            mc = mrc.split('\n')
            say_index = mc.index(u'نفهم')
            user_input = mc[:say_index]
            try:
                dq = User.delete().where(User.user==user_input[0])
                dq.execute()
                #TODO delete u_id that not exist in User, from Chat
            except:
                r = u'چنین چیزی وجود ندارد!'
            
            
                
                
                
        elif m[0] == u'حوی':
            if len(m) >= 3 and m[1] == u'بگو':
                r = mr[8:]
            elif m[1] == u'کمک':
                r = u'• به این شکل حوی را آموزش دهید:\n\
\n\
سلام\n\
درود\n\
بگو\n\
علیک سلام\n\
سلام حاجی\n\
چه سلامی؟\n\
\n\
• اگر به نظرتان حوی چیز اشتباهی گفت، این گونه او را منع کنید تا دیگر چنین چیزی نگوید:\n\
\n\
سلام\n\
نگو\n\
چه سلامی؟\n\
\n\
• اگر فکر می‌کنید چیزی که وارد می‌کنید، یک‌سری پاسخ نامربوط به دنبال دارد و چیزی که حوی می‌گوید باید در پاسخ به ورودی‌های دیگری گفته شود، به صورت زیر، ورودی نامربوط را از پاسخ‌ها جدا کنید. (بعداً می‌توانید آن را به پاسخ‌های مربوط به خود وصل کنید.):\n\
\n\
مثال گپ:\n\
کاربر: خداحافظ\n\
حوی: علیک سلام\n\
\n\
نحوهٔ جدا کردن خداحافظ از پاسخ‌های مربوط به سلام:\n\
\n\
خداحافظ\n\
نفهم\n\
\n\
و در نهایت، مربوط ساختن خداحافظ به پاسخ‌های مربوط:\n\
\n\
خداحافظ\n\
خدانگهدار\n\
بگو\n\
به امید دیدار\n\
از دیدنت خوش‌حال شدم.\n\
\n\
(دقت کنید که در یک پیام و در خط‌های جدا باشد. اگر در گروه آموزشش می‌دهید، ابتدا در یک خط حوی بنویسید و سپس مثل بالا خطوط را وارد کنید.)\n\
! لطفاً در پایان جملهٔ سؤالی از علامت سؤال فارسی (؟) استفاده کنید.'
            elif len(m) == 3:
                m2 = m[1]+' '+m[2]
                if m2 == u'چه خبر؟':
                    response = urllib2.urlopen('http://www.farsnews.com/RSS')
                    rss = response.read()
                    soup = BeautifulSoup.BeautifulSoup(rss)
                    all_title = soup.findAll('title')
                    def get_link(nth):
                        item = soup.findAll('item')[nth]
                        link = re.search(r'http://www.farsnews.com/(\d+)',unicode(item)).group(0)
                        return link
                    r = unicode(all_title[2]).replace('<title>', '<a href="%s">'%get_link(0), 2).replace('</title>', '</a>') + '\n\n' + \
                            unicode(all_title[3]).replace('<title', '<a href="%s"'%get_link(1), 2).replace('</title>', '</a>') + '\n\n' + \
                         unicode(all_title[4]).replace('<title', '<a href="%s"'%get_link(2), 2).replace('</title>', '</a>')
            
            if r == '':
                try:
                    hoy_output = (Hoy.select().join(Chat).join(User).where(User.user==mr[4:]))[0].hoy
                    r = choice(ast.literal_eval(hoy_output))
                except:
                    r = u'نمی‌فهمم چی می‌گی.'
                    
        self.sender.sendMessage(r,parse_mode='HTML')


#TOKEN = sys.argv[1]  # get token from command-line
TOKEN = '238806755:AAH1vINCnTj8Dfka8hl3Qza6ih28xze9PgM'
bot = telepot.DelegatorBot(TOKEN, [
    (per_chat_id(), create_open(Babilo, timeout=1)),
])
#bot = telepot.async.Bot(TOKEN, )
#bot.setWebhook('https://bot-ajor.rhcloud.com')
#bot.notifyOnMessage(run_forever=True)
bot.message_loop(run_forever=True)
