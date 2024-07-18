import os

APP_ROOT = os.path.join(os.path.dirname(__file__))

# 默认配置，可被环境变量覆盖。
config_data = {
    "APP_ROOT":
    APP_ROOT,
    "LOGS_ROOT":
    os.path.join(APP_ROOT, 'logs'),
    "DATA_ROOT":
    os.path.join(APP_ROOT, 'data'),
    "ROOT_PASSWORD":
    "www.gmail123456.com",
    "GHHOOK_TOKEN":
    'token1234567890',
    'GHTOKEN':
    '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',
    'ONIONKEY':
    'PT0gZWQyNTUxOXYxLXNlY3JldDogdHlwZTAgPT0AAABIhW8C1hUv92DkipPFSjAdxKU6oTHmYsRx7r0rZlGIYvwxQE5vwuDb2ZaGY9gZcuWTA6ZgInQvBxgZZPYKZyKr',
    'ID_ED25519':
    """-----BEGIN OPENSSH PRIVATE KEY-----
                b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtzc2gtZW
                QyNTUxOQAAACABjDQF9yT/3VpsrYW2AGd7Fn50+qUzBOnOvkkeWZuRMQAAAJDG1qKlxtai
                pQAAAAtzc2gtZWQyNTUxOQAAACABjDQF9yT/3VpsrYW2AGd7Fn50+qUzBOnOvkkeWZuRMQ
                AAAEB23P1AcFLmqQv3Bus0dIdlg0AG4WQKh3v0oxiRJpee7QGMNAX3JP/dWmythbYAZ3sW
                fnT6pTME6c6+SR5Zm5ExAAAACWthbGlAa2FsaQECAwQ=
                -----END OPENSSH PRIVATE KEY-----
""",
}

config_data.update(os.environ)


def get(name):
    return config_data.get(name)
