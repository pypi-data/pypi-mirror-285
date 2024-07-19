
import ipaddress
import proxy

def on_command(args):
    """显示内部信心"""
    print('proxy====')
    proxy.main(
        # hostname=ipaddress.IPv6Address('::1'),
        hostname=ipaddress.IPv4Address('0.0.0.0'),
        port=8899
    )