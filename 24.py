import requests
import re

KEY = "0036c67c5753a73ef6ddbeb3cd434049"

def get_weather(city, option):
    url = "https://restapi.amap.com/v3/weather/weatherInfo"
    
    city = city.strip()
    
    if not city:
        print("X 请输入正确城市")
        return
    
    if not re.search('[\u4e00-\u9fa5]', city):
        print("X 请输入正确城市(必须是中文城市名)")
        return
    
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
            print(f"API返回数据: {data_base}")  # 调试信息
            
            if data_base.get("status") == "1":
                if "lives" in data_base and len(data_base["lives"]) > 0:
                    weather = data_base["lives"][0]
                    # 检查必要字段
                    if "city" in weather and "weather" in weather:
                        print(f"城市: {weather['city']}")
                        print(f"天气: {weather['weather']}")
                        print(f"温度: {weather.get('temperature', '未知')}°C")
                        print(f"湿度: {weather.get('humidity', '未知')}%")
                        print(f"风力: {weather.get('winddirection', '未知')} {weather.get('windpower', '')}级")
                    else:
                        print("X 返回数据缺少必要字段")
                else:
                    print("X 未获取到天气数据")
            else:
                print(f"X API返回错误: {data_base.get('info', '未知错误')}")
        except requests.exceptions.RequestException as e:
            print(f"X 请求失败: {e}")
        except KeyError as e:
            print(f"X 解析数据失败: 缺少字段 {e}")
        except Exception as e:
            print(f"X 未知错误: {e}")
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
                    print(f"城市: {forecast.get('city', '未知')}")
                    print("未来天气预报:")
                    if "casts" in forecast and len(forecast["casts"]) > 0:
                        for day in forecast["casts"]:
                            print(f"日期: {day.get('date', '未知')}")
                            print(f"  天气: {day.get('weather', '未知')}")
                            print(f"  温度: {day.get('nighttemp', '未知')}°C ~ {day.get('daytemp', '未知')}°C")
                            print(f"  风力: {day.get('winddirection', '未知')} {day.get('windpower', '')}级")
                            print()
                    else:
                        print("X 未获取到预报数据")
                else:
                    print("X 未获取到天气数据")
            else:
                print(f"X API返回错误: {data_all.get('info', '未知错误')}")
        except requests.exceptions.RequestException as e:
            print(f"X 请求失败: {e}")
        except KeyError as e:
            print(f"X 解析数据失败: 缺少字段 {e}")
        except Exception as e:
            print(f"X 未知错误: {e}")
    else:
        print("X 无效选项")

if __name__ == "__main__":
    city = input("请输入城市名: ")
    option = input("请选择选项(1-实况天气, 2-未来预报): ")
    get_weather(city, option)