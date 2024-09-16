import os
import json
import time,datetime
import httpx as requests
from pytz import timezone

# 前言,这里用不到的函数可以不定义,可以直接删去,包括API也可以删去不定义,不会报错的

flora_api = {}  # 顾名思义,FloraBot的API,载入(若插件已设为禁用则不载入)后会赋值上
timeout=requests.Timeout(10.0,connect=20.0,read=15.0)
header={
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36 Edg/89.0.774.54",
    "Content-Type": "application/json"
}
post_json={
    "size": ["original","regular"]
}


def occupying_function(*values):  # 该函数仅用于占位,并没有任何意义
    pass


send_msg = occupying_function


def init():  # 插件初始化函数,在载入(若插件已设为禁用则不载入)或启用插件时会调用一次,API可能没有那么快更新,可等待,无传入参数
    global send_msg
    print(flora_api)
    send_msg = flora_api.get("SendMsg")
    print("Lolicon 加载成功")


def api_update_event():  # 在API更新时会调用一次(若插件已设为禁用则不调用),可及时获得最新的API内容,无传入参数
    #print(flora_api)
    try:
        os.rmdir(f"./{flora_api.get('ThePluginPath')}/temp")
    except:
        pass
    pass


def event(data: dict):  # 事件函数,FloraBot每收到一个事件都会调用这个函数(若插件已设为禁用则不调用),传入原消息JSON参数
    print(data)
    uid = data.get("user_id")  # 事件对象QQ号
    gid = data.get("group_id")  # 事件对象群号
    mid = data.get("message_id")  # 消息ID
    msg = data.get("raw_message")  # 消息内容
    try:
        global ws_client
        global ws_server
        send_address = data.get("SendAddress")
        ws_client = send_address.get("WebSocketClient")
        ws_server = send_address.get("WebSocketServer")
    except:
        ws_server=None
        ws_client=None
        pass
    # 处理消息
    if msg is not None:
        msg = msg.replace("&#91;", "[").replace("&#93;", "]").replace("&amp;", "&").replace("&#44;", ",")  # 消息需要将URL编码替换到正确内容
        #print(uid, gid, mid, msg)
        if msg == ".lolitest":
            r=requests.get("https://net.lolicon.app/detail",headers=header)
            print(r.text)
        message=msg.split(" ")
        print(message)
        api="https://api.lolicon.app/setu/v2"
        #转小写
        if message[0] == "lolicon":
            api_flags = {}
            api_flags.clear()
            api_flags=post_json.copy()
            num=1
            begins=1
            ifail=False
            mutil=False
            tags=[]
            uids=[]
            try:
                a=int(message[1])
            except:
                ifail=True
                api_flags["num"]=num
            finally:
                if not ifail and a <= 20 and a > 0 :
                    begins=2
                    if gid is None:
                        mutil=True
                        api_flags["num"]=a
                        send_compatible(msg="准备获取多张图片",uid=uid,gid=gid,mid=mid)
                    else:
                        send_compatible(msg="为防止群聊刷屏，已禁用发送多张图片",uid=uid,gid=gid,mid=mid)
            rate18_set=False
            try:
                for i in range(begins,len(message)): # 遍历参数
                    if gid is None: # 私聊检测,然后再确认tag内容是否设置了r18需求
                        if rate18_set and message[i].lower() in ["adultonly","adult-only","r18","r-18"] : # 如果已经设置r18参数，则跳过# 
                            continue
                        elif message[i].lower() in ["adultonly","adult-only"]: # 设置r18参数（只发送r18）
                            rate18_set=True
                            api_flags["r18"]=1
                            continue
                        elif message[i].lower() in ["r18","r-18"]: # 设置r18参数（混入r18）
                            rate18_set=True
                            api_flags["r18"]=2
                            continue
                    if message[i].lower() in ["noai","no-ai"]: # 屏蔽AI图
                        api_flags["excludeAI"]=True
                        continue
                    elif message[i].lower().startswith("uid") is True: # 添加UID
                        uids.append(message[i][3:])
                        continue
                    tags.append(message[i]) # 添加tag
            finally:
                api_flags["tag"]=tags
                api_flags["uid"]=uids
                print(json.dumps(api_flags,ensure_ascii=False))
                fail=False
                
                try:
                    results=requests.post(api,data=json.dumps(api_flags,ensure_ascii=False),timeout=timeout,headers=header)
                except:
                    fail=True
                    send_compatible(msg=f"[CQ:at,qq={uid}]\n获取失败,也许是api调用限制问题,稍后可重新获取qwq",uid=uid,gid=gid,mid=mid)
                    raise
                if fail:
                    return
                #print(results.text)
                resulted=json.loads(results.text)
                if len(resulted['data']) == 0: # 没有找到图片（数组为空）
                    send_compatible(msg=f"[CQ:at,qq={uid}]\n没有找到图片，你的需求似乎很奇怪呢～",uid=uid,gid=gid,mid=mid)
                #print(resulted)
            for i in range(0,len(resulted['data'])):
                #print(i)
                datas=parse_data(resulted['data'][i])
                #print(datas)
                texts=f"NO.{i+1} PID:{datas['pid']} p{str(datas['p'])}\n标题：{datas['title']}\n上传时间:{datas['date']}\n作者：{datas['author']} UID:{datas['uid']}\nR18:{datas['r18']} AI:{datas['aitype']}\n标签：{datas['tags']}\n原图链接：{datas['original_url']}"
                time.sleep(1)
                if i==0:
                    send_compatible(msg=f"获取成功，正在发送(共{str(len(resulted['data']))}张)",uid=uid,gid=gid,mid=mid)
                send_compatible(msg=f"[CQ:image,file={datas['regular_url']}]\n{texts}",uid=uid,gid=gid)

def parse_data(data: dict): #解析数据函数
    #print(data)
    tzc=timezone("Asia/Shanghai")
    tags=data["tags"]
    text_tag=""
    choices=["未知","否","是"]
    ai_text=choices[data["aiType"]]
    time=float(data['uploadDate']) /1000
    time=datetime.datetime.fromtimestamp(time)
    time_formated=time.astimezone(tzc).strftime("%Y-%m-%d %H:%M:%S (%Z)")
    for i in range(0,len(tags)):
        if i == 0:
            text_tag=f"{tags[i]}"
        else:
            text_tag+=f",{tags[i]}"
    if data["r18"] is True:
        r18_type=choices[2]
    else:
        r18_type=choices[1]
    return {
        "pid": data["pid"],
        "p": data["p"],
        "uid": data["uid"],
        "title": data["title"],
        "author": data["author"],
        "date": time_formated,
        "r18": r18_type,
        "tags": text_tag,
        "aitype": ai_text,
        "original_url": data["urls"]["original"],
        "regular_url": data["urls"]["regular"]
    }
def send_compatible(msg:str,uid:str|int,gid: str|int,mid:int|str=None):  #兼容性函数,用于兼容旧版本API(请直接调用本函数)
    if flora_api.get("FloraVersion") == 'v1.01': #旧版本API
        send_msg(msg=msg,gid=gid,uid=uid,mid=mid)
    else:
        send_type=flora_api.get("ConnectionType") # 获取连接类型
        send_address=flora_api.get("FrameworkAddress")
        send_msg(msg=msg,gid=gid,uid=uid,mid=mid,send_type=send_type,ws_client=ws_client,ws_server=ws_server)