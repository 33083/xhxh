import json
import os
import requests
from openai import OpenAI
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1"
)


class ConversationManager:
    """多轮对话管理器"""

    def __init__(
        self,
        system_prompt: str,
        model: str = "qwen-turbo",
        max_history: int = 4,       # 最多保留几轮历史
        max_tokens: int = 4000       # 历史区预留 token 上限（粗略估算）
    ):
        self.system_prompt = system_prompt
        self.model = model
        self.max_history = max_history
        self.max_tokens = max_tokens
        self.history: list[dict] = []
        self.turn_count = 0

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
        """发送消息，自动管理上下文"""
        self.turn_count += 1
        self.history.append({"role": "user", "content": user_input})

        messages = [{"role": "system", "content": self.system_prompt}] + self.history

        if verbose:
            total_msg_tokens = sum(self._estimate_tokens(m["content"]) for m in messages)
            print(f"[轮次 {self.turn_count}] 历史轮数: {len(self.history)//2}, 预计 token: ~{total_msg_tokens}")

        response = client.chat.completions.create(
            model=self.model,
            messages=messages
        )
        reply = response.choices[0].message.content
        self.history.append({"role": "assistant", "content": reply})

        # 添加后再修剪（保证本轮完整）
        self._trim_history()
        return reply

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


# ── 情绪日记功能 ────────────────────────────────────────────
MOOD_SCHEMA = {
    "type": "object",
    "properties": {
        "date": {"type": "string"},
        "mood": {"type": "string", "enum": ["开心", "焦虑", "平静", "悲伤", "愤怒", "兴奋"]},
        "mood_score": {"type": "integer", "description": "情绪分1-10, 10最积极"},
        "mood_keywords": {"type": "array", "items": {"type": "string"}},
        "keywords": {"type": "array", "items": {"type": "string"}},
        "trigger": {"type": "string", "description": "情绪触发原因"},
        "advice": {"type": "string", "description": "给自己的建议"}
    },
    "required": ["mood", "mood_score", "keywords"]
}

