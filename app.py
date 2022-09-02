# -*- coding: utf-8 -*-
"""
Created on Fri Sep  2 18:03:05 2022
@author: 李欣諭 Haley, email:fidhaley@gmail.com
"""
# encoding: utf-8
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import pyimgur
from rembg import remove
from PIL import Image
import time, random
from serpapi import GoogleSearch
import requests
from bs4 import BeautifulSoup
app = Flask(__name__)

# you can replace by load env file
handler = WebhookHandler('Your_Channel_Secret') #Your_Channel_Secret
line_bot_api = LineBotApi('Your_Channel_Access_Token') #Your_Channel_Access_Token


@app.route('/')
def index():
    return "<p>圖片救星!</p>"

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

#Echo回應，學你說話
#設定pyimgur
client_id='imgur申請後的ID' #imgur申請後的ID
def glucose_graph(client_id, imgpath):
    im = pyimgur.Imgur(client_id)
    upload_image = im.upload_image(imgpath, title="Uploaded with PyImgur")
    return upload_image.link
#設定去背function
def rembgo(input_path,output_path):
    input = Image.open(input_path)
    output = remove(input)
    output.save(output_path)
    return output.size
#設定圖片縮放function
def resize(path,out_path,width):
    new=Image.open(path)
    print(new.size)
    ratio=float(width)/new.size[0] #計算出寬被放大的比例
    height=int(new.size[1]*ratio) #高乘以相同放大的比例
    newimage=new.resize((width,height),Image.NEAREST) #NEAREST最近鄰居差值法，BILINEAR雙線性差值法
    print(newimage.size)
    newimage.save(out_path)
    return newimage.size
#設定獲取圖片大小function
def sizeimg(input_path):
    img=Image.open(input_path)
    return img.size
#設定文字搜圖清晰版function，需要先登入得到(api key)https://serpapi.com/users/sign_in
def search_img_better(msg):
    URL_list = []
    try:
        params = {
                "engine": "google",
                "tbm": "isch",
                "api_key": "需要先登入得到(api key)https://serpapi.com/users/sign_in",
                }
        params['q'] = msg
        client = GoogleSearch(params)
        data = client.get_dict()
        imgs = data['images_results']
        x = 0
        for img in imgs:
            if x < 5:
                URL_list.append(img['original'])
                x += 1
    except:
        url = 'https://www.google.com.tw/search?q=' + \
        msg+'&tbm=isch'
        request = requests.get(url=url)
        html = request.content
        bsObj = BeautifulSoup(html, 'html.parser')
        content = bsObj.findAll('img', {'class': 't0fcAb'})
        for i in content:
            URL_list.append(i['src'])
    url = random.choice(URL_list)
    print(url)
    return url
