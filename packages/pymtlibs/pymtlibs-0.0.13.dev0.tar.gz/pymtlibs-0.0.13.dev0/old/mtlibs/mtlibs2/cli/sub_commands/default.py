import threading
import asyncio
import types
import config
import time
from flask import Flask

from csservices import portforward
from csservices import flaskapp
from csservices import clash
from csservices import tor
from csservices import vpn

from csservices import flaskapp
async def on_command(args):
    """
        用独立的线程处理异步后台服务，
        因为放主线程会被其他应用干扰，例如flask app.run会阻塞事件循环。
    """
    # thread_event_loop = asyncio.new_event_loop() #若在新线程中，要创建线程专用的事件循环。
    # asyncio.set_event_loop(thread_event_loop)

    thread_event_loop = asyncio.get_event_loop()
    deamonTasks = [] #后台任务
    appconfig = config.getConfig()
    print('配置文件：',appconfig)

    if appconfig.get('services'):
        for k,v in appconfig["services"].items():
            print(f'服务 {k}')
            if 'portforward' == k : 
                task = thread_event_loop.create_task(portforward.PortService().start(v))            
                deamonTasks.append(task)
            elif 'http' ==k:
                # 这个特殊对待。使用线程。
                threading.Thread(target=flaskapp.FlaskService().start).start()
                # deamonTasks.append(thread_event_loop.create_task(flaskapp.FlaskService().start(v)))
            elif 'clash' == k:
                deamonTasks.append(thread_event_loop.create_task(clash.ClashService().start(v)))
            elif 'tor' ==k:
                deamonTasks.append(thread_event_loop.create_task(tor.TorService().start(v)))
            elif 'vpn' ==k:
                deamonTasks.append(thread_event_loop.create_task(vpn.VpnService().start(v)))
            else:
                raise Exception(f"未知的服务配置{k}")

    # 等待全部结束  
    print(f"后台服务数量：{len(deamonTasks)}")
    for coro in asyncio.as_completed(deamonTasks):
        try:
            earliest_result = await coro        
            print("一个任务完成",earliest_result,coro)
        except Exception as err:
            print("异步工作完成，但是有错误，",err)

        # print('earliest_result',earliest_result)
        # print('错误',earliest_result.exception())

    # thread_event_loop.run_forever()



