import asyncio
import logging
import os
import shlex
import subprocess
import tempfile
import traceback
from mtlibs import mtutils, process_helper
from mtlibs.mtutils import ranstr
logger = logging.getLogger(__name__)
class OpenvpnClientProc():
    """
        openvpn 客户端进程
        可以考虑整个ovpn从yml config这里整个填写，而不用分开host port proto key 等信息。:
    """

    def __init__(self, ovpn):
        self.tmpdirname = tempfile.gettempdir() + "/openvpn_" + ranstr(20)
        self.ovpn = ovpn
        # self.host = host
        # self.port = port
        # self.proto= proto
        # self.key=key

    def write_openvpnconfig(self):
        self.pki_base_path = os.path.abspath("./data/openvpn/pki")
        self.ccd_path = os.path.abspath("./data/openvpn/ccd")
        self.openvpn_config_path = self.tmpdirname + "/openvpn.conf"
        mtutils.writefile(self.openvpn_config_path, self.ovpn.encode())
        # client1.ovpn


#         mtutils.writefile(self.openvpn_config_path,"""
# client
# nobind
# dev tun
# remote-cert-tls server
# <key>
# {key}
# </key>
# <cert>
# -----BEGIN CERTIFICATE-----
# MIIDVTCCAj2gAwIBAgIQfjDxXG3QojWJqt/yHJTZbjANBgkqhkiG9w0BAQsFADAW
# MRQwEgYDVQQDDAtFYXN5LVJTQSBDQTAeFw0yMTA1MjcwOTUxNTlaFw0yMzA4MzAw
# OTUxNTlaMBIxEDAOBgNVBAMMB2NsaWVudDEwggEiMA0GCSqGSIb3DQEBAQUAA4IB
# DwAwggEKAoIBAQCkduSZA+yMcpDNj2tvAToDkZNn4as0w7VQr6Rtk+J6UJeMX/ey
# wNUGrmUkBvwlJRp5hfZiummFSwhr1T7/mXawkLvtJW7z+cRyPPEeUZ7HclC0GTp8
# xbELfdI6wxPoezI5faGg8Qep5KR4kJuU8FQ1B7QxNkVP8Owu/CazRRuELG0QssIs
# vPXIEgXs1jAUNT8HvU39ARHIdzhnRtELUqW0vKae6paDSRklYyxqaUt6po+xaJQ2
# 2xkEagU+R6rDzwhyNEOnNyfKRj9PCsOACTou1IxZGBuSRE2VBaMgmMevygSS1XkC
# fPHBFcbrjw7fiOX4KWdV2RlCIRCgI7uHtrUJAgMBAAGjgaIwgZ8wCQYDVR0TBAIw
# ADAdBgNVHQ4EFgQUFrj/q3NsCq7jvLK+xxLIw/vvR8UwUQYDVR0jBEowSIAUiyDv
# HnmqCFSDiba2OLD7PngWoWKhGqQYMBYxFDASBgNVBAMMC0Vhc3ktUlNBIENBghR5
# fHYry44n8OdznFdjjDbP5ng+vTATBgNVHSUEDDAKBggrBgEFBQcDAjALBgNVHQ8E
# BAMCB4AwDQYJKoZIhvcNAQELBQADggEBAGwzTOEFOm7ETisycezWnPJXsbDtU9Ia
# /IwD3lNm+RXPoMDrwCqyNO1ySQmW8upuyYCaPMChTrEgWCJQdTwrBsO8hr2RUsYP
# HbKV7GmEweP6gq04HZLHnaLP/xf9GkIrCu4FjvMFq7kGJ1JUdlrUor3yTXqagU05
# 6m0f2W8dGmHQT2riH1JotY590z813E+tnSFqFj5telpMbsSetRR7B8KX3SASasKV
# RrqtfSY4ul0DVM5v6SFyst+UOxnBTK1FUqweOogZtt9r0b/rO8odO79I5KeKBOxi
# vIvsE6xZ/fPF5EJ9tR9ZKEU1iHiChMZ8kRNgZlVb4+zAxr+CMQUuSGE=
# -----END CERTIFICATE-----
# </cert>
# <ca>
# -----BEGIN CERTIFICATE-----
# MIIDSzCCAjOgAwIBAgIUeXx2K8uOJ/Dnc5xXY4w2z+Z4Pr0wDQYJKoZIhvcNAQEL
# BQAwFjEUMBIGA1UEAwwLRWFzeS1SU0EgQ0EwHhcNMjEwNTI3MDk1MDMzWhcNMzEw
# NTI1MDk1MDMzWjAWMRQwEgYDVQQDDAtFYXN5LVJTQSBDQTCCASIwDQYJKoZIhvcN
# AQEBBQADggEPADCCAQoCggEBAKwNo0TmEv9Zpc/1v2zHMwzqCd484tmxWPAij8oU
# lr0BovXOiQ6f2P5Qvq2oRby0msxmcNHBQBhMGbibyrISDPoY7WYdggNDB0P/aZks
# G+qXJwo7iDfAs094M3omO0Bz5dp5YFrIQoO2oaroxX+NFciy6J872muylmfwU8O+
# ajX/s2Ov3CMmkwMml6qB8pUwnvfadV+cX1rFE1cxZfU3x73ySnPOlFYVJ5nch2Ac
# UzTNCz0Pt7OneQ06kmyWFIUS92a/+eAWO/VcRp9cOig4JYhat6EfwdA/aCjTLpDO
# X6ZYtP6JwPb5rO0+BeEXz70IZAjDuNnNw/MuSV78NwyheksCAwEAAaOBkDCBjTAd
# BgNVHQ4EFgQUiyDvHnmqCFSDiba2OLD7PngWoWIwUQYDVR0jBEowSIAUiyDvHnmq
# CFSDiba2OLD7PngWoWKhGqQYMBYxFDASBgNVBAMMC0Vhc3ktUlNBIENBghR5fHYr
# y44n8OdznFdjjDbP5ng+vTAMBgNVHRMEBTADAQH/MAsGA1UdDwQEAwIBBjANBgkq
# hkiG9w0BAQsFAAOCAQEABABlAKPETJ3+ivNzaqSz/QuElm4YfBPaukADckGh2ES5
# /T/SXNvSe4+hmTYq8WS0fDZE5n1sWTUR/Qb+KlTAWkTc8+HWHJaN3S0MWG0wtbsQ
# jH8FQKbb4pO40eVOdtZV0TjHbo/tDy4tkYBl8WFRAFomktAQaI8RjsgIe1dYyDon
# GsIffaOx1nnGw74AsDD8NTLaRAVLVX2qGLslSM7amc/XhLQKGuMwm4/pV4k47zyX
# wIQPx3BHoOgDTXtjvo3u4zTerzOS0Vq0CFeP024bK9G0IKlG6AQOzg30wRfeeB9Z
# jCGtJ4vzS2EkEN5CtvqYD0bPWp1i6hX61ZRQKyp9Xw==
# -----END CERTIFICATE-----
# </ca>
# key-direction 1
# <tls-auth>
# #
# # 2048 bit OpenVPN static key
# #
# -----BEGIN OpenVPN Static key V1-----
# ce5697cb2037f7977386df5744226ee3
# 8a69f892d69af37b210cb6e7e6f51d15
# b74003290477dac0ccc9d3434567e205
# 8386436418be5bde673c01dc53203211
# ed4a66835e393fd2f5f5dbafff9a08df
# 45744c9cc4088a957de3f67a7aad4b6e
# d92ee87413ea24e126b98dafc6a351aa
# 61fc86c0d1cb10b2a0bde19dfb7747bc
# 93bf68a045f10050495edd99652d4a3c
# e76593ab4c0f960a2fd2dbb199bfee87
# 20dc8e68a9f00c0b5fbf2538f703cc71
# b04a759d55795c692e04a2bd0f070bd4
# 963b5b8ecfadf2e65df18b430fa0778e
# 9e1d955e99a14b1ec63c003db9bbcd8b
# 74564c86d6e90d91bf94e730bcdf32d5
# bf61149dd85d40221c191e5dd6c3dd5d
# -----END OpenVPN Static key V1-----
# </tls-auth>

