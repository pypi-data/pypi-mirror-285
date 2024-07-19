
import ipaddress
import proxy
import asyncio
from csservices import portforward
async def on_command(args):
    """端口转发"""
    print('port====')
    #暂时写死
    options={
        "ports":[
                        "http://0.0.0.0:8080@www.google.com:80",
                        # "http://0.0.0.0:9090@127.0.0.1:49090"
            ]
        }
    loop  = asyncio.get_event_loop()
    task = loop.create_task(portforward.PortService().start(options))       
    # asyncio.run(task)
    done, pending = await asyncio.wait({task})
    print('命令运行结束')     
    # deamonTasks.append(task)