class MoodDiary:
    """情绪日记管理器"""
    
    def __init__(self):
        self.entries: list[dict] = []  # 存储情绪记录
    
    def analyze_diary(self, diary_text: str) -> dict:
        """分析日记文本，提取情绪信息"""
        schema_str = json.dumps(MOOD_SCHEMA, ensure_ascii=False, indent=2)
        
        prompt = f"""<task>
<role>你是情绪分析助手</role>
<input><diary>{diary_text}</diary></input>
<output_format>
严格按照以下 Schema 输出 JSON：
{schema_str}
</output_format>
</task>"""
        
        try:
            response = client.chat.completions.create(
                model="deepseek-v4-pro",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            result = json.loads(response.choices[0].message.content)
            
            # 添加日期
            if "date" not in result:
                result["date"] = datetime.now().strftime("%Y-%m-%d")
            
            # 保存记录
            self.entries.append(result)
            return result
        except Exception as e:
            return {"error": str(e)}
    
    def get_weekly_report(self) -> dict:
        """生成本周情绪趋势报告"""
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        
        # 筛选本周记录，过滤无效日期
        weekly_entries = []
        for e in self.entries:
            date_str = e.get("date", "")
            if not date_str or date_str.strip() == "":
                continue  # 跳过空日期记录
            try:
                entry_date = datetime.strptime(date_str, "%Y-%m-%d")
                if entry_date >= week_start:
                    weekly_entries.append(e)
            except ValueError:
                continue  # 跳过无效日期格式
        
        if not weekly_entries:
            return {"error": "本周暂无情绪记录"}
        
        # 计算统计数据
        scores = [e["mood_score"] for e in weekly_entries]
        week_avg = round(sum(scores) / len(scores), 1)
        
        # 找出情绪最低的一天
        lowest_entry = min(weekly_entries, key=lambda x: x["mood_score"])
        lowest_date = lowest_entry["date"]
        # 转换为星期几
        weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        lowest_day = weekdays[datetime.strptime(lowest_date, "%Y-%m-%d").weekday()]
        
        # 判断趋势（简单比较首尾）
        if len(scores) >= 2:
            trend = "上升" if scores[-1] > scores[0] else "下降" if scores[-1] < scores[0] else "平稳"
        else:
            trend = "数据不足"
        
        # 检查负面情绪连续3天预警
        alert = self._check_negative_alert()
        
        return {
            "week_avg": week_avg,
            "lowest_day": lowest_day,
            "trend": trend,
            "alert": alert,
            "count": len(weekly_entries)
        }
    
    def _check_negative_alert(self) -> str:
        """检查是否有负面情绪连续3天"""
        # 过滤出有效日期的记录
        valid_entries = [
            e for e in self.entries
            if e.get("date") and e["date"].strip()
        ]
        
        if len(valid_entries) < 3:
            return ""
        
        # 按日期排序
        sorted_entries = sorted(valid_entries, key=lambda x: x["date"])
        recent_3 = sorted_entries[-3:]
        
        # 检查是否连续3天情绪得分 <= 4（负面）
        if all(e["mood_score"] <= 4 for e in recent_3):
            return "警告：已连续3天处于负面情绪状态，建议放松休息或寻求帮助！"
        return ""
    
    def get_all_entries(self) -> list:
        """获取所有情绪记录"""
        return self.entries

# 全局情绪日记实例
mood_diary = MoodDiary()

# ── 角色定义 ────────────────────────────────────────────────
ROLES = {
    "qa": {
        "name": "知识助手",
        "prompt": """你是一个知识渊博的问答助手。
回答问题时，输出 JSON 格式：
{"answer": "回答内容", "confidence": "高/中/低", "related_topics": ["相关话题1", "相关话题2"]}""",
        "output": "json"
    },
    "task": {
        "name": "任务管家",
        "prompt": """你是一个任务管理助手。
当用户描述任务时，提取任务信息输出 JSON：
{"task_name": "任务名", "deadline": "截止日期或null", "priority": "高/中/低", "tags": ["标签"]}
当用户查询任务列表时，以文字形式回复。""",
        "output": "json"
    },
    "writing": {
        "name": "写作助手",
        "prompt": """你是一个专业写作助手，擅长各种文体。
用户可以指定写作风格（正式/轻松/文艺/幽默）。
默认风格：轻松自然。""",
        "output": "text"
    },
    "tutor": {
        "name": "学习导师",
        "prompt": """你是一位耐心细致的学习导师，擅长 Python 和 AI 领域。
根据学员水平调整讲解深度，多用类比和例子。
遇到学员不理解时，换一种方式解释。""",
        "output": "text"
    },
    "mood": {
        "name": "情绪日记",
        "prompt": """你是一个情绪分析助手。
当用户输入日记内容时，分析情绪并输出 JSON。
当用户说「本周情绪报告」或「本周情绪趋势」时，输出趋势报告。
输出格式：{"mood": "情绪标签", "mood_score": 分数, "keywords": ["关键词"], "trigger": "触发原因", "advice": "建议"}""",
        "output": "json"
    }
}

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "当你想查询指定城市的当天天气时非常有用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "城市或县区，比如北京市、杭州市、余杭区等。",
                    }
                },
                "required": ["location"],
            },
        },      
    },
    {
        "type": "function",
        "function": {
            "name": "get_weilai_weather",
            "description": "当你想查询指定城市的未来天气时非常有用。",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "城市或县区，比如北京市、杭州市、余杭区等。",
                    }
                },
                "required": ["location"],
            },
        },      
    },
]
KEY = "0036c67c5753a73ef6ddbeb3cd434049"