# redirect-gateway def1

# """.format(
#     host=self.host,
#     port=self.port,
#     proto=self.proto,
#     key=self.key
#     ).encode())

    async def handle_output(self):
        try:
            while True:
                if self.process.stdout:
                    line = self.process.stdout.readline().decode().strip()
                    logger.debug("vpnclient->{}".format(line))
                    if line.strip().find(
                            'Initialization Sequence Completed') > 0:
                        return "ok"
                    # TODO: 捕获失败的字符串，返回
                    # 要不然，进程启动失败会卡住,协程一直不退出

                if self.process.stderr:
                    line = self.process.stderr.readline().decode()
                    logger.info("vpn->[error]{}".format(line))
                if self.process.poll() is not None:
                    break
        except Exception as e:
            logger.error(traceback.format_exc(e))

    async def start(self):
        """启动openvpn进程"""
        self.write_openvpnconfig()
        # 必要的初始化
        bash_init = """
mkdir -p /dev/net
if [ ! -c /dev/net/tun ]; then
    mknod /dev/net/tun c 10 200
fi
"""
        process_helper.bash(bash_init)
        cmd = "openvpn --config {config}".format(
            # host=self.host,
            # port =self.port,
            # proto=self.proto,
            config=self.openvpn_config_path)
        logger.debug("执行命令：{}".format(cmd))
        self.process = subprocess.Popen(shlex.split(cmd),
                                        stdout=subprocess.PIPE)
        await self.handle_output()
