from openai import OpenAI
from dotenv import load_dotenv
import requests
import json
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor
from pydantic import BaseModel, Field, ValidationError
from datetime import datetime, timedelta
import pymysql

load_dotenv()

# ====================== 数据库配置（MySQL） ======================
DATABASE_TYPE = "mysql"
MYSQL_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "123456",
    "database": "student_db",
    "port": 3307
}

# ====================== 并发限制配置 ======================
MAX_CONCURRENT_TOOLS = 10  # 最大并发工具数（可手动调整）

# ====================== Pydantic 参数模型 ======================
class WeatherQueryParams(BaseModel):
    location: str = Field(description="城市或县区，比如北京市、杭州市、余杭区等。")

class MathQueryParams(BaseModel):
    math: str = Field(description="数学问题，如 2+3*4-5/2，支持 sqrt()")

class FileQueryParams(BaseModel):
    file_path: str = Field(description="本地文件路径（相对或绝对），不得包含..防越权")
    encoding: str = Field("utf-8", description="文件编码，默认utf-8")

class DateCalcParams(BaseModel):
    start_date: str = Field(None, description="开始日期，格式YYYY-MM-DD")
    end_date: str = Field(None, description="结束日期，格式YYYY-MM-DD")
    base_date: str = Field(None, description="基准日期，格式YYYY-MM-DD")
    days_delta: int = Field(None, description="天数增量，正数加，负数减")

class DatabaseQueryParams(BaseModel):
    sql: str = Field(..., description="SQL查询语句，仅支持SELECT")
    params: list = Field(default_factory=list, description="参数化查询的参数列表")

class TimeQueryParams(BaseModel):
    pass

# ====================== 工具定义（OpenAI格式） ======================
def pydantic_to_tool_definition(model, name, desc):
    json_schema = model.model_json_schema()
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": desc,
            "parameters": json_schema,
        },
    }

tools = [
    pydantic_to_tool_definition(WeatherQueryParams, "get_current_weather", "查询指定城市的当天天气"),
    pydantic_to_tool_definition(WeatherQueryParams, "get_weilai_weather", "查询指定城市的未来天气"),
    pydantic_to_tool_definition(MathQueryParams, "shuxjsj", "计算数学问题（加减乘除开方）"),
    pydantic_to_tool_definition(FileQueryParams, "read_file_content", "读取本地文件（防越权）"),
    pydantic_to_tool_definition(DateCalcParams, "date_calc", "日期计算：日期差 或 日期加减天数"),
    pydantic_to_tool_definition(DatabaseQueryParams, "db_query", "安全数据库查询（防SQL注入）"),
    pydantic_to_tool_definition(TimeQueryParams, "get_current_time", "查询当前时间"),
]

# ====================== 初始化DeepSeek客户端 ======================
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1",
)

# 高德天气API Key（请替换为你自己的有效Key）
KEY = "0036c67c5753a73ef6ddbeb3cd434049"

# ====================== 工具函数 ======================
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
        data_base = res_base.json()
        if "lives" in data_base and len(data_base["lives"]) > 0:
            weather = data_base["lives"][0]
            city = weather.get('city', '未知')
            weather_desc = weather.get('weather', '未知')
            temperature = weather.get('temperature', '未知')
            # 温度范围校验（实训要求 ±60℃）
            if temperature != '未知':
                temp_val = int(temperature)
                if temp_val > 60 or temp_val < -60:
                    return f"⚠️ 天气数据异常：{city}温度{temperature}°C超出正常范围（±60℃）"
            humidity = weather.get('humidity', '未知')
            wind_direction = weather.get('winddirection', '未知')
            wind_power = weather.get('windpower', '')
            return f"{city}当前天气：{weather_desc}，温度{temperature}°C，湿度{humidity}%，风力{wind_direction}{wind_power}级"
        else:
            error_info = data_base.get('info', '未获取到天气数据')
            return f"获取天气失败：{error_info}"
    except Exception as e:
        return f"获取天气数据失败：{str(e)}"

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
        data_all = res_all.json()
        if data_all.get("status") == "1":
            if "forecasts" in data_all and len(data_all["forecasts"]) > 0:
                forecast = data_all["forecasts"][0]
                city = forecast.get('city', '未知')
                if "casts" in forecast and len(forecast["casts"]) > 0:
                    weather_info = f"{city}未来天气预报：\n"
                    for day in forecast["casts"]:
                        date = day.get('date', '未知')
                        day_weather = day.get('dayweather', '未知')
                        night_weather = day.get('nightweather', '未知')
                        weather = day_weather if day_weather == night_weather else f"{day_weather}转{night_weather}"
                        nighttemp = day.get('nighttemp', '未知')
                        daytemp = day.get('daytemp', '未知')
                        weather_info += f"{date}: {weather}，温度{nighttemp}°C ~ {daytemp}°C\n"
                    return weather_info
                else:
                    return "获取天气预报失败：未返回预报信息"
            else:
                return "获取天气预报失败：未返回预报信息"
        else:
            error_info = data_all.get('info', '未知错误')
            return f"获取天气预报失败：{error_info}"
    except Exception as e:
        return f"获取天气预报失败：{str(e)}"

