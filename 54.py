import json
import os
import re
import time
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv
from jsonschema import validate, ValidationError
from jsonschema.exceptions import SchemaError
import xml.etree.ElementTree as ET

# 加载环境变量（.env 文件中需包含 DEEPSEEK_API_KEY）
load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1",
)

# ==================== 完善 get_response 函数 ====================
def get_response(messages: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    发送请求到 DeepSeek API，处理流式响应，提取思考过程和最终 JSON 答案。

    参数:
        messages: 对话消息列表

    返回:
        包含以下字段的字典：
        - reasoning: 模型的思考过程文本
        - answer: 解析后的 JSON 对象（dict）或原始字符串（如果解析失败）
        - raw_answer: 原始回答字符串
        - usage: token 使用统计（如果 API 返回了）
    """
    start = time.time()
    
    # 发送流式请求，启用思考模式，并强制 JSON 输出
    completion = client.chat.completions.create(
        model="deepseek-chat",                # 或 "deepseek-reasoner" 支持思考
        messages=messages,
        stream=True,
        extra_body={"enable_thinking": True}, # 开启思考过程
        response_format={"type": "json_object"}  # 强制输出 JSON 对象
    )
    
    cost = round(time.time() - start, 3)
    print(f"请求耗时：{cost}秒")
    
    reasoning_content = ""      # 思考过程
    answer_content = ""         # 最终回答（原始字符串）
    usage = None
    
    print("\n" + "=" * 20 + "思考过程" + "=" * 20)
    
    for chunk in completion:
        # 处理 usage（通常在最后一个 chunk 中）
        if hasattr(chunk, 'usage') and chunk.usage:
            usage = chunk.usage
            print("\n" + "=" * 20 + "Usage" + "=" * 20)
            print(chunk.usage)
            continue
        
        if not chunk.choices:
            continue
            
        delta = chunk.choices[0].delta
        
        # 累积思考内容
        if hasattr(delta, 'reasoning_content') and delta.reasoning_content:
            reasoning_content += delta.reasoning_content
            print(delta.reasoning_content, end="", flush=True)
        
        # 累积最终回答内容
        if delta.content:
            answer_content += delta.content
    
    # 打印最终回答
    print("\n" + "=" * 20 + "最终回答（原始JSON字符串）" + "=" * 20)
    print(answer_content)
    
    # 尝试解析 JSON
    parsed_answer = safe_parse_json(answer_content)
    if parsed_answer is None:
        print("警告：无法解析为 JSON，将返回原始字符串")
        parsed_answer = answer_content
    
    return {
        "reasoning": reasoning_content,
        "answer": parsed_answer,
        "raw_answer": answer_content,
        "usage": usage
    }


def safe_parse_json(text: str) -> Optional[dict]:
    """安全解析 AI 返回的 JSON 字符串，多层兜底容错"""
    # 1. 直接解析纯 JSON
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 2. 提取 markdown json 代码块
    pattern_code = r'```(?:json)?\s*([\s\S]+?)```'
    match = re.search(pattern_code, text)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # 3. 提取全文第一个 {} 或 [] 对象
    pattern_obj = r'(\{[\s\S]+?\}|\[[\s\S]+?\])'
    match = re.search(pattern_obj, text)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    return None

def validate_ai_output(data: dict, schema: dict) -> tuple[bool, str]:
    HAS_JSONSCHEMA = True
    """校验 AI 输出是否符合 Schema"""
    if not HAS_JSONSCHEMA:
        return False, "jsonschema 模块未安装，无法校验"
    try:
        validate(instance=data, schema=schema)
        return True, "校验通过"
    except ValidationError as e:
        return False, f"校验失败：{e.message}"


# ==================== JSON Schema 定义 ====================
order_schema = {
    "type": "object",
    "properties": {
        "order_id": {
            "type": "string",
            "description": "情感倾向（正面/负面/中性）  "
        },
        "customer": {
            "type": "integer",
            "description": "评分（1-5 的整数）"
        },
        "items": {
            "type": "array",
            "description": "关键词（字符串数组）",
            "items": {"type": "string"}
        },
     
        "priority": {
            "type": "boolean",
            "description": "是否需要人工处理（布尔值）"
        }
    },
    "required": ["order_id", "customer", "items", "priority"]
}


def extract_with_schema(text: str, schema: dict, model: str = "deepseek-chat") -> dict:
    """用 Schema 约束提取结构化信息"""
    schema_str = json.dumps(schema, ensure_ascii=False, indent=2)



    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)


def parse_ai_xml(xml_text: str) -> ET.Element | None:
    """安全解析 AI 返回的 XML"""
    # 清理 markdown 代码块
    xml_text = re.sub(r'```(?:xml)?\s*', '', xml_text)
    xml_text = xml_text.replace('```', '').strip()

    try:
        return ET.fromstring(xml_text)
    except ET.ParseError as e:
        print(f"XML 解析失败：{e}")
        return None


def review_to_dict(root: ET.Element) -> dict:
    """将 review XML 转为字典"""
    result = {
        "sentiment": root.findtext("sentiment", ""),
        "score":     int(root.findtext("score", "0")),
        "pros":      [item.text for item in root.findall("pros/item")],
        "cons":      [item.text for item in root.findall("cons/item")],
        "summary":   root.findtext("summary", "")
    }
    return result


# class AIRole:
#     """可持久化的 AI 角色"""

#     def __init__(self, name: str, system_prompt: str, model: str = "deepseek-chat"):
#         self.name = name
#         self.system_prompt = system_prompt
#         self.model = model
#         self.history: list[dict] = []  # 对话历史

#     def chat(self, user_input: str) -> str:
#         """发送消息，保留上下文"""
#         self.history.append({"role": "user", "content": user_input})

#         messages = [{"role": "system", "content": self.system_prompt}] + self.history

#         response = client.chat.completions.create(
#             model=self.model,
#             messages=messages
#         )
#         reply = response.choices[0].message.content
#         self.history.append({"role": "assistant", "content": reply})
#         return reply

#     def reset(self):
#         """重置对话历史，保留角色设定"""
#         self.history = []
#         print(f"[{self.name}] 对话历史已清空")

#     def get_history_count(self) -> int:
#         return len(self.history) // 2  # 轮数


# # 创建两个不同角色
# python_tutor = AIRole(
#     name="代码审查官",
#     system_prompt="""你是一个严格代码审查官
#     行为准则
#      1.发现代码问题时态度严格，要求学员修改后才能通过。
#      2.如果代码没有问题，直接通过。
#      3.回答要包含可运行的代码示例
#      输出格式：

    
#      边界限制：


#      """
# )

# career_advisor = AIRole(
#     name="学习伙伴",
#     system_prompt="你是一个温柔学习伙伴，鼓励式教学，即使代码有错也先肯定亮点"
# )
# ==================== 会话状态定义 ====================
class ConversationState(Enum):
    IDLE      = "空闲"
    ACTIVE    = "活跃"
    WAITING   = "等待用户"
    SUMMARIZING = "摘要中"
    ENDED     = "已结束"

@dataclass
class ConversationSession:
    """对话会话（带状态追踪）"""
    session_id: str
    role_name: str
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))
    state: ConversationState = ConversationState.IDLE
    turn_count: int = 0
    tags: list[str] = field(default_factory=list)

    def start(self):
        self.state = ConversationState.ACTIVE
        print(f"[{self.role_name}] 会话 {self.session_id} 开始")

    def end(self):
        self.state = ConversationState.ENDED
        print(f"[{self.role_name}] 会话结束，共 {self.turn_count} 轮")

    def __str__(self):
        return f"Session({self.session_id}, {self.role_name}, {self.state.value}, {self.turn_count}轮)"

