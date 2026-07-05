"""个人微信接入（仅 Windows）：基于 wxauto 监听 PC 微信消息 -> Agent 应答。

注意：自动化操作个人微信有账号风控风险，仅用于个人测试；
默认白名单为"文件传输助手"，即给自己发消息自测。
"""
import time

from wxauto import WeChat

import config
import rag
from agent import run_agent

WHITELIST = ["文件传输助手"]
HUMAN_KEYWORDS = ["转人工", "人工", "投诉", "紧急"]
REPLY_INTERVAL = 3
POLL_INTERVAL = 1

sessions: dict[str, list] = {}


def handle_message(chat, who: str, text: str):
    print(f"[recv] {who}: {text}")

    if any(kw in text for kw in HUMAN_KEYWORDS):  # 规则层兜底，不走大模型
        chat.SendMsg("收到~已为您转接人工，客户经理会尽快回复您。")
        return

    try:
        answer, sessions[who] = run_agent(text, sessions.get(who))
    except Exception as e:
        print(f"[error] {e}")
        answer = "系统繁忙，请稍后再试，或回复'转人工'。"

    chat.SendMsg(answer)
    time.sleep(REPLY_INTERVAL)


def main():
    if not config.API_KEY:
        print("请先设置环境变量 DASHSCOPE_API_KEY")
        return

    rag.build_index()
    wx = WeChat()
    for name in WHITELIST:
        wx.AddListenChat(who=name)
        print(f"[listen] {name}")

    while True:
        for chat, msgs in wx.GetListenMessage().items():
            for msg in msgs:
                if msg.type == "friend":
                    handle_message(chat, chat.who, msg.content.strip())
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
