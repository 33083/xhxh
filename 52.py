
from openai import OpenAI
from dotenv import load_dotenv
import requests
import json
import os
load_dotenv()
# 初始化客户端
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    # 以下为华北2（北京）地域的URL，各地域的URL不同。
    base_url="https://api.deepseek.com/v1",
)
# 模拟用户问题
# USER_QUESTION = input("请输入您的问题：")  # 交互式输入
USER_QUESTION = "北京今天的天气和天津明天的天气怎么样"  # 默认测试问题

system_message = {
    "role": "system",
    "content": """你是一个很有帮助的助手
请以友好的语气回答问题。"""
}
messages = [system_message, {"role": "user", "content": USER_QUESTION}]
# 定义工具列表
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
# 天气查询工具
def get_current_weather(arguments):
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
            print(f"HTTP状态码: {res_base.status_code}")
            
            data_base = res_base.json()
            print(f"API返回数据: {data_base}")  # 调试信息
            
            
            if "lives" in data_base and len(data_base["lives"]) > 0:
                    weather = data_base["lives"][0]
                    # 检查必要字段
                    if "city" in weather and "weather" in weather:
                        city = weather['city']
                        weather_desc = weather['weather']
                        temperature = weather.get('temperature', '未知')
                        humidity = weather.get('humidity', '未知')
                        wind_direction = weather.get('winddirection', '未知')
                        wind_power = weather.get('windpower', '')
                        
                        print(f"城市: {city}")
                        print(f"天气: {weather_desc}")
                        print(f"温度: {temperature}°C")
                        print(f"湿度: {humidity}%")
                        print(f"风力: {wind_direction} {wind_power}级")
                        
                        # 返回格式化的天气信息
                        return f"{city}当前天气：{weather_desc}，温度{temperature}°C，湿度{humidity}%，风力{wind_direction}{wind_power}级"
    except requests.exceptions.RequestException as e:
            print(f"X 请求失败: {e}")
            return f"获取天气数据失败：网络请求错误"
    except KeyError as e:
            print(f"X 解析数据失败: 缺少字段 {e}")
            return f"获取天气数据失败：解析数据出错"
    except Exception as e:
            print(f"X 未知错误: {e}")
            return f"获取天气数据失败：未知错误"

def get_weilai_weather(arguments):
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
            print(f"HTTP状态码: {res_all.status_code}")
            
            data_all = res_all.json()
            print(f"API返回数据: {data_all}")  # 调试信息
            
            if data_all.get("status") == "1":
                if "forecasts" in data_all and len(data_all["forecasts"]) > 0:
                    forecast = data_all["forecasts"][0]
                    city = forecast.get('city', '未知')
                    print(f"城市: {city}")
                    print("未来天气预报:")
                    
                    # 只在开头添加一次城市名
                    weather_info = f"{city}未来天气预报：\n"
                    
                    if "casts" in forecast and len(forecast["casts"]) > 0:
                        for day in forecast["casts"]:
                            date = day.get('date', '未知')
                            # API返回的字段名是dayweather/nightweather
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
                            
                            print(f"日期: {date}")
                            print(f"  天气: {weather}")
                            print(f"  温度: {nighttemp}°C ~ {daytemp}°C")
                            print(f"  风力: {wind_direction} {wind_power}级")
                            
                            weather_info += f"{date}: {weather}，温度{nighttemp}°C ~ {daytemp}°C\n"
                        
                        return weather_info
                    else:
                        print("X 未获取到天气预报数据")
                        return "获取天气预报失败：未返回预报信息"
                else:
                    print("X 未获取到预报数据")
                    return "获取天气预报失败：未返回预报信息"
            else:
                error_info = data_all.get('info', '未知错误')
                print(f"X API返回错误: {error_info}")
                return f"获取天气预报失败：{error_info}"
    except requests.exceptions.RequestException as e:
            print(f"X 请求失败: {e}")
            return f"获取天气预报失败：网络请求错误"
    except KeyError as e:
            print(f"X 解析数据失败: 缺少字段 {e}")
            return f"获取天气预报失败：解析数据出错"
    except Exception as e:
            print(f"X 未知错误: {e}")
            return f"获取天气预报失败：未知错误"


