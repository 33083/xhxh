import requests
import re
import sys
import os
from datetime import datetime
from openai import OpenAI
from openai import APIConnectionError
from dotenv import load_dotenv

load_dotenv()


class LLM:
    PLATFORMS = {
        "deepseek": {
            "base_url": "https://api.deepseek.com/v1",
            "model": "deepseek-v4-pro",         
        }
    }

    def __init__(self, platform: str, api_key: str = None):
        config = self.PLATFORMS[platform]
        if api_key is None:
            api_key = os.getenv(f"{platform.upper()}_API_KEY")
        self.client = OpenAI(
            api_key=api_key,
            base_url=config["base_url"],
        )
        self.model = config["model"]
        self.temperature = 0.7
        self.platform = platform

    def chat_stream(self, messages: list, max_tokens: int = 300):
        """流式生成器，逐块返回内容"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=max_tokens,
                stream=True,
            )
        except APIConnectionError as e:
            yield f"网络连接失败：{str(e)}"
            return
        except Exception as e:
            yield f"请求失败：{str(e)}"
            return

        for chunk in response:
            delta = chunk.choices[0].delta
            content = delta.content if delta and delta.content else ""
            if content:
                yield content
    
    def chat(self, prompt: str):
        """简单的聊天接口，直接返回完整响应"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
            )
            return response.choices[0].message.content
        except APIConnectionError as e:
            return f"网络连接失败：无法连接到 {self.platform} API"
        except Exception as e:
            return f"请求失败：{str(e)}"


KEY = "0036c67c5753a73ef6ddbeb3cd434049"

def get_weather(city, option):
    url = "https://restapi.amap.com/v3/weather/weatherInfo"
    
    city = city.strip()
    
    if not city:
        print("X 请输入正确城市")
        return None
    
    if not re.search('[\u4e00-\u9fa5]', city):
        print("X 请输入正确城市(必须是中文城市名)")
        return None
    
    if option == '1':
        params_base = {
            "city": city,
            "key": KEY,
            "extensions": "base",
            "output": "JSON"
        }
        try:
            res_base = requests.get(url, params=params_base, timeout=10)
            print(f"HTTP状态码: {res_base.status_code}")
            
            data_base = res_base.json()
            
            if data_base.get("status") == "1":
                if "lives" in data_base and len(data_base["lives"]) > 0:
                    weather = data_base["lives"][0]
                    # 检查必要字段
                    if "city" in weather and "weather" in weather:
                        city_name = weather['city']
                        weather_desc = weather['weather']
                        temperature = weather.get('temperature', '未知')
                        humidity = weather.get('humidity', '未知')
                        wind_dir = weather.get('winddirection', '未知')
                        wind_power = weather.get('windpower', '')
                        
                        print(f"城市: {city_name}")
                        print(f"天气: {weather_desc}")
                        print(f"温度: {temperature}°C")
                        print(f"湿度: {humidity}%")
                        print(f"风力: {wind_dir} {wind_power}级")
                        
                        # 返回天气描述字符串
                        return f"{city_name} {weather_desc} {temperature}°C 湿度{humidity}%"
                    else:
                        print("X 返回数据缺少必要字段")
                        return None
                else:
                    print("X 未获取到天气数据")
                    return None
            else:
                print(f"X API返回错误: {data_base.get('info', '未知错误')}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"X 请求失败: {e}")
            return None
        except KeyError as e:
            print(f"X 解析数据失败: 缺少字段 {e}")
            return None
        except Exception as e:
            print(f"X 未知错误: {e}")
            return None
    elif option == '2':
        params_all = {
            "city": city,
            "key": KEY,
            "extensions": "all",
            "output": "JSON"
        }
        try:
            res_all = requests.get(url, params=params_all, timeout=10)
            print(f"HTTP状态码: {res_all.status_code}")
            
            data_all = res_all.json()
            
            if data_all.get("status") == "1":
                if "forecasts" in data_all and len(data_all["forecasts"]) > 0:
                    forecast = data_all["forecasts"][0]
                    city_name = forecast.get('city', '未知')
                    print(f"城市: {city_name}")
                    print("未来天气预报:")
                    
                    forecast_str = f"{city_name}未来天气: "
                    if "casts" in forecast and len(forecast["casts"]) > 0:
                        day_descs = []
                        for day in forecast["casts"]:
                            date = day.get('date', '未知')
                            weather_desc = day.get('weather', '未知')
                            night_temp = day.get('nighttemp', '未知')
                            day_temp = day.get('daytemp', '未知')
                            
                            print(f"日期: {date}")
                            print(f"  天气: {weather_desc}")
                            print(f"  温度: {night_temp}°C ~ {day_temp}°C")
                            print(f"  风力: {day.get('winddirection', '未知')} {day.get('windpower', '')}级")
                            print()
                            
                            day_descs.append(f"{date} {weather_desc} {night_temp}°C~{day_temp}°C")
                        
                        forecast_str += "；".join(day_descs)
                        return forecast_str
                    else:
                        print("X 未获取到预报数据")
                        return None
                else:
                    print("X 未获取到天气数据")
                    return None
            else:
                print(f"X API返回错误: {data_all.get('info', '未知错误')}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"X 请求失败: {e}")
            return None
        except KeyError as e:
            print(f"X 解析数据失败: 缺少字段 {e}")
            return None
        except Exception as e:
            print(f"X 未知错误: {e}")
            return None
    else:
        print("X 无效选项")
        return None

if __name__ == "__main__":
    city = input("请输入城市名: ")
    option = input("请选择选项(1-实况天气, 2-未来预报): ")
    weather_info = get_weather(city, option)
    llm = LLM("deepseek")
    if weather_info:
        print("DeepSeek:", llm.chat(f"这种{weather_info}天气适合穿什么衣服，输出美观一点"))
    else:
        print("无法获取天气信息，无法提供穿衣建议")