def get_current_weather(arguments):
    """查询指定城市的实时天气"""
    location = arguments["location"]
    url = "https://restapi.amap.com/v3/weather/weatherInfo"

    params_base = {
        "city": location,
        "key": KEY,
        "extensions": "base",
        "output": "JSON"
    }
    try:
        res_base = requests.get(url, params=params_base, timeout=10)
        print(f"[实时天气] HTTP状态码: {res_base.status_code}")

        data_base = res_base.json()
        print(f"[实时天气] API返回: {data_base}")

        # 检查 API 返回状态
        if data_base.get("status") != "1":
            error_info = data_base.get("info", "未知错误")
            print(f"X API返回错误: {error_info}")
            return f"获取天气数据失败：{error_info}"

        if "lives" in data_base and len(data_base["lives"]) > 0:
            weather = data_base["lives"][0]
            city = weather.get('city', location)
            weather_desc = weather.get('weather', '未知')
            temperature = weather.get('temperature', '未知')
            humidity = weather.get('humidity', '未知')
            wind_direction = weather.get('winddirection', '未知')
            wind_power = weather.get('windpower', '')

            print(f"  城市: {city}")
            print(f"  天气: {weather_desc}")
            print(f"  温度: {temperature}°C")
            print(f"  湿度: {humidity}%")
            print(f"  风力: {wind_direction} {wind_power}级")

            return f"{city}当前天气：{weather_desc}，温度{temperature}°C，湿度{humidity}%，风力{wind_direction}{wind_power}级"
        else:
            print("X 未获取到实时天气数据")
            return f"未查询到「{location}」的天气信息，请确认城市名称是否正确。"
    except requests.exceptions.RequestException as e:
        print(f"X 请求失败: {e}")
        return f"获取天气数据失败：网络请求错误"
    except Exception as e:
        print(f"X 未知错误: {e}")
        return f"获取天气数据失败：{str(e)}"

def get_weilai_weather(arguments):
    """查询指定城市的未来天气预报"""
    location = arguments["location"]
    url = "https://restapi.amap.com/v3/weather/weatherInfo"

    params_all = {
        "city": location,
        "key": KEY,
        "extensions": "all",
        "output": "JSON"
    }
    try:
        res_all = requests.get(url, params=params_all, timeout=10)
        print(f"[未来天气] HTTP状态码: {res_all.status_code}")

        if res_all.status_code != 200:
            print(f"X HTTP错误: {res_all.status_code}")
            return f"获取天气预报失败：HTTP {res_all.status_code}"

        data_all = res_all.json()
        print(f"[未来天气] API返回: {data_all}")

        if data_all.get("status") != "1":
            error_info = data_all.get("info", "未知错误")
            print(f"X API返回错误: {error_info}")
            return f"获取天气预报失败：{error_info}"

        if "forecasts" in data_all and len(data_all["forecasts"]) > 0:
            forecast = data_all["forecasts"][0]
            city = forecast.get('city', location)
            print(f"  城市: {city}")
            print("  未来天气预报:")

            weather_info = f"{city}未来天气预报：\n"

            if "casts" in forecast and len(forecast["casts"]) > 0:
                for day in forecast["casts"]:
                    date = day.get('date', '未知')
                    day_weather = day.get('dayweather', '未知')
                    night_weather = day.get('nightweather', '未知')
                    # 合并昼夜天气
                    if day_weather == night_weather:
                        weather = day_weather
                    else:
                        weather = f"{day_weather}转{night_weather}"
                    nighttemp = day.get('nighttemp', '未知')
                    daytemp = day.get('daytemp', '未知')
                    wind_direction = day.get('daywind', day.get('nightwind', '未知'))
                    wind_power = day.get('daypower', day.get('nightpower', ''))

                    print(f"    日期: {date}")
                    print(f"    天气: {weather}")
                    print(f"    温度: {nighttemp}°C ~ {daytemp}°C")
                    print(f"    风力: {wind_direction} {wind_power}级")

                    weather_info += f"  {date}: {weather}，温度{nighttemp}°C ~ {daytemp}°C\n"

                return weather_info
            else:
                print("X 未获取到天气预报数据")
                return "获取天气预报失败：未返回预报信息"
        else:
            print("X 未获取到预报数据")
            return f"未查询到「{location}」的未来天气信息，请确认城市名称是否正确。"
    except requests.exceptions.RequestException as e:
        print(f"X 请求失败: {e}")
        return f"获取天气预报失败：网络请求错误"
    except Exception as e:
        print(f"X 未知错误: {e}")
        return f"获取天气预报失败：{str(e)}"