# ==================== 示例调用 ====================
class ConversationManager:
    """多轮对话管理器（集成会话状态追踪）"""

    def __init__(
        self,
        system_prompt: str,
        role_name: str = "AI助手",
        model: str = "deepseek-chat",
        max_history: int = 4,       # 最多保留几轮历史
        max_tokens: int = 400000       # 历史区预留 token 上限（粗略估算）
    ):
        self.system_prompt = system_prompt
        self.model = model
        self.max_history = max_history
        self.max_tokens = max_tokens
        self.history: list[dict] = []
        
        # 集成会话状态追踪
        self.session = ConversationSession(
            session_id=f"session_{int(time.time())}",
            role_name=role_name
        )
        self.session.start()  # 初始化时自动开始会话

    def _estimate_tokens(self, text: str) -> int:
        """粗略估算 token 数（中文约1.5字/token，英文约4字/token）"""
        chinese_count = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        other_count = len(text) - chinese_count
        return int(chinese_count / 1.5 + other_count / 4)

    def _trim_history(self):
        """修剪历史记录：超过限制则删除最早的对话轮"""
        # 先按轮数限制
        while len(self.history) > self.max_history * 2:
            self.history.pop(0)  # 删除最早的 user
            self.history.pop(0)  # 删除对应的 assistant

        # 再按 token 估算限制
        total_tokens = sum(self._estimate_tokens(m["content"]) for m in self.history)
        while total_tokens > self.max_tokens and len(self.history) >= 2:
            removed_user = self.history.pop(0)
            removed_ai   = self.history.pop(0)
            total_tokens -= (
                self._estimate_tokens(removed_user["content"]) +
                self._estimate_tokens(removed_ai["content"])
            )

    def chat(self, user_input: str, verbose: bool = False) -> str:
        """发送消息，自动管理上下文（集成会话状态追踪）"""
        # 更新会话状态为活跃（处理中）
        self.session.state = ConversationState.ACTIVE
        
        # 更新会话轮次计数
        self.session.turn_count += 1
        self.history.append({"role": "user", "content": user_input})

        messages = [{"role": "system", "content": self.system_prompt}] + self.history

        if verbose:
            total_msg_tokens = sum(self._estimate_tokens(m["content"]) for m in messages)
            print(f"[{self.session.role_name}] [轮次 {self.session.turn_count}] 状态: {self.session.state.value}, 历史轮数: {len(self.history)//2}, 预计 token: ~{total_msg_tokens}")

        response = client.chat.completions.create(
            model=self.model,
            messages=messages
        )
        reply = response.choices[0].message.content
        self.history.append({"role": "assistant", "content": reply})

        # 更新状态为等待用户输入
        self.session.state = ConversationState.WAITING

        # 添加后再修剪（保证本轮完整）
        self._trim_history()
        return reply

    def end_session(self):
        """结束当前会话"""
        self.session.end()

    def inject_context(self, context: str):
        """注入背景信息（不占用对话轮次）"""
        # 用 system 角色在历史中插入一条上下文
        self.history.append({
            "role": "user",
            "content": f"[背景信息，请记住：{context}]"
        })
        self.history.append({
            "role": "assistant",
            "content": "好的，我已记录这些背景信息。"
        })

    def get_summary_prompt(self) -> str:
        """生成对话摘要 prompt"""
        history_text = "\n".join(
            f"{'用户' if m['role']=='user' else 'AI'}: {m['content']}"
            for m in self.history
        )
        return f"请将以下对话总结为3-5句话的摘要：\n\n{history_text}"