# ========== handle user message ==========
@handler.add(MessageEvent)  
def handle_message(event):
    #用戶傳送圖片指令區
    if event.message.type=='image':
        image_content = line_bot_api.get_message_content(event.message.id) #獲取圖片資訊
        #存圖片
        path=f'/tmp/+tmp.jpg'
        with open(path,'wb') as file:
            for c in image_content.iter_content():
                file.write(c)              
        path_out=f'/tmp/rem_tmp.png'
        remsize=rembgo(path,path_out)
        print(remsize)
        #去背完成
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='圖片傳送成功!請選擇去背饅頭或縮放饅頭進行下一步動作'))
        print(image_content)

    #用戶傳送文字指令區
    elif isinstance(event.message, TextMessage):
        msg=event.message.text #存下輸入的文字資訊
        #回復傳入的訊息文字
        if msg == '圖片救星解說':
            f='''歡迎來到圖片救星~~~\n以下為使用說明:\n我們提供圖片去背、圖片縮放以及文字搜圖三種功能\n要使用圖片去背及圖片縮放功能，請先上傳一張圖片(注意:上傳多張圖片將只會處理最後一張)\n上傳圖片完成後，即可透過選單選擇"去背饅頭"或"縮放饅頭"\n如果你比較喜歡文字遊戲XD~\n可以直接輸入(xxxx為圖片寬度，請輸入100到2048之間的數值):
                1. 去背饅頭
                2. 縮放原圖xxxx
                3. 縮放去背xxxx\n文字搜圖功能請直接輸入(xxxx為你想搜尋的物品):
                4. 搜尋xxxx'''
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f))
        elif msg == '去背饅頭':
            remi=TextSendMessage(sender=Sender(
                    name="去背饅頭",
                    icon_url="https://i.imgur.com/fUC9pBV.png"),
                    text='圖片去背中...')
            rempath=f'/tmp/rem_tmp.png'
            time.sleep(2)
            img_url = glucose_graph(client_id, rempath)
            print(img_url)
            remi2=TemplateSendMessage(sender=Sender(
                    name="去背饅頭",
                    icon_url="https://i.imgur.com/fUC9pBV.png"),
                    alt_text='Buttons template',
                    template=ButtonsTemplate(
                        title='去背圖片',
                        text='圖片大小:'+str(sizeimg(rempath)),
                        thumbnail_image_url= img_url,
                        actions=[
                            MessageTemplateAction(
                                label='下載jpg', #欲呈現的文字
                                text= '去背jpg檔:'+ img_url
                            ),
                            URITemplateAction(
                                label='png圖片網址', #欲呈現的文字
                                uri= img_url #連結的網址
                                )]))                        
            remT=[remi,remi2]
            line_bot_api.reply_message(event.reply_token, remT)
        elif msg[:6] == '去背jpg檔':
            remi=ImageSendMessage(sender=Sender(
                    name="去背饅頭",
                    icon_url="https://i.imgur.com/fUC9pBV.png"),
                    original_content_url = msg[7:], preview_image_url = msg[7:])
            line_bot_api.reply_message(event.reply_token, remi)
        elif msg == '縮放饅頭':
            resi=TextSendMessage(sender=Sender(
                    name="縮放饅頭",
                    icon_url="https://i.imgur.com/1NDry3o.png"),
                    text='請輸入(縮放原圖xxxx/縮放去背xxxx)xxxx為圖片寬度數值介於100到2048，例如:縮放原圖1024')
            line_bot_api.reply_message(event.reply_token, resi)
        elif msg[:4]== '縮放原圖':
            pathin=f'/tmp/+tmp.jpg'
            outp=f'/tmp/resize_+tmp.png'
            width=int(msg[4:])
            size=str(resize(pathin,outp,width))
            sendT=TextSendMessage(sender=Sender(
                    name="縮放饅頭",
                    icon_url="https://i.imgur.com/1NDry3o.png"),text=size)
            time.sleep(2)
            img_urlorg = glucose_graph(client_id, outp)
            print(img_urlorg)
            sendI=ImageSendMessage(sender=Sender(
                    name="縮放饅頭",
                    icon_url="https://i.imgur.com/1NDry3o.png"),
                    original_content_url = img_urlorg, preview_image_url = img_urlorg)
            url=TextSendMessage(sender=Sender(
                    name="縮放饅頭",
                    icon_url="https://i.imgur.com/1NDry3o.png"),text=img_urlorg)
            messages=[sendI, sendT,url]
            line_bot_api.reply_message(event.reply_token, messages)
        elif msg[:4]== '縮放去背':
            pathin=f'/tmp/rem_tmp.png'
            outp=f'/tmp/resize_rem_tmp.png'
            width=int(msg[4:])
            size=str(resize(pathin,outp,width))
            sendT=TextSendMessage(sender=Sender(
                    name="縮放饅頭",
                    icon_url="https://i.imgur.com/1NDry3o.png"),text=size)
            time.sleep(2)
            img_urlrem = glucose_graph(client_id, outp)
            print(img_urlrem)
            sendI=ImageSendMessage(sender=Sender(
                    name="縮放饅頭",
                    icon_url="https://i.imgur.com/1NDry3o.png"),
                    original_content_url = img_urlrem, preview_image_url = img_urlrem)
            url=TextSendMessage(sender=Sender(
                    name="縮放饅頭",
                    icon_url="https://i.imgur.com/1NDry3o.png"),text=img_urlrem)
            messages=[sendI, sendT,url]
            line_bot_api.reply_message(event.reply_token, messages)
        elif msg == '搜尋饅頭':
            searchi=TextSendMessage(sender=Sender(
                    name="搜尋饅頭",
                    icon_url="https://i.imgur.com/ptniNHM.png"),
                    text='請輸入:搜尋xxx，例如:搜尋line')
            line_bot_api.reply_message(event.reply_token, searchi)
        elif msg[:2] == '搜尋':
            message1 = TextSendMessage(
                text=f"以下為\"{msg[2:]}\"的搜尋結果...",
                sender=Sender(
                    name="搜尋饅頭Google",
                    icon_url="https://storage.googleapis.com/support-kms-prod/ZAl1gIwyUsvfwxoW9ns47iJFioHXODBbIkrK")
                )
            url=search_img_better(str(msg[2:]))
            if url[:5]=='https':
                message2 = ImageSendMessage(sender=Sender(
                    name="搜尋饅頭Google",
                    icon_url="https://storage.googleapis.com/support-kms-prod/ZAl1gIwyUsvfwxoW9ns47iJFioHXODBbIkrK"),
                    original_content_url=url, preview_image_url=url
                    )
            else:
                message2=TextSendMessage(
                    text="哦...圖片害羞了，請直接看網站XD",
                    sender=Sender(
                        name="搜尋饅頭Google",
                        icon_url="https://storage.googleapis.com/support-kms-prod/ZAl1gIwyUsvfwxoW9ns47iJFioHXODBbIkrK")
                    )
            urllink=TextSendMessage(
                text=url,
                sender=Sender(
                    name="搜尋饅頭Google",
                    icon_url="https://storage.googleapis.com/support-kms-prod/ZAl1gIwyUsvfwxoW9ns47iJFioHXODBbIkrK")
                    )
            messages=[message1, message2,urllink]
            line_bot_api.reply_message(event.reply_token, messages)
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=msg))


    


import os
if __name__ == "__main__":
    #app.run(host='0.0.0.0', port=3000)
    app.run(host='0.0.0.0', port=os.environ['PORT'])