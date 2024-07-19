# tar 归档文件实用工具
import logging
import os
import tarfile
from io import BytesIO

# from os.path import relpath
# from pathlib import Path

logger = logging.getLogger(__file__)
# def tarFolder(src, tar_name):
#     """创建tar.gz文件, 压缩包里面使用相对路径"""
#     """功能正常,但是暂时用不上,因为github本身就提供压缩包的下载"""
#     abs_src = os.path.abspath(src)
#     if not Path(tar_name).parent.exists():
#         Path(tar_name).parent.mkdir()
#     with tarfile.open(tar_name, "w:gz") as tar_handle:
#         for dirname, subdirs, files in os.walk(src):
#             for filename in files:
#                 absname = os.path.abspath(os.path.join(dirname, filename))
#                 arcname = absname[len(abs_src) + 1:]
#                 print('zipping %s as %s' % (os.path.join(dirname, filename),
#                                             arcname))
#                 tar_handle.add(absname, arcname)


def tarFolder(base_dir, fileObj):
    """
        将目录下的所有文件,生成归档格式,
        :fileObj 是类文件对象, 例如:可以是 BytesIO , 或者 普通 open()打开的的文件对象
        用法:
            bytesObj = BytesIO()
            tar_helper.tarFolder(str(current_dir),bytesObj)
            bytesObj.seek(0)"""
    tar_obj = tarfile.TarFile(fileobj=fileObj, mode='w')

    for dirname, subdirs, files in os.walk(base_dir):
        for filename in files:
            absname = os.path.abspath(os.path.join(dirname, filename))
            arc_name = absname[len(base_dir) + 1:]
            with open(os.path.abspath(os.path.join(dirname, filename)),
                      'rb') as f:
                file_bytes = f.read()

                tarinfo = tarfile.TarInfo(name=arc_name)
                tarinfo.size = len(file_bytes)
                # 可以设置文件的其他属性
                # tarinfo.mtime = time.time()
                # tarinfo.mode = 0600
                tar_obj.addfile(tarinfo, BytesIO(file_bytes))
                logger.debug('tar file add : %s ' % (filename))
