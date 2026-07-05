"""微信公众号（测试号）接入：Webhook 回调 -> Agent 应答。

使用：
1. 注册测试号 https://mp.weixin.qq.com/debug/cgi-bin/sandboxinfo
2. python wechat_official_bot.py 启动服务（默认 5000 端口）
3. ngrok http 5000 获取公网地址，将 {地址}/wechat 与 Token 填入测试号接口配置
"""
import hashlib
import os
import time
import xml.etree.ElementTree as ET

from flask import Flask, request

import config
import rag
from agent import run_agent

TOKEN = os.getenv("WECHAT_TOKEN", "myagent2026")

app = Flask(__name__)
sessions: dict[str, list] = {}  # openid -> 对话历史


def check_signature() -> bool:
    """校验请求来自微信服务器（官方 SHA1 验签算法）。"""
    signature = request.args.get("signature", "")
    timestamp = request.args.get("timestamp", "")
    nonce = request.args.get("nonce", "")
    raw = "".join(sorted([TOKEN, timestamp, nonce]))
    return hashlib.sha1(raw.encode()).hexdigest() == signature


def build_reply_xml(to_user: str, from_user: str, content: str) -> str:
    return f"""<xml>
<ToUserName><![CDATA[{to_user}]]></ToUserName>
<FromUserName><![CDATA[{from_user}]]></FromUserName>
<CreateTime>{int(time.time())}</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[{content}]]></Content>
</xml>"""


@app.route("/wechat", methods=["GET", "POST"])
def wechat():
    if not check_signature():
        return "invalid signature", 403

    if request.method == "GET":  # 接口配置验证
        return request.args.get("echostr", "")

    msg = ET.fromstring(request.data)
    user_openid = msg.find("FromUserName").text
    account_id = msg.find("ToUserName").text

    if msg.find("MsgType").text != "text":
        answer = "目前仅支持文字消息，请用文字描述您的问题~"
    else:
        text = msg.find("Content").text.strip()
        try:
            answer, sessions[user_openid] = run_agent(text, sessions.get(user_openid))
        except Exception as e:
            print(f"[error] {e}")
            answer = "系统繁忙，请稍后再试~"

    return build_reply_xml(user_openid, account_id, answer)


if __name__ == "__main__":
    if not config.API_KEY:
        print("请先设置环境变量 DASHSCOPE_API_KEY")
    else:
        rag.build_index()
        app.run(host="0.0.0.0", port=5000)