# class ConversationState(Enum):
#     IDLE      = "空闲"
#     ACTIVE    = "活跃"
#     WAITING   = "等待用户"
#     SUMMARIZING = "摘要中"
#     ENDED     = "已结束"

# @dataclass
# class ConversationSession:
#     """对话会话（带状态追踪）"""
#     session_id: str
#     role_name: str
#     created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))
#     state: ConversationState = ConversationState.IDLE
#     turn_count: int = 0
#     tags: list[str] = field(default_factory=list)

#     def start(self):
#         self.state = ConversationState.ACTIVE
#         print(f"[{self.role_name}] 会话 {self.session_id} 开始")

#     def end(self):
#         self.state = ConversationState.ENDED
#         print(f"[{self.role_name}] 会话结束，共 {self.turn_count} 轮")

#     def __str__(self):
#         return f"Session({self.session_id}, {self.role_name}, {self.state.value}, {self.turn_count}轮)"

# class RoleManager:
#     """多角色管理器"""
    
#     def __init__(self, model: str = "deepseek-v4-pro"):
#         self.model = model
#         self.roles: dict[str, dict] = {}        # 角色库
#         self.role_histories: dict[str, list] = {}  # 各角色独立历史
#         self.current_role: str | None = None    # 当前角色

#     def register_role(self, role_id: str, name: str, system_prompt: str, description: str = ""):
#         """注册一个角色"""
#         self.roles[role_id] = {
#             "name":          name,
#             "system_prompt": system_prompt,
#             "description":   description
#         }
#         self.role_histories[role_id] = []
#         print(f"角色 [{name}] 注册成功 (id: {role_id})")