def get_current_time(arguments=None):
    now = datetime.now()
    time_str = now.strftime("%Y年%m月%d日 %H:%M:%S 星期%w")
    return f"\n======= 当前系统时间 =======\n{time_str}\n==========================\n"

def shuxjsj(arguments):
    expr = arguments["math"]
    # 安全校验：只允许数字、运算符、括号、空格、小数点、sqrt函数
    if not re.fullmatch(r'[\d+\-*/()sqrt.\s]+', expr, re.I):
        return f"❌ 参数校验失败：表达式包含非法字符"
    try:
        import math
        # 严格限制全局命名空间，只允许 sqrt
        allowed = {"sqrt": math.sqrt, "__builtins__": None}
        result = eval(expr, allowed, {})
        return f"{expr} = {result}"
    except Exception as e:
        return f"计算错误：{e}"

def read_file_content(arguments):
    file_path = arguments["file_path"]
    encoding = arguments.get("encoding", "utf-8")
    # 防路径越权：禁止包含..且必须位于当前工作目录下
    abs_path = os.path.abspath(file_path)
    cwd = os.path.abspath(os.getcwd())
    if not abs_path.startswith(cwd):
        return f"❌ 安全错误：禁止访问工作目录外的文件（{file_path}）"
    if ".." in file_path or (file_path.startswith("/") and not file_path.startswith(cwd)):
        return f"❌ 安全错误：路径包含越权符号（{file_path}）"
    try:
        with open(abs_path, encoding=encoding) as f:
            content = f.read(10000)  # 限制最大读取长度
            return f"文件内容：\n{content}"
    except Exception as e:
        return f"读取文件失败：{e}"

def date_calc(arguments):
    start_date = arguments.get("start_date")
    end_date = arguments.get("end_date")
    base_date = arguments.get("base_date")
    days_delta = arguments.get("days_delta")

    if start_date and end_date:
        try:
            d1 = datetime.strptime(start_date, "%Y-%m-%d")
            d2 = datetime.strptime(end_date, "%Y-%m-%d")
            diff = abs((d2 - d1).days)
            return f"从 {start_date} 到 {end_date} 相差 {diff} 天"
        except ValueError:
            return "⚠️ 参数校验失败：日期格式必须为 YYYY-MM-DD"
    elif base_date is not None and days_delta is not None:
        try:
            d = datetime.strptime(base_date, "%Y-%m-%d")
            new_date = d + timedelta(days=days_delta)
            op = "加" if days_delta >= 0 else "减"
            return f"{base_date} {op} {abs(days_delta)} 天后是 {new_date.strftime('%Y-%m-%d')}"
        except ValueError:
            return "⚠️ 参数校验失败：基准日期格式必须为 YYYY-MM-DD"
    else:
        return "⚠️ 参数校验失败：请提供 (start_date+end_date) 或 (base_date+days_delta) 参数组合"

# ====================== 数据库连接（MySQL） ======================
_db_conn = None

def get_db_connection():
    global _db_conn
    if _db_conn is None:
        _db_conn = pymysql.connect(**MYSQL_CONFIG)
    return _db_conn

