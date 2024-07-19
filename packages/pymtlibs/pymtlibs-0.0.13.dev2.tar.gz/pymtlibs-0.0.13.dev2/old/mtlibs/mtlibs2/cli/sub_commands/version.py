from mtlibs import mtutils

def on_command(args):
    """显示内部信心"""
    print('debug info====')
    print('is in github action',mtutils.isInGhAction())
    print('is in gitPod',mtutils.isInGitPod())