#     def switch_role(self, role_id: str, keep_history: bool = False):
#         """切换当前角色"""
#         if role_id not in self.roles:
#             raise ValueError(f"角色 {role_id} 不存在")

#         old_role = self.current_role
#         self.current_role = role_id

#         if not keep_history:
#             # 切换时可选择是否清空该角色的历史
#             pass

#         role_name = self.roles[role_id]["name"]
#         print(f"角色切换：{self.roles[old_role]['name'] if old_role else '无'} → {role_name}")

#     def chat(self, user_input: str) -> str:
#         """用当前角色对话"""
#         if self.current_role is None:
#             raise RuntimeError("未设置当前角色，请先调用 switch_role()")

#         role = self.roles[self.current_role]
#         history = self.role_histories[self.current_role]

#         history.append({"role": "user", "content": user_input})

#         messages = [{"role": "system", "content": role["system_prompt"]}] + history

#         response = client.chat.completions.create(
#             model=self.model,
#             messages=messages
#         )
#         reply = response.choices[0].message.content
#         history.append({"role": "assistant", "content": reply})
#         return reply

#     def auto_route(self, user_input: str) -> str:
#         """自动路由：让 AI 判断该用哪个角色，然后切换并回答"""
#         role_descriptions = "\n".join(
#             f"- {rid}: {info['name']} - {info['description']}"
#             for rid, info in self.roles.items()
#         )

#         routing_prompt = f"""根据用户输入，选择最合适的角色ID来回答。
# 只输出角色ID，不要任何其他内容。

# 可用角色：
# {role_descriptions}

# 用户输入：{user_input}
# """
#         routing_response = client.chat.completions.create(
#             model=self.model,
#             messages=[{"role": "user", "content": routing_prompt}]
#         )
#         role_id = routing_response.choices[0].message.content.strip()

#         # 容错：如果返回的不是有效 role_id，用第一个角色
#         if role_id not in self.roles:
#             role_id = list(self.roles.keys())[0]

#         self.switch_role(role_id)
#         return self.chat(user_input)

#     def list_roles(self):
#         """显示所有角色"""
#         print("\n=== 已注册角色 ===")
#         for rid, info in self.roles.items():
#             marker = " ← 当前" if rid == self.current_role else ""
#             print(f"  [{rid}] {info['name']}: {info['description']}{marker}")


# # 构建一个客服系统
# manager = RoleManager()

# manager.register_role(
#     "tech",
#     "技术支持",
#     "你是专业技术支持工程师，解答产品技术问题，答案要具体准确。",
#     "处理技术问题、bug 报告、使用教程"
# )

# manager.register_role(
#     "sales",
#     "销售顾问",
#     "你是热情的销售顾问，了解产品优势，引导用户购买，回答要有亲和力。",
#     "产品介绍、价格咨询、购买建议"
# )

# manager.register_role(
#     "complaint",
#     "投诉处理",
#     "你是有同理心的投诉处理专员，先安抚情绪，再解决问题，语气要温柔耐心。",
#     "处理投诉、退款申请、纠纷协调"
# )

# manager.register_role(
#     "teacher",
#     "知识讲解老师",
#     "你是有同理心的知识讲解老师，讲解产品知识，回答要详细准确。",
#     "产品知识讲解、产品使用建议"
# )

# manager.register_role(
#     "creator",
#     "出题考官",
#     "你是有同理心的出题考官，先安抚情绪，再解决问题，语气要温柔耐心。",
#     "出判断，选择题"
# )

# manager.register_role(
#     "assistant",
#     "学习规划师",
#     "你是有同理心的学习规划师，先安抚情绪，再解决问题，语气要温柔耐心。",
#     "学习规划、学习建议"
# )
# manager.list_roles()

# class SummaryConversationManager:
#     """带摘要压缩的对话管理器"""

