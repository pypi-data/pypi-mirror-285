import asyncio
from urllib.parse import urlparse
from mtlibs.mtutils import pipe

class SimpleHttpService:
    """端口转发服务"""
    async def handle_tcp_portforward(reader, writer, targetHost,targetPort):
        """tcp端口转发"""
        try:
            targetReader, targetWriter = await asyncio.open_connection(self.targetHost, self.targetPort)
            asyncio.create_task(pipe(reader, targetWriter))
            asyncio.create_task(pipe(targetReader, writer))
            addr1 = writer.get_extra_info('sockname')
            addr2 = writer.get_extra_info('peername')
            addr3 = targetWriter.get_extra_info('sockname')
            addr4 = targetWriter.get_extra_info('peername')
            print(f'''新的连接 {addr1!r} {addr2!r}-- {addr3!r} {addr4!r}''')
        except ConnectionRefusedError as e:
            # print("远程计算机拒绝网络连接")
            print(e)


    async def start(self,args):
        print(args)
        print('配置字符串',args.configurl)
        uri =  urlparse(args.configurl)
        self.localPort = uri.password
        self.localHost = uri.username
        self.remoteHost = uri.hostname,
        self.remotePort = uri.port or 80
        server = await asyncio.start_server(self.handle_tcp_portforward, self.localHost, self.localPort)
        addr = server.sockets[0].getsockname()
        print(f'tcp portforward Serving on {addr[0]}:{addr[1]}--->{self.remoteHost[0]}:{self.remotePort}')
        async with server:
            await server.serve_forever()