def db_query(arguments):
    sql = arguments["sql"]
    params = arguments.get("params", [])

    if not sql or not sql.strip():
        return "错误：SQL 语句不能为空"
    sql_upper = sql.strip().upper()
    if not sql_upper.startswith("SELECT"):
        return "错误：仅允许 SELECT 查询，禁止 INSERT/UPDATE/DELETE/DROP 等操作"

    dangerous_keywords = [
        "DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "CREATE",
        "EXEC", "EXECUTE", "UNION", "INTO", "LOAD", "DUMP",
        "OUTFILE", "SLEEP", "BENCHMARK", "SCRIPT", "JAVASCRIPT"
    ]
    for keyword in dangerous_keywords:
        if keyword in sql_upper:
            return f"错误：SQL 中包含禁止的关键字 '{keyword}'，请使用参数化查询避免注入"

    if re.search(r'--|#|/\*', sql):
        return "错误：SQL 中不能包含注释符（--, #, /*）"

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        rows = cursor.fetchall()
        if not rows:
            return "查询结果为空"
        # 获取列名
        col_names = [desc[0] for desc in cursor.description]
        result_lines = []
        for row in rows:
            row_dict = dict(zip(col_names, row))
            result_lines.append(str(row_dict))
        return "查询结果：\n" + "\n".join(result_lines)
    except pymysql.Error as e:
        return f"数据库查询错误：{e}"
    finally:
        if cursor:
            cursor.close()
        # 注意：不要关闭 conn，保持长连接

# ====================== 工具注册表 + 分发器 ======================
tool_registry = {
    "get_current_weather": (get_current_weather, WeatherQueryParams),
    "get_weilai_weather": (get_weilai_weather, WeatherQueryParams),
    "get_current_time": (get_current_time, TimeQueryParams),
    "read_file_content": (read_file_content, FileQueryParams),
    "date_calc": (date_calc, DateCalcParams),
    "db_query": (db_query, DatabaseQueryParams),
    "shuxjsj": (shuxjsj, MathQueryParams),
}

def dispatch_tool(func_name, func_args):
    if func_name not in tool_registry:
        return f"❌ 不存在工具：{func_name}"
    tool_func, param_model = tool_registry[func_name]
    try:
        valid_params = param_model(**func_args)
        clean_params = valid_params.model_dump(exclude_unset=True)
        return tool_func(clean_params)
    except ValidationError as e:
        # 返回简洁的错误提示，方便大模型修正
        errors = []
        for err in e.errors():
            field = ".".join(err["loc"])
            msg = err["msg"]
            errors.append(f"{field}: {msg}")
        return f"⚠️ 参数校验失败：{'; '.join(errors)}"
    except Exception as e:
        return f"❌ 工具执行异常：{str(e)}"

# ====================== 单工具并行执行包装 ======================
def run_single_tool(tool_call):
    func_name = tool_call.function.name
    func_args = json.loads(tool_call.function.arguments)
    print(f"[并行线程] 调用工具 [{func_name}]，参数：{func_args}")
    res = dispatch_tool(func_name, func_args)
    return {
        "tool_call_id": tool_call.id,
        "content": res
    }

