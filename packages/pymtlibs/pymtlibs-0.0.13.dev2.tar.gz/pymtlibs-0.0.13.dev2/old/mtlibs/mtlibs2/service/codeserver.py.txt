import os
from stem.util import term


def start():
    """
        启动 vpn 服务
    """
    print(term.format("启动 codeserver", term.Color.RED), flush=True)

    os.system("sudo -u {nottor_user} bash -c 'code-server --link cli_container &'".format(
        nottor_user=os.environ.get("NOTTOR_USER",'nottor')
    ))

    
if __name__ == '__main__':
    start()