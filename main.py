"""命令行入口：python main.py"""
import config
import rag
from agent import run_agent


def main():
    if not config.API_KEY:
        print("请先设置环境变量 DASHSCOPE_API_KEY")
        return

    rag.build_index()
    print("\n===== 金融知识问答 Agent =====")
    print("示例：贷款30万年利率4.5%，每月利息多少？提前还款有什么限制？（输入 q 退出）\n")

    history = None
    while True:
        query = input("你: ").strip()
        if query.lower() in ("q", "quit", "exit"):
            break
        if not query:
            continue
        answer, history = run_agent(query, history)
        print(f"\nAgent: {answer}\n")


if __name__ == "__main__":
    main()