# ====================== 流式请求处理 ======================
def get_response(messages):
    start = time.time()
    completion = client.chat.completions.create(
        model="deepseek-v4-pro",
        messages=messages,
        tools=tools,
        stream=True,
        parallel_tool_calls=True,
        extra_body={"enable_thinking": True}
    )
    cost = round(time.time() - start, 3)
    print(f"请求耗时：{cost}秒")
    reasoning_content = ""
    answer_content = ""
    tool_info = []
    is_answering = False

    print("\n" + "=" * 20 + "思考过程" + "=" * 20)

    for chunk in completion:
        if not chunk.choices:
            if hasattr(chunk, 'usage') and chunk.usage:
                print("\n" + "=" * 20 + "Usage" + "=" * 20)
                print(chunk.usage)
            continue

        delta = chunk.choices[0].delta

        if hasattr(delta, 'reasoning_content') and delta.reasoning_content is not None:
            reasoning_content += delta.reasoning_content
            print(delta.reasoning_content, end="", flush=True)

        if delta.content is not None:
            if not is_answering:
                is_answering = True
                print("\n" + "=" * 20 + "回复内容" + "=" * 20)
            answer_content += delta.content
            print(delta.content, end="", flush=True)

        if delta.tool_calls is not None:
            for tool_call in delta.tool_calls:
                index = tool_call.index
                while len(tool_info) <= index:
                    tool_info.append({"id": "", "name": "", "arguments": ""})
                if tool_call.id:
                    tool_info[index]["id"] += tool_call.id
                if tool_call.function:
                    if tool_call.function.name:
                        tool_info[index]["name"] += tool_call.function.name
                    if tool_call.function.arguments:
                        tool_info[index]["arguments"] += tool_call.function.arguments

    print("\n" + "=" * 19 + "工具调用信息" + "=" * 19)
    if not tool_info:
        print("没有工具调用")
    else:
        print(tool_info)

    # 构造模拟响应
    class MockToolCall:
        def __init__(self, info):
            self.id = info["id"]
            self.function = type('obj', (object,), {
                'name': info["name"],
                'arguments': info["arguments"]
            })

    class MockMessage:
        def __init__(self):
            self.content = answer_content if answer_content else None
            self.tool_calls = [MockToolCall(info) for info in tool_info] if tool_info else None

    class MockChoice:
        def __init__(self, message):
            self.message = message

    class MockCompletion:
        def __init__(self, choices):
            self.choices = choices

    return MockCompletion([MockChoice(MockMessage())])

# ====================== 主程序入口 ======================
# ====================== 循环问答主程序 ======================
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("欢迎使用轻量级 Function Calling 多工具集成平台")
    print("支持工具：天气查询、数学计算、文件读取、日期计算、数据库查询、当前时间")
    print("输入 'exit' 或 'quit' 或 '退出' 结束对话")
    print("=" * 60 + "\n")

    # 初始化对话历史（可保留上下文）
    messages = []
    total_start = time.time()

    while True:
        try:
            user_input = input(" 请输入:  ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "退出"):
                print("\n👋 再见！")
                break

            # 将用户消息加入历史
            messages.append({"role": "user", "content": user_input})

            # 调用模型获取回复（可能包含工具调用）
            response = get_response(messages)
            assistant_output = response.choices[0].message
            if assistant_output.content is None:
                assistant_output.content = ""

            # 构建助手消息并加入历史
            assistant_msg = {
                "role": "assistant",
                "content": assistant_output.content,
            }
            if assistant_output.tool_calls:
                assistant_msg["tool_calls"] = [
                    {
                        "id": tc.id,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        },
                        "type": "function"
                    }
                    for tc in assistant_output.tool_calls
                ]
            messages.append(assistant_msg)

            # 判断是否有工具调用
            if not assistant_output.tool_calls:
                # 无工具调用，直接输出回复
                print(f"\n🤖 助手: {assistant_output.content}")
            else:
                print(f"\n🔧 模型一次性下发 {len(assistant_output.tool_calls)} 个工具任务，开启多线程并行执行（最大并发 {MAX_CONCURRENT_TOOLS}）...")
                tool_start = time.time()
                with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_TOOLS) as pool:
                    all_tool_results = list(pool.map(run_single_tool, assistant_output.tool_calls))
                tool_cost = round(time.time() - tool_start, 3)
                print(f"\n⏱️ [全部工具并行执行总耗时] {tool_cost} s")

                # 将工具执行结果加入对话历史
                for item in all_tool_results:
                    print(f"\n📦 [工具返回结果]\n{item['content']}")
                    messages.append({
                        "role": "tool",
                        "tool_call_id": item["tool_call_id"],
                        "content": item["content"]
                    })

                # 将工具结果发回模型，获取最终整合回复
                final_response = get_response(messages)
                final_ans = final_response.choices[0].message.content
                print("\n🤖 助手最终整合回复:")
                print(final_ans)

                # 将助手的最终回复也加入历史（注意：这里助手回复只有 content，没有 tool_calls）
                messages.append({"role": "assistant", "content": final_ans})

        except KeyboardInterrupt:
            print("\n\n👋 检测到中断，退出程序。")
            break
        except Exception as e:
            print(f"\n⚠️ 发生错误: {e}")
            # 可选择是否继续循环
            continue

    total_cost = round(time.time() - total_start, 3)
    print(f"\n🏁 程序运行总耗时：{total_cost} 秒")