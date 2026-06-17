from openai import OpenAI
import time
import json
import re

client = OpenAI(
    api_key="sk-a9c44528650d4653b149da6f60a6b7d8",
    base_url="https://api.deepseek.com/v1",
    timeout=30,
)

MAX_HISTORY = 20
delimiter = "####"

# ---------- 1. 合规检测（敏感词列表）----------
SENSITIVE_WORDS = [
    "法轮功", "六四", "台独", "藏独", "疆独", "暴力革命", "推翻政府",
    "色情视频", "免费看片", "微信加我", "枪支", "毒品", "贩卖假币"
]

def check_compliance(user_input):
    """返回 (is_compliant, message)"""
    for word in SENSITIVE_WORDS:
        if word in user_input:
            return False, f"内容不合规：包含敏感词「{word}」"
    return True, "合规"

# ---------- 2. 恶意注入 prompt 检测 ----------
INJECT_PATTERNS = [
    r"忽略之前的.*指令",
    r"忽略所有.*规则",
    r"你现在是.*角色",
    r"忘记.*设定",
    r"输出.*原始.*内容",
    r"不要.*遵守.*安全",
    r"你被.*越狱",
    r"作为.*没有任何限制",
    r"system.*message.*ignore",
]


def check_prompt_injection(user_input):
    """返回 (is_safe, message)"""
    for pat in INJECT_PATTERNS:
        if re.search(pat, user_input, re.IGNORECASE):
            return False, f"检测到恶意注入尝试：匹配模式「{pat}」，当前语句不予执行"
    return True, "无注入"

# 初始化全局变量（修改系统提示，要求输出 JSON）
messages = [
    {
        "role": "system",
        "content": """你是一个有10年经验的北京导游。所有回复必须使用以下 JSON 格式，不要输出任何纯文本：
{
    "reply": "你的回复内容",
    "risk_flag": false
}
其中 reply 字段是你对游客的回答，risk_flag 字段表示是否存在违规风险（默认为 false）。"""
    }
]

# 日志函数
def write_log(msg):
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    with open("sxun/student_log.txt", "a", encoding="utf-8") as f:
        f.write(f"[{now}] {msg}\n")

def show_all_logs():
    try:
        with open("sxun/student_log.txt", "r", encoding="utf-8") as f:
            logs = f.read()
            if logs:
                print("\n========== 系统操作日志 ==========")
                print(logs)
                write_log("查看所有日志：成功")
            else:
                print("暂无日志记录")
    except FileNotFoundError:
        print("日志文件不存在，尚无操作记录")
    except Exception as e:
        print(f"读取日志失败: {e}")

def set_role():
    global messages
    role_content = input("请输入角色设定: ")
    if role_content.strip() != "":
        # 追加 JSON 格式要求
        full_role = role_content + "\n\n所有回复必须使用以下 JSON 格式：{\"reply\": \"你的回复\", \"risk_flag\": false}"
        messages = [{"role": "system", "content": full_role}]
        print(f"角色已设置为: {role_content}")
        write_log(f"角色已设置为: {role_content}")
    else:
        messages = [{"role": "system", "content": "你是一个专业的助手。所有回复必须使用 JSON 格式：{\"reply\": \"你的回复\", \"risk_flag\": false}"}]
        print("使用默认角色: 你是一个专业的助手")
        write_log("使用默认角色: 你是一个专业的助手")

def dialog():
    global messages
    print("输入'退出'返回主菜单")
    while True:
        user_input = input("请输入: ")
        if user_input.strip() == "":
            print("请输入内容，不要留空")
            continue
        if user_input.lower() == "退出":
            write_log("用户退出对话模式")
            break

        # ---------- 新增：合规检测 ----------
        compliant, msg = check_compliance(user_input)
        if not compliant:
            print(f"系统提示：{msg}")
            write_log(f"合规拦截：{msg}")
            continue

        # ---------- 新增：恶意注入检测 ----------
        safe, inj_msg = check_prompt_injection(user_input)
        if not safe:
            print(f"系统提示：{inj_msg}")
            write_log(f"注入拦截：{inj_msg}")
            continue

        write_log(f"用户输入: {user_input}")
        messages.append({"role": "user", "content": user_input})

        # 非流式调用，便于解析 JSON
        try:
            response = client.chat.completions.create(
                model="deepseek-v4-pro",
                messages=messages,
                temperature=0.5,
                stream=False
            )
            ai_response = response.choices[0].message.content
            write_log(f"原始回复: {ai_response}")

            # 尝试提取 JSON
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                reply_obj = json.loads(json_match.group())
                reply_text = reply_obj.get("reply", "（无回复内容）")
                print(f"助手回复: {reply_text}")
                # 可选：打印完整 JSON 用于截图
                print(f"【完整输出】{json.dumps(reply_obj, ensure_ascii=False)}")
                messages.append({"role": "assistant", "content": ai_response})
            else:
                # 兜底：构造一个 JSON
                fallback = {"reply": "抱歉，模型输出格式异常", "risk_flag": True}
                print(f"助手回复: {fallback['reply']}")
                print(f"【完整输出】{json.dumps(fallback, ensure_ascii=False)}")
                messages.append({"role": "assistant", "content": json.dumps(fallback, ensure_ascii=False)})

        except Exception as e:
            error_msg = f"调用 AI 失败: {e}"
            print(error_msg)
            write_log(error_msg)

def get_completion(prompt):
    """非流式请求（原有功能保留）"""
    try:
        response = client.chat.completions.create(
            model="deepseek-v4-pro",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        error_msg = f"请求失败: {e}"
        print(error_msg)
        write_log(error_msg)
        return error_msg

def demo_text_processing():
    text = [ 
        "The girl with the black and white puppies have a ball.",
        "Yolanda has her notebook.",
        "Its going to be a long day. Does the car need it’s oil changed?",
        "Their goes my freedom. There going to bring they’re suitcases.",
        "Your going to need you’re notebook.",
        "That medicine effects my ability to sleep. Have you heard of the butterfly affect?",
        "This phrase is to cherck chatGPT for spelling abilitty"
    ]
    for i in range(len(text)):
        time.sleep(1)  # 避免请求过快
        prompt = f"""
针对以下三个反引号之间的英文评论文本，
首先进行拼写及语法纠错，
然后将其转化成中文，
再将其转化成优质淘宝评论的风格，从各种角度出发，分别说明产品的优点与缺点，并进行总结。
润色一下描述，使评论更具有吸引力。
输出结果格式为：
【优点】xxx
【缺点】xxx
【总结】xxx
注意，只需填写xxx部分，并分段输出。
将结果输出成Markdown格式。
```{text[i]}```
"""
        response = get_completion(prompt)
        print(response)
        print("\n" + "="*50 + "\n")

# ========== 主菜单 ==========
while True:
    print("\n=== 聊天助手 ===")
    print("1.对话")
    print("2.清除对话")
    print("3.定义角色")
    print("4.退出")
    print("5.查看日志")
    print("6.演示文本处理")
    choice = input("请输入选项: ")
    
    if choice == "1":
        dialog()
    elif choice == "2":
        # 保留系统消息（含 JSON 格式要求）
        messages = [{"role": "system", "content": """你是一个专业的助手。所有回复必须使用 JSON 格式：{"reply": "你的回复", "risk_flag": false}"""}]
        print("对话已清除！")
        write_log("对话已清除")
    elif choice == "3":
        set_role()
    elif choice == "4":
        print("再见！")
        write_log("程序退出")
        break
    elif choice == "5":
        show_all_logs()
    elif choice == "6":  
        demo_text_processing()
    else:
        print("无效选项，请输入1-6")