#     def __init__(
#         self,
#         system_prompt: str,
#         model: str = "deepseek-v4-pro",
#         compress_every: int = 6,   # 每 6 轮压缩一次
#         keep_recent: int = 3       # 压缩后保留最近 3 轮原文
#     ):
#         self.system_prompt = system_prompt
#         self.model = model
#         self.compress_every = compress_every
#         self.keep_recent = keep_recent
#         self.history: list[dict] = []
#         self.summary: str = ""     # 历史摘要（压缩的结果）
#         self.turn_count = 0

#     def _compress(self):
#         """压缩历史：把早期历史总结成摘要"""
#         print("\n[系统] 正在压缩对话历史...")

#         # 准备要压缩的部分（保留最近 keep_recent 轮）
#         keep_count = self.keep_recent * 2
#         to_compress = self.history[:-keep_count] if len(self.history) > keep_count else []
#         recent = self.history[-keep_count:] if len(self.history) > keep_count else self.history

#         if not to_compress:
#             return  # 没有需要压缩的内容

#         # 生成新摘要
#         history_text = "\n".join(
#             f"{'用户' if m['role']=='user' else 'AI'}: {m['content']}"
#             for m in to_compress
#         )

#         existing_summary = f"已有摘要：\n{self.summary}\n\n" if self.summary else ""

#         compress_prompt = f"""{existing_summary}请将以下对话补充摘要到已有摘要中，保留关键事实、用户偏好、重要决策：

# {history_text}

# 要求：
# 1. 摘要控制在200字以内
# 2. 用第三人称描述（"用户表示..."）
# 3. 突出关键信息"""

#         response = client.chat.completions.create(
#             model=self.model,
#             messages=[{"role": "user", "content": compress_prompt}]
#         )
#         self.summary = response.choices[0].message.content

#         # 用摘要替换旧历史
#         self.history = recent
#         print(f"[系统] 压缩完成，历史从 {len(to_compress)+len(recent)} 条压缩至 {len(recent)} 条")
#         print(f"[摘要] {self.summary[:80]}...")

#     def chat(self, user_input: str) -> str:
#         """对话，自动触发摘要压缩"""
#         self.turn_count += 1
#         self.history.append({"role": "user", "content": user_input})

#         # 构建消息：system + 摘要（如有）+ 近期历史
#         messages = [{"role": "system", "content": self.system_prompt}]

#         if self.summary:
#             messages.append({
#                 "role": "system",
#                 "content": f"[对话摘要 - 之前聊过的内容]\n{self.summary}"
#             })

#         messages.extend(self.history)

#         response = client.chat.completions.create(
#             model=self.model,
#             messages=messages
#         )
#         reply = response.choices[0].message.content
#         self.history.append({"role": "assistant", "content": reply})

#         # 达到压缩阈值时触发压缩
#         if self.turn_count % self.compress_every == 0:
#             self._compress()

#         return reply


# 测试长对话
mgr = ConversationManager(
    system_prompt="你是一个助手，帮用户规划。记住用户提到的偏好和需求。",
)

conversations = [
    "我喜欢吃香蕉",
    "我喜欢喝甜甜的水",
    "我对历史文化很感兴趣，喜欢寺庙和神社",
    "我不能吃海鲜，对花粉过敏",
    "我喜欢吃鸭子",
    "我不喜欢吃鱼",
    "我喜欢在海边吃东西",
    "我可以在沙滩玩",
    "我在市中心工作",
    "请给我推荐一部电影"  # 这时已经压缩过了，看看 AI 还记得多少
]

for msg in conversations:
    print(f"\n用户：{msg}")
    reply = mgr.chat(msg)
    print(f"AI：{reply}")

# 使用演示
# conv = ConversationManager(
#     system_prompt="你是一个学习计划助手，帮助用户制定个性化学习路线。",
#     role_name="学习助手"
# )

# 查看初始会话状态
# print(f"初始会话状态: {conv.session.state.value}")
# print(f"会话信息: {conv.session}")

# 进行对话
# a = input("请输入：")
# print(conv.chat(a, verbose=True))

# 查看会话状态
# print(f"\n会话状态: {conv.session.state.value}")
# print(f"会话信息: {conv.session}")

# 结束会话
# conv.end_session()