# ── 工具函数映射（供 function calling 使用） ──────────────────
TOOLS_MAP = {
    "get_current_weather": get_current_weather,
    "get_weilai_weather": get_weilai_weather,
}


class PersonalAI:
    """个人 AI 助手，支持多角色切换、自动路由、函数调用"""

    def __init__(self, model: str = "deepseek-chat"):
        self.model = model
        self.current_role = "qa"
        self.histories: dict[str, list] = {role_id: [] for role_id in ROLES}
        self.summaries: dict[str, str] = {role_id: "" for role_id in ROLES}
        self.tasks: list[dict] = []    # 任务列表
        self.turn_counts: dict[str, int] = {role_id: 0 for role_id in ROLES}

    def switch(self, role_id: str):
        if role_id not in ROLES:
            print(f"无效角色ID，可选：{', '.join(ROLES.keys())}")
            return
        self.current_role = role_id
        print(f"✓ 已切换到【{ROLES[role_id]['name']}】")

    def _call_api(self, messages: list[dict], use_tools: bool = True,
                  json_mode: bool = False) -> "ChatCompletionMessage":
        """封装 API 调用，统一异常处理和参数配置"""
        kwargs = {
            "model": self.model,
            "messages": messages,
        }
        if use_tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        response = client.chat.completions.create(**kwargs)
        return response.choices[0].message

    def _execute_tool(self, tool_call) -> str:
        """执行单个工具调用并返回结果字符串"""
        func_name = tool_call.function.name
        try:
            arguments = json.loads(tool_call.function.arguments)
        except json.JSONDecodeError:
            return f"工具调用参数解析失败：{tool_call.function.arguments}"

        func = TOOLS_MAP.get(func_name)
        if func is None:
            return f"未知工具：{func_name}"

        print(f"  🔧 调用工具: {func_name}({arguments})")
        result = func(arguments)
        print(f"  📋 工具返回: {result[:100]}{'...' if len(result) > 100 else ''}")
        return result

    def _handle_tool_calls(self, messages: list[dict], message,
                           max_rounds: int = 3) -> str:
        """处理 function calling 循环：执行工具 → 将结果反馈给模型 → 获取最终回复"""
        # 添加 assistant 消息（含 tool_calls）
        messages.append({
            "role": "assistant",
            "content": message.content or "",
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in message.tool_calls
            ]
        })

        for _ in range(max_rounds):
            # 执行所有工具调用
            for tool_call in message.tool_calls:
                result = self._execute_tool(tool_call)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })

            # 再次调用模型获取最终回复
            response_message = self._call_api(messages, use_tools=True)
            message = response_message

            # 如果模型不再请求工具调用，返回文本内容
            if not response_message.tool_calls:
                return response_message.content or ""

        # 超过最大轮次，强制返回
        return "抱歉，工具调用轮次过多，请简化你的问题。"

    def chat(self, user_input: str) -> str:
        """发送消息，自动管理上下文，支持 function calling"""
        role = ROLES[self.current_role]
        history = self.histories[self.current_role]
        summary = self.summaries[self.current_role]

        history.append({"role": "user", "content": user_input})

        messages = [{"role": "system", "content": role["prompt"]}]
        if summary:
            messages.append({"role": "system", "content": f"[历史摘要]\n{summary}"})
        messages.extend(history[-12:])  # 最近 6 轮

        try:
            response_message = self._call_api(
                messages,
                use_tools=True,
                json_mode=(role["output"] == "json")
            )
        except Exception as e:
            print(f"X API 调用失败: {e}")
            reply = f"抱歉，服务暂时不可用。（{e}）"
            history.append({"role": "assistant", "content": reply})
            self.turn_counts[self.current_role] += 1
            return reply

        # 如果模型请求工具调用，进入 function calling 循环
        if response_message.tool_calls:
            reply = self._handle_tool_calls(messages, response_message)
        else:
            reply = response_message.content or ""

        history.append({"role": "assistant", "content": reply})

        # 任务管理：解析并保存任务
        if self.current_role == "task":
            try:
                task_data = json.loads(reply)
                if "task_name" in task_data:
                    task_data["created_at"] = datetime.now().strftime("%m-%d %H:%M")
                    task_data["id"] = len(self.tasks) + 1
                    self.tasks.append(task_data)
            except (json.JSONDecodeError, KeyError):
                pass

        # 情绪日记：特殊处理
        if self.current_role == "mood":
            # 如果是查询本周情绪趋势
            if "本周情绪" in user_input or "情绪报告" in user_input or "情绪趋势" in user_input or "趋势报告" in user_input:
                report = mood_diary.get_weekly_report()
                if "error" not in report:
                    reply = json.dumps({
                        "week_avg": report["week_avg"],
                        "lowest_day": report["lowest_day"],
                        "trend": report["trend"],
                        "alert": report.get("alert", ""),
                        "count": report.get("count", 0)
                    }, ensure_ascii=False)
                    history[-1]["content"] = reply
                else:
                    history[-1]["content"] = json.dumps({"error": report["error"]}, ensure_ascii=False)
            # 如果是查看所有记录
            elif "查看" in user_input and "记录" in user_input or "获取" in user_input and "记录" in user_input:
                entries = mood_diary.get_all_entries()
                if entries:
                    reply = json.dumps({"count": len(entries), "entries": entries}, ensure_ascii=False, indent=2)
                else:
                    reply = json.dumps({"message": "暂无情绪记录"})
                history[-1]["content"] = reply
            else:
                # 分析日记内容
                analysis = mood_diary.analyze_diary(user_input)
                if "error" not in analysis:
                    reply = json.dumps(analysis, ensure_ascii=False)
                    history[-1]["content"] = reply

        self.turn_counts[self.current_role] += 1
        return reply

    def auto_route(self, user_input: str) -> str:
        """自动路由：让 AI 判断该用哪个角色，然后切换并回答"""
        role_descriptions = "\n".join(
            f"- {rid}: {info['name']} - {info['prompt'][:60]}..."
            for rid, info in ROLES.items()
        )

        routing_prompt = f"""根据用户输入，选择最合适的角色ID来回答。
只输出角色ID（qa/task/writing/tutor），不要任何其他内容。

可用角色：
{role_descriptions}

用户输入：{user_input}
"""
        try:
            routing_response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": routing_prompt}]
            )
            role_id = routing_response.choices[0].message.content.strip()
        except Exception as e:
            print(f"X 路由失败: {e}，使用当前角色")
            return self.chat(user_input)

        # 容错：如果返回的不是有效 role_id，保持当前角色不变
        if role_id not in ROLES:
            print(f"  ⚠ 路由失败（{role_id}），使用当前角色")
            return self.chat(user_input)

        # 如果角色不同，自动切换
        if role_id != self.current_role:
            self.switch(role_id)
        return self.chat(user_input)

    def show_tasks(self):
        if not self.tasks:
            print("暂无任务")
            return
        print("\n=== 任务列表 ===")
        for t in self.tasks:
            deadline = t.get('deadline') or '无截止日期'
            print(f"  [{t['id']}] {t['task_name']} | {t.get('priority','中')}优先 | {deadline}")

    def generate_summary(self) -> str:
        """为当前角色的对话生成摘要"""
        history = self.histories[self.current_role]
        if len(history) < 2:
            return "对话历史不足，无法生成摘要。"

        history_text = "\n".join(
            f"{'👤 用户' if m['role'] == 'user' else '🤖 AI'}: {m['content'][:200]}"
            for m in history
        )
        summary_prompt = f"请将以下对话总结为 3-5 句话的摘要：\n\n{history_text}"

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": summary_prompt}]
            )
            summary = response.choices[0].message.content
            self.summaries[self.current_role] = summary
            return summary
        except Exception as e:
            return f"生成摘要失败：{e}"

    def clear_history(self, role_id: str = None):
        """清除指定角色或当前角色的对话历史"""
        if role_id is None:
            role_id = self.current_role
        if role_id not in self.histories:
            print(f"无效角色ID：{role_id}")
            return
        self.histories[role_id] = []
        self.summaries[role_id] = ""
        role_name = ROLES[role_id]['name']
        print(f"✓ 已清除【{role_name}】的对话历史")

    def quick_weather(self, location: str):
        """快速查询天气（直接调用，不走 AI）"""
        print(f"查询「{location}」天气...")
        current = get_current_weather({"location": location})
        print(f"\n{current}")
        future = get_weilai_weather({"location": location})
        print(f"\n{future}")

    def status(self):
        print(f"\n当前角色：【{ROLES[self.current_role]['name']}】")
        print(f"任务数量：{len(self.tasks)}")
        for rid, count in self.turn_counts.items():
            if count > 0:
                print(f"  {ROLES[rid]['name']}: {count} 轮对话")


