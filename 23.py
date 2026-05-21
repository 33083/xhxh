import requests
response=requests.get('https://httpbin.org/ip')
print(response.status_code)
if response.status_code==200:
    print('请求成功')
# print(response.headers)
# print(response.text)

# url='https://httpbin.org/get'
# payload={
#     'name':'张三',
#     'age':'25',
#     'city':'Beijing'
# }
# res=requests.get(url,params=payload)
# print(res.url)
print(response.json())
a=response.json()
print(a['origin'])
# resp=requests.get('https://httpbin.org/status/404')
# # print(type(resp.text))
# # data=resp.json()
# # print(type(data))
# print(resp.status_code)
# try:
#     resp.raise_for_status()
# except requests.HTTPError as e:
#     print(e)
try:
    r=requests.get('https://httpbin.org/ip', timeout=1)
    r.raise_for_status()
    print('请求成功')
except requests.exceptions.Timeout:
    print('请求超时')
except requests.exceptions.RequestException as e:
    print('未知错误')