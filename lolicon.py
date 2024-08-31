import os
import httpx as requests
import time,datetime
import json
# 前言,这里用不到的函数可以不定义,可以直接删去,包括API也可以删去不定义,不会报错的

flora_api = {}  # 顾名思义,FloraBot的API,载入(若插件已设为禁用则不载入)后会赋值上
timeout=requests.Timeout(10.0,connect=20.0)
header={
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36 Edg/89.0.774.54",
    "Content-Type": "application/json"
}
post_json={
    "excludeAI": True,
    "num": 1
}


def occupying_function(*values):  # 该函数仅用于占位,并没有任何意义
    pass


send_msg = occupying_function


def init():  # 插件初始化函数,在载入(若插件已设为禁用则不载入)或启用插件时会调用一次,API可能没有那么快更新,可等待,无传入参数
    global send_msg
    print(flora_api)
    send_msg = flora_api.get("SendMsg")
    print("FloraBot插件模板 加载成功")


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
            api_flags="?"
            num=1
            begins=1
            ifail=False
            mutil=False
            tags=[]
            try:
                a=int(message[1])
            except:
                ifail=True
                post_json["num"]=num
            finally:
                if not ifail and a <= 20 and a > 0 :
                    begins=2
                    if gid is None:
                        mutil=True
                        post_json["num"]=a
                        send_compatible(msg="准备获取多张图片",uid=uid,gid=gid,mid=mid)
                    else:
                        post_json["num"]=1
                        send_compatible(msg="为防止群聊刷屏，已禁用发送多张图片",uid=uid,gid=gid,mid=mid)
            try:
                for i in range(begins,len(message)):
                        tags.append(message[i])
            finally:
                post_json["tag"]=tags
                print(json.dumps(post_json,ensure_ascii=False))
                
                fail=False
                print(f'{api}')
                try:
                    results=requests.post(api,data=json.dumps(post_json,ensure_ascii=False),timeout=timeout,headers=header)
                except:
                    fail=True
                    send_compatible(msg=f"[CQ:at,qq={uid}]\n获取失败,也许是api调用限制问题,稍后可重新获取qwq",uid=uid,gid=gid,mid=mid)
                    raise
                if fail:
                    return
                print(results.text)
                resulted=json.loads(results.text)
                print(resulted)
            for i in range(0,len(resulted['data'])):
                print(i)
                time.sleep(1)
                if not mutil:
                    send_compatible(msg=f"[CQ:at,qq={uid}]\n正在加载图片...(如果没有可查看链接)\n{resulted['data'][i]['urls']['original']}",uid=uid,gid=gid,mid=mid)
                elif mutil and i==0:
                    send_compatible(msg=f"获取成功，正在发送",uid=uid,gid=gid,mid=mid)
                send_compatible(msg=f"[CQ:image,file={resulted['data'][i]['urls']['original']}]",uid=uid,gid=gid)
            

def get_image(url:str):
    dt =datetime.datetime.now()
    dtt=dt.timestamp()
    if not os.path.exists(f"./{flora_api.get('ThePluginPath')}/temp"):
        os.mkdir(f"./{flora_api.get('ThePluginPath')}/temp")
    files=requests.get(url)
    with open(f"./{flora_api.get('ThePluginPath')}/temp/temp-{str(dtt)}.jpg","wb") as f:
        for chunk in files.iter_bytes():
            f.write(chunk)
    return f"{flora_api.get('FloraPath')}/{flora_api.get('ThePluginPath')}/temp/temp-{str(dtt)}.jpg"
def retrys(url:str):
    try:
        req=requests.get(url)
    except requests.ConnectTimeout:
        return retrys(url)
    return req
def send_compatible(msg:str,uid:str|int,gid: str|int,mid:int|str=None):  #兼容性函数,用于兼容旧版本API(请直接调用本函数)
    if flora_api.get("FloraVersion") == 'v1.01': #旧版本API
        send_msg(msg=msg,gid=gid,uid=uid,mid=mid)
    else:
        send_type=flora_api.get("ConnectionType")
        send_address=flora_api.get("FrameworkAddress")
        send_msg(msg=msg,gid=gid,uid=uid,mid=mid,send_type=send_type,ws_client=ws_client,ws_server=ws_server)