def main():
    ai = PersonalAI()
    auto_mode = True  # 默认开启自动路由
    print("PersonalAI 启动！自动路由模式已开启，输入 /help 查看命令\n")

    COMMANDS = {
        "/qa":      ("手动切换→知识助手",    lambda: ai.switch("qa")),
        "/task":    ("手动切换→任务管家",    lambda: ai.switch("task")),
        "/write":   ("手动切换→写作助手",    lambda: ai.switch("writing")),
        "/tutor":   ("手动切换→学习导师",    lambda: ai.switch("tutor")),
        "/mood":    ("手动切换→情绪日记",    lambda: ai.switch("mood")),
        "/tasks":   ("查看任务列表",        lambda: ai.show_tasks()),
        "/status":  ("查看系统状态",        lambda: ai.status()),
        "/auto":    ("切换自动/手动模式",    lambda: toggle_auto()),
        "/summary": ("生成对话摘要",        lambda: print(f"\n📝 摘要：\n{ai.generate_summary()}")),
        "/clear":   ("清除当前对话历史",     lambda: ai.clear_history()),
        "/quit":    ("退出",               lambda: exit(0)),
    }

    def toggle_auto():
        nonlocal auto_mode
        auto_mode = not auto_mode
        mode_text = "自动路由" if auto_mode else "手动切换"
        print(f"✓ 已切换到【{mode_text}】模式")

    while True:
        mode_indicator = " AUTO" if auto_mode else ""
        user_input = input(f"\n[{ROLES[ai.current_role]['name']}{mode_indicator}] > ").strip()
        if not user_input:
            continue

        # 处理斜杠命令
        if user_input in COMMANDS:
            desc, action = COMMANDS[user_input]
            action()
            continue

        if user_input == "/help":
            for cmd, (desc, _) in COMMANDS.items():
                print(f"  {cmd:12} {desc}")
            print(f"  {'/weather <城市>':12} 快速查询天气")
            continue

        # 快速天气查询：/weather 北京
        if user_input.startswith("/weather "):
            location = user_input[len("/weather "):].strip()
            if location:
                ai.quick_weather(location)
            else:
                print("用法：/weather <城市名>")
            continue

        # 自动路由模式：AI 自动选择角色；手动模式：使用当前角色
        if auto_mode:
            reply = ai.auto_route(user_input)
        else:
            reply = ai.chat(user_input)

        # 格式化输出
        if ROLES[ai.current_role]["output"] == "json":
            try:
                data = json.loads(reply)
                print(json.dumps(data, ensure_ascii=False, indent=2))
            except json.JSONDecodeError:
                print(reply)
        else:
            print(f"\n{reply}")


if __name__ == "__main__":
    main()