def get_response(messages):
    # 使用流式输出，开启思考模式
    completion = client.chat.completions.create(
        model="deepseek-v4-pro",
        messages=messages,
        tools=tools,
        stream=True,
        parallel_tool_calls=True,
        extra_body={
            # 开启深度思考模式
            "enable_thinking": True
        }
    )
    
    reasoning_content = ""  # 定义完整思考过程
    answer_content = ""     # 定义完整回复
    tool_info = []          # 存储工具调用信息
    is_answering = False    # 判断是否结束思考过程并开始回复
    
    print("\n" + "="*20 + "思考过程" + "="*20)
    
    for chunk in completion:
        if not chunk.choices:
            # 处理用量统计信息
            print("\n" + "="*20 + "Usage" + "="*20)
            print(chunk.usage)
        else:
            delta = chunk.choices[0].delta
            
            # 处理AI的思考过程（链式推理）
            if hasattr(delta, 'reasoning_content') and delta.reasoning_content is not None:
                reasoning_content += delta.reasoning_content
                print(delta.reasoning_content, end="", flush=True)  # 实时输出思考过程
            
            # 处理最终回复内容
            if delta.content is not None:
                if not is_answering:  # 首次进入回复阶段时打印标题
                    is_answering = True
                    print("\n" + "="*20 + "回复内容" + "="*20)
                answer_content += delta.content
                print(delta.content, end="", flush=True)  # 流式输出回复内容
            
            # 处理工具调用信息（支持并行工具调用）
            if delta.tool_calls is not None:
                for tool_call in delta.tool_calls:
                    index = tool_call.index  # 工具调用索引，用于并行调用
                    
                    # 动态扩展工具信息存储列表
                    while len(tool_info) <= index:
                        tool_info.append({})
                    
                    # 收集工具调用ID（用于后续函数调用）
                    if tool_call.id:
                        tool_info[index]['id'] = tool_info[index].get('id', '') + tool_call.id
                    
                    # 收集函数名称（用于后续路由到具体函数）
                    if tool_call.function and tool_call.function.name:
                        tool_info[index]['name'] = tool_info[index].get('name', '') + tool_call.function.name
                    
                    # 收集函数参数（JSON字符串格式，需要后续解析）
                    if tool_call.function and tool_call.function.arguments:
                        tool_info[index]['arguments'] = tool_info[index].get('arguments', '') + tool_call.function.arguments
    
    print("\n" + "="*19 + "工具调用信息" + "="*19)
    if not tool_info:
        print("没有工具调用")
    else:
        print(tool_info)
    
    # 创建模拟的完整响应对象供工具调用处理
    class MockToolCall:
        def __init__(self, info):
            self.id = info.get('id', '')
            self.function = type('obj', (object,), {
                'name': info.get('name', ''),
                'arguments': info.get('arguments', '{}')
            })
    
    class MockMessage:
        def __init__(self):
            self.content = answer_content if answer_content else None
            if tool_info:
                self.tool_calls = [MockToolCall(info) for info in tool_info]
            else:
                self.tool_calls = None
    
    class MockChoice:
        def __init__(self, message):
            self.message = message
    
    class MockCompletion:
        def __init__(self, choices):
            self.choices = choices
    
    return MockCompletion([MockChoice(MockMessage())])

messages = [{"role": "user", "content": USER_QUESTION}]
def process_user_message(messages):
    """传入已有的 messages（已包含系统消息和历史对话），
       追加用户消息后，自动处理工具调用，最终将助手回复追加到 messages 中。
       返回助手的最终回复内容。
    """
    # 注意：调用此函数前，外部已经将用户消息追加到 messages 中
    response = get_response(messages)
    assistant_output = response.choices[0].message
    
    # 将 assistant_output 转换为字典格式，以便后续 JSON 序列化
    assistant_msg = {
        "role": "assistant",
        "content": assistant_output.content if assistant_output.content else "",
    }
    
    # 如果有工具调用，添加到字典中
    if assistant_output.tool_calls:
        # 将工具调用转换为字典格式
        tool_calls_dict = []
        for tc in assistant_output.tool_calls:
            tool_calls_dict.append({
                "id": tc.id,
                "function": {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments
                },
                "type": "function"
            })
        assistant_msg["tool_calls"] = tool_calls_dict
    
    messages.append(assistant_msg)            

    # 进入工具调用循环
    while assistant_output.tool_calls is not None:
        # 处理所有工具调用
        for tool_call in assistant_output.tool_calls:
            tool_call_id = tool_call.id
            func_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            print(f"正在调用工具 [{func_name}]，参数：{arguments}")
            
            if func_name == "get_current_weather":
                tool_result = get_current_weather(arguments)
            elif func_name == "get_weilai_weather":
                tool_result = get_weilai_weather(arguments)
            else:
                raise ValueError(f"未知函数: {func_name}")
            
            tool_message = {
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": tool_result,
            }
            print(f"工具返回：{tool_message['content']}")
            messages.append(tool_message)
        
        # 工具调用结果全部返回后，再次调用模型生成总结或继续调用工具
        response = get_response(messages)
        assistant_output = response.choices[0].message
        
        # 将 assistant_output 转换为字典格式
        assistant_msg = {
            "role": "assistant",
            "content": assistant_output.content if assistant_output.content else "",
        }
        
        if assistant_output.tool_calls:
            tool_calls_dict = []
            for tc in assistant_output.tool_calls:
                tool_calls_dict.append({
                    "id": tc.id,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    },
                    "type": "function"
                })
            assistant_msg["tool_calls"] = tool_calls_dict
        
        messages.append(assistant_msg)
    
    # 循环结束，此时 assistant_output 就是最终的回复（不再有 tool_calls）
    return assistant_output.content

def main():
    # 1. 初始化 messages，包含 System Message
    system_message = {
        "role": "system",
        "content": (
            "你是一个助手，你可以回答用户的问题。"
            "如果用户的问题不能用工具回答，你可以直接回答。"
        )
    }
    messages = [system_message]
    
    print("天气助手已启动，输入“退出”结束对话。")
    
    # 为了演示，可以先用一个默认问题
    # 但在交互模式下，建议直接让用户输入
    while True:
        user_input = input("\n您想问什么？> ")
        if user_input.lower() in ["退出", "exit", "quit"]:
            print("再见！")
            break
        
        # 将用户消息追加到 messages
        messages.append({"role": "user", "content": user_input})
        
        # 处理这一轮对话（包括可能的工具调用）
        final_reply = process_user_message(messages)
        print(f"助手：{final_reply}")
        
        # 注意：process_user_message 已经将 assistant 的最终回复追加到 messages 中，
        # 所以下一轮循环时，历史对话都会保留。

if __name__ == "__main__":
    main()