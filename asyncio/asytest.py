import time
import asyncio
import requests

# 定义异步函数
async def test(url):
    print('start')
    await hello()

async def hello():
    return 1

url = 'https://www.baidu.com'

a = test(url)




