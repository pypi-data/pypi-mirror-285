#!/usr/bin/env python3
import os
import subprocess
from pathlib import Path
import subprocess
import logging
from mtxp import settings
from mtlibs import process_helper
from mtlibs import mtutils
import shutil
logger = logging.getLogger(__name__)

class NginxService():
    def __init__(self):
        self.html_root = settings.getHtmlRoot()
        logger.info(f"html root {self.html_root}")
        self.smapiRoot = "/mtxp"

    def start(self):
        logger.info("启动nginx 进程")
        
        if Path("/etc/nginx/conf.d/default.conf").exists():
            os.remove("/etc/nginx/conf.d/default.conf")
        port = 80
        check_port = mtutils.get_tcp_open_port(80)
        if not check_port:
            logger.info(f"tcp port opend {port},skip start nginx")
        else:
            setup_nginx(
                smApiPrefix=self.smapiRoot,
                htmlRoot=self.html_root,
                port=port,
                server_name="127.0.0.1"
            )

    def stop(self):
        pass


def setup_nginx(
    smApiPrefix: str,
    htmlRoot: str="/var/www/html",
    port: int = 80,
    server_name:str="127.0.0.1"
):
    nginx_conf = """user nginx;
worker_processes auto;

error_log /var/log/nginx/error.log notice;
pid /var/run/nginx.pid;

events {
  worker_connections 1024;
}

http {
  upstream mtxtun {
    server 127.0.0.1:3000 weight=99 max_fails=12 fail_timeout=60s;
  }
  upstream smirror {
    server 127.0.0.1:3456 weight=100 max_fails=12 fail_timeout=60s;
  }
  upstream mtx {
    server 127.0.0.1:8000 weight=200 max_fails=12 fail_timeout=60s;
  }
  upstream mtxp {
    server 127.0.0.1:5000 weight=300 max_fails=12 fail_timeout=60s;
  }
  upstream default_backend {
    server 127.0.0.1:3000 weight=450 max_fails=12 fail_timeout=60s;
  }

  include /etc/nginx/mime.types;
  default_type application/octet-stream;

  log_format main '$remote_addr - $remote_user [$time_local] "$request" '
  '$status $body_bytes_sent "$http_referer" '
  '"$http_user_agent" "$http_x_forwarded_for"';

  access_log /var/log/nginx/access.log main;

  sendfile on;
  #tcp_nopush     on;
  keepalive_timeout 65;
  gzip on;
  types_hash_max_size 2048;
  include /etc/nginx/conf.d/*.conf;
}
"""
    # print("nginx 配置信息", nginx_conf)
    nginx_default_site = """


server {
  listen @@PORT@@;
  server_name @@SERVER_NAME@@;
  #access_log  /var/log/nginx/host.access.log  main;
  # location / {
  #   root /app/static;
  #   index index.html index.htm;
  # }
  index index.php;
  # access_log /etc/nginx/conf.d/log/access.log;
  # error_log /etc/nginx/conf.d/log/error.log;
  # location / {
  #   add_header X-Powered-By 'PHP';
  #   root /var/www/html;
  #   index index.php index.html index.htm;
  #   # try_files @sm $uri $uri/;
  #   # try_files $uri /index.php?$args $uri/index.html $uri.html @default_backend;
  #   try_files $uri $uri/index.html $uri.html @default_backend;

  #   # # proxy_pass http://default_backend;
  #   # # autoindex on;
  #   # proxy_http_version 1.1;
  #   # index index.html index.htm;
  #   # proxy_set_header Upgrade $http_upgrade;
  #   # proxy_set_header Connection "Upgrade";
  #   # proxy_set_header Host $host;
  #   # proxy_set_header Host $host;
  #   # proxy_set_header X-Real-IP $remote_addr;
  #   # proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  # }
  root @@STATIC_DIR@@;
  location / {
    autoindex on;
    index index.php index.html index.htm;
    try_files $uri $uri/ /index.php?$args @mtx default_backend;
    # try_files $uri $uri/ /index.php?$args;
    # proxy_pass http://mtx;
  }

  location ^~ /smirror {
    add_header X-Powered-By 'PHP';
    # root /app/static;
    # try_files @nextfront $uri $uri/;
    proxy_pass http://smirror;
    # autoindex on;
    # index index.html index.htm;
  }

  location ^~ /mtxcms/ {
    add_header X-Powered-By 'PHP';
    # try_files @nextfront $uri $uri/;
    proxy_pass http://default_backend;
  }


  location ^~ @@SM_API@@/ {
    add_header X-Powered-By 'PHP';
    # root /app/static;
    # try_files @nextfront $uri $uri/;
    proxy_pass http://mtxp;
    # autoindex on;
    # index index.html index.htm;
  }

  location ^~ /admin/ {
    add_header X-Powered-By 'PHP';
    # try_files @nextfront $uri $uri/;
    proxy_pass http://mtx;
    # autoindex on;
    # index index.html index.htm;
  }

  error_page 500 502 503 504 /50x.html;
  location = /50x.html {
    root /usr/share/nginx/html;
  }

  location /baidu {
    try_files /baidu.html
    $uri $uri/index.html $uri.html
    @fallback1;
  }
  #跳转到百度页面
  location @fallback {
    # rewrite ^/(.*)$ http://www.baidu.com;
    proxy_pass http://smirror;
  }

  location @default_backend {
    proxy_pass http://default_backend;
  }
  location @mtx {
    proxy_pass http://mtx;
  }


  # deny access to .htaccess files, if Apache's document root
  # concurs with nginx's one
  location ~ /\.ht {
    deny all;
  }
  # proxy the PHP scripts to Apache listening on 127.0.0.1:80
  #
  #location ~ \.php$ {
  #    proxy_pass   http://127.0.0.1;
  #}

  # pass the PHP scripts to FastCGI server listening on 127.0.0.1:9000
  #
  location ~ \.php$ {
    # root /var/www/html;
    # try_files $uri =404;
    fastcgi_pass 127.0.0.1:9000;
    # fastcgi_pass /run/php/php7.4-fpm.sock;
    # 设置nginx的默认首页文件(上面已经设置过了，可以删除)
    fastcgi_index index.php;
    fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
    include fastcgi_params;
  }
  location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires max;
    log_not_found off;
  }
  # #ignored: “-” thing used or unknown variable in regex/rew
  # rewrite ^/([_0-9a-zA-Z-]+/)?wp-admin$ /$1wp-admin/ permanent;

  # if (-f $request_filename) {
  #   set $rule_2 1;
  # }
  # if (-d $request_filename) {
  #   set $rule_2 1;
  # }
  # if ($rule_2 = "1") {
  #   #ignored: “-” thing used or unknown variable in regex/rew
  # }
  # rewrite ^/([_0-9a-zA-Z-]+/)?(wp-(content|admin|includes).*) /$2 last;
  # rewrite ^/([_0-9a-zA-Z-]+/)?(.*.php)$ /$2 last;
  # rewrite /. /index.php last;

  # deny access to .htaccess files, if Apache's document root
  # concurs with nginx's one
  #
  location ~ /\.ht {
    deny all;
  }
  location ~* \.(xml|yaml|cmd|cfg|yml|tmp|sh|bat|txt|ts|tsx|jsx|lock)$ {
    # 禁用某些后缀名文件访问。
    deny all;
  }
  location ~ (README\.md|ockerfile.*|package.*\.json|.*config.js|.*prisma.*)$ {
    deny all;
  }
  location ^~ /(configs|build|log|logs)/ {
    #禁用某些目录访问
    deny all;
  }
  location ^~ /. {
    # 禁止以.开始的文件访问
    # 匹配任何以 /. 开头的地址，匹配符合以后，停止往下搜索正则，采用这一条。
    deny all;
  }
  location = /some2.html {
    rewrite ^/some2.html$ /test/2.html break;
  }
}


"""
    with open("/etc/nginx/nginx.conf", "w") as f:
        f.write(nginx_conf)

    if not Path(htmlRoot).exists():
        Path(htmlRoot).mkdir(parents=True, mode=0o777, exist_ok=True)

    with open("/etc/nginx/conf.d/default.conf", "w") as f:
        f.write(nginx_default_site\
                            .replace("@@PORT@@", str(port))\
                            .replace("@@SERVER_NAME@@", server_name)\
                            .replace("@@STATIC_DIR@@", htmlRoot)\
                            .replace("@@SM_API@@", smApiPrefix))

    cp: subprocess.CompletedProcess = process_helper.exec("nginx -t")
    if cp.returncode != 0:
        print("nginx 配置信息不正确")
        print(cp.stderr + cp.stdout)
        return
    nginx_cp = process_helper.exec("nginx -s reload", check=False)
    nginx_cp = process_helper.exec("nginx", check=False)
    if nginx_cp.returncode == 0:
        print("nginx 成功启动")
