
import os
import sys
import time
import subprocess
from subprocess import run, Popen, PIPE
from pathlib import Path
from urllib.parse import urlparse
import shutil
import logging
from mtlibs.process_helper import is_tool
logger = logging.getLogger(__name__)


class Nginx:

    def __init__(self, base_dir):
        self.base_dir = base_dir

    def setup_nginx_django_init_site(self, 
        domain_name="localhost", 
        with_php=True,
        # with_wordpress=False,
        ):
        """
            由于环境不同，可能不能立即获取到证书，所以先启动一个http的 确保django能启动
        """

        logger.info(f"启动主站，绑定域名:{domain_name}")
        cert_dir = f"/etc/letsencrypt/live/{domain_name}"
        if Path("/etc/nginx/conf.d/default.conf").exists():
            shutil.move("/etc/nginx/conf.d/default.conf", "/etc/nginx/conf.d/default.backup")


        nginx_conf_tpl = """
server {
    root @@www_root@@; 
    client_max_body_size 256M;
    index index.html index.htm index.php;
    server_name @@DOMAIN_NAME@@;   

    # 其他页面先尝试相关文件和路径，由前端nextjs兜底
    location / {
        # try_files $uri $uri/ /index.php?$args @backend;
        try_files $uri $uri/ /index.php?$args;
    }            

    location = /favicon.ico { access_log off; log_not_found off; }
    location = /robots.txt  { access_log off; log_not_found off; }
    access_log /var/www/logs/access.log;
    error_log  /var/www/logs/error.log error;
    # 无任何页面时，默认路由，也许这样的方式作为兜底页面，是一个不错的选择
    #error_page 404 /index.php;
    location ^~ /mtxadmin/ {
        add_header X-Powered-By 'PHP';
        # try_files @nextfront $uri $uri/;
        proxy_pass http://backend;
        # autoindex on;
        # index index.html index.htm;
    }
    location ^~ /static/ {
        # 开发板的静态文件
        add_header X-Powered-By 'PHP';
        proxy_pass http://backend;
    }
    location ^~ /api/ {
        add_header X-Powered-By 'PHP';
        proxy_pass http://backend;
    }

    location @backend {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Necessary for Let's Encrypt Domain Name ownership validation. Place any other deny rules after this
    location ~ /.well-known {
        allow all;
    }

    # Deny access to .htaccess or .htpasswd files
    location ~ /\.ht {
        deny all;
    }

    # Deny access to any git repository
    location ~ /\.git {
        deny all;
    }
    @@PHP@@

    listen 80;
    @@LISTEN@@
    @@REDIRECT_HTTPS@@

    
}

"""

        # DOMAIN_NAME = domain_name or os.environ.get("DOMAIN_NAME", "localhost")
        # print(f"DOMAIN_NAME: {DOMAIN_NAME}")
        # cert_dir = self.renew_cert(DOMAIN_NAME)
        # if not cert_dir:
        #     logger.info(f"证书没有成功获取")
        #     return



        nginx_php = ""
        if with_php:
            nginx_php="""
    location ~ \.php$ {
        fastcgi_split_path_info ^(.+\.php)(/.+)$;
        # fastcgi_pass unix:/var/run/php/php8.1-fpm.sock;
        fastcgi_pass 127.0.0.1:9000;
        fastcgi_index index.php;
        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        fastcgi_intercept_errors off;
        fastcgi_buffer_size 16k;
        fastcgi_buffers 4 16k;
        fastcgi_connect_timeout 600;
        fastcgi_send_timeout 600;
        fastcgi_read_timeout 600;
    }
"""     
        nginx_listen = ""

        logger.info(f"尝试找域名证书: {cert_dir}")
        
            
        if domain_name != "localhost" and cert_dir and Path(os.path.join(cert_dir,"fullchain.pem")).exists():
            # 如果设置了绑定域名，使用SSL证书
            nginx_listen=f"""
    listen 443 ssl;
    ssl_certificate {cert_dir}/fullchain.pem;
    ssl_certificate_key {cert_dir}/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
"""     
        else:
            logger.info(f"域名: [{domain_name}]")
            if domain_name != "localhost":
                logger.info(domain_name)
                logger.info("========================")
                try:
                    logger.info(f"尝试获取, letsencrypt 证书，域名:{domain_name}")
                    self.renew_cert(domain_name)
                except Exception as e:
                    logger.info(f"获取letsencrypt证书失败, 域名：{domain_name},详情：")
                    logger.exception(e)
                # 使用临时证书，先确保站点能以https的方式启动。
                temp_cert_dir =os.path.join( os.getcwd(), "certs/localhost")
                nginx_listen=f"""
        listen 443 ssl;
        ssl_certificate {temp_cert_dir}/server.crt;
        ssl_certificate_key {temp_cert_dir}/server.key;
        # include /etc/letsencrypt/options-ssl-nginx.conf;
        # ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
"""     
                logger.info("使用临时证书，先确保站点能以https的方式启动。")
        

        nginx_redirect_https = """if ($scheme = http) {
        return 301 https://$host$request_uri;
    }"""
        logger.info(f"==nginx_redirect_https {nginx_redirect_https}")
        if os.environ.get("GITPOD_WORKSPACE_ID"):
            logger.info(f"在gitpod环境下,无需https跳转")
            nginx_redirect_https = ""

        site_root = os.path.join(self.base_dir, domain_name)
        nginx_conf = nginx_conf_tpl\
            .replace("@@DOMAIN_NAME@@", domain_name)\
            .replace("@@www_root@@", site_root)\
            .replace("@@PHP@@", nginx_php)\
            .replace("@@LISTEN@@", nginx_listen)\
            .replace("@@REDIRECT_HTTPS@@", nginx_redirect_https)

        with open(f"/etc/nginx/sites-enabled/{domain_name}", 'w') as fd:
            fd.write(nginx_conf)

        print(f"nginx.confg配置=============================================")
        print(nginx_conf)
        print("========================================================")
        # 设置目前权限
        if not os.path.exists(site_root):
            Path(site_root).mkdir(mode=0o700, exist_ok=True, parents=True)
        run(f"sudo chown nginx -R {site_root}", shell=True, check=True)
        run(f"nginx -t", shell=True, check=True)


    def setup_nginx(self):
        """根据环境变量和相关参数生产nginx配置文件"""
        nginx_conf_tpl = """user  www-data;
    worker_processes auto;
    error_log  /var/log/nginx/error.log notice;
    pid        /var/run/nginx.pid;
    events {
        worker_connections  1024;
    }
    http {
        include       /etc/nginx/mime.types;
        default_type  application/octet-stream;
        log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                        '$status $body_bytes_sent "$http_referer" '
                        '"$http_user_agent" "$http_x_forwarded_for"';
        access_log  /var/log/nginx/access.log  main;
        sendfile        on;
        #tcp_nopush     on;
        keepalive_timeout  65;

        gzip  on;
        gzip_comp_level 5;

        # gzip.conf
        gzip_min_length 256;
        gzip_proxied any;
        gzip_vary on;    

        include /etc/nginx/conf.d/*.conf;
        include /etc/nginx/sites-enabled/*;

        # upstream front {
        #     # 默认前端
        #     server front:3000 weight=100 max_fails=12 fail_timeout=60s;
        # }

        upstream backend {
            server 127.0.0.1:8000 weight=450 max_fails=12 fail_timeout=60s;
        }

    }
    """

        nginx_conf = nginx_conf_tpl
        with open("/etc/nginx/nginx.conf", 'w') as fd:
            fd.write(nginx_conf)

        logger.info(f"初始化相关目录")
        os.makedirs("/var/www/logs", exist_ok=True)
        # os.path.exists(
        #     "/etc/nginx/conf.d") and shutil.rmtree("/etc/nginx/conf.d")
        Path("/etc/nginx/conf.d/").mkdir(exist_ok=True)
        Path("/etc/nginx/sites-enabled/").mkdir(exist_ok=True)


    def renew_cert(self, domain, exist_ok=True) -> bool:
        """重新获取ssl证书"""
        cert_dir = f"/etc/letsencrypt/live/{domain}"
        if exist_ok and os.path.exists(cert_dir):
            logger.info(f"ssl证书`{domain}`已经存在，跳过获取")
            return cert_dir

        else:
            if not is_tool('certbot'):
                run(f"sudo apt install -y certbot python3-certbot-nginx",
                    shell=True, check=True)
            # 使用nginx插件的形式获取证书，这个问题在于，需要nginx首先配置成为http的方式（即没有使用https的情况下）才行，考虑到容器经常重置的问题，这个方式不妥。
            # run(f"sudo certbot certonly --non-interactive --agree-tos --nginx -d {domain} -m a@a.com", shell=True, check=True)
            # 现在使用 certbot 独立的方式获取证书。获取证书后，直接手动配置nginx配置文件启动。
            certbot_email = os.environ.get("CERTBOT_EMAIL", "b@b.com")

            while True:
                try:
                    run(f"certbot certonly --non-interactive --agree-tos --standalone -d {domain} -m {certbot_email}",
                        shell=True,
                        check=True)
                    break
                except Exception as e:
                    logger.info(f"获取ssl证书出错, 60s 后重试, 错误消息:{str(e)}")
                    # logger.exception(msg)
                    time.sleep(60)

            # 确实证书文件存在
            if os.path.exists(cert_dir):
                return cert_dir

        logger.info(f"证书文件视乎不存在，请注意查找原因")
        return None

    def restart(self):
        """重启"""
        logger.info(f"重启nginx服务")
        run("sudo service nginx restart", shell=True)

    def new_site(self, domain_name):
        """添加新的站点配置"""
        nginx_conf_tpl = """server {
    if ($host = @@DOMAIN_NAME@@) {
        return 301 https://$host$request_uri;
    } # managed by Certbot


    server_name @@DOMAIN_NAME@@;
    listen 80;
    return 404; # managed by Certbot
}

server {
    root @@www_root@@; 
    client_max_body_size 256M;
    index index.html index.htm index.php;
    server_name @@DOMAIN_NAME@@;
    # location / {
    #     # First attempt to serve request as file, then
    #     # as directory, then fall back to displaying a 404.
    #     try_files $uri $uri/ /index.php?$query_string;
    # }

    # location / {
    #     # autoindex on;
    #     index index.html index.htm index.php;
    #     try_files $uri $uri/ /index.php?$args @front @backend;
    # }

    # 明确指定默认首页
    # location = / {
    #     proxy_pass http://front;
    #     proxy_http_version 1.1;
    #     proxy_set_header Upgrade $http_upgrade;
    #     proxy_set_header Connection 'upgrade';
    #     proxy_set_header Host $host;
    #     proxy_cache_bypass $http_upgrade;
    # }

    # 其他页面先尝试相关文件和路径，由前端nextjs兜底
    location / {
        try_files $uri $uri/ /index.php?$args @backend;
    }            

    location = /favicon.ico { access_log off; log_not_found off; }
    location = /robots.txt  { access_log off; log_not_found off; }
    access_log /var/www/logs/access.log;
    error_log  /var/www/logs/error.log error;
    # 无任何页面时，默认路由，也许这样的方式作为兜底页面，是一个不错的选择
    # error_page 404 /index.php;

    location ~ \.php$ {
        fastcgi_split_path_info ^(.+\.php)(/.+)$;
        # fastcgi_pass unix:/var/run/php/php8.1-fpm.sock;
        fastcgi_pass 127.0.0.1:9000;
        fastcgi_index index.php;
        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
        fastcgi_intercept_errors off;
        fastcgi_buffer_size 16k;
        fastcgi_buffers 4 16k;
        fastcgi_connect_timeout 600;
        fastcgi_send_timeout 600;
        fastcgi_read_timeout 600;
    }

    location ^~ /mtxadmin/ {
        add_header X-Powered-By 'PHP';
        # try_files @nextfront $uri $uri/;
        proxy_pass http://backend;
        # autoindex on;
        # index index.html index.htm;
    }
    location ^~ /static/ {
        # 开发板的静态文件
        add_header X-Powered-By 'PHP';
        proxy_pass http://backend;
    }
    location ^~ /api/ {
        add_header X-Powered-By 'PHP';
        proxy_pass http://backend;
    }

    location @backend {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # location @front {
    #     # reverse proxy for next server
    #     proxy_pass http://front;
    #     proxy_http_version 1.1;
    #     proxy_set_header Upgrade $http_upgrade;
    #     proxy_set_header Connection 'upgrade';
    #     proxy_set_header Host $host;
    #     proxy_cache_bypass $http_upgrade;
    # }

    # Necessary for Let's Encrypt Domain Name ownership validation. Place any other deny rules after this
    location ~ /.well-known {
        allow all;
    }

    # Deny access to .htaccess or .htpasswd files
    location ~ /\.ht {
        deny all;
    }

    # Deny access to any git repository
    location ~ /\.git {
        deny all;
    }

    # Deny access to xmlrpc.php - a common brute force target against Wordpress
    location = /xmlrpc.php {
        deny all;
        access_log off;
        log_not_found off;
        return 444;
    }

    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/@@DOMAIN_NAME@@/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/@@DOMAIN_NAME@@/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
}"""

        DOMAIN_NAME = domain_name or os.environ.get("DOMAIN_NAME", "localhost")

        cert_dir = self.renew_cert(DOMAIN_NAME)
        if not cert_dir:
            logger.info(f"证书没有成功获取")
            return

        site_root = os.path.join(self.base_dir, DOMAIN_NAME)
        nginx_conf = nginx_conf_tpl\
            .replace("@@DOMAIN_NAME@@", DOMAIN_NAME)\
            .replace("@@www_root@@", site_root)

        
        with open(f"/etc/nginx/sites-enabled/{DOMAIN_NAME}", 'w') as fd:
            fd.write(nginx_conf)

        # print(f"nginx.confg配置=============================================")
        # print(nginx_conf)
        # print("========================================================")
        # 设置目前权限
        if not os.path.exists(site_root):
            Path(site_root).mkdir(mode=0o700, exist_ok=True, parents=True)
        run(f"sudo chown nginx -R {site_root}", shell=True, check=True)


    def forward(self, domain_name, target_url):
        """
            建立纯转发(反向代理)站点。
        """
        # target_uri = urlparse(target_url)
        nginx_conf_tpl = """
#转https
server {
    if ($host = @@DOMAIN_NAME@@) {
        return 301 https://$host$request_uri;
    } # managed by Certbot
    server_name @@DOMAIN_NAME@@;
    listen 80;
    return 404; # managed by Certbot
}
server {
    root @@www_root@@; 
    client_max_body_size 256M;
    server_name @@DOMAIN_NAME@@;
    location / {
        proxy_pass @@PROXY_PASS@@;
        # proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header   X-Real-IP        $remote_addr;
        proxy_set_header   X-Forwarded-For  $proxy_add_x_forwarded_for;
        # 让scheme的值传递给后方，要不然，虽然页面时https，但是后端依然认为是http，导致可能的网址错误。
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/@@DOMAIN_NAME@@/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/@@DOMAIN_NAME@@/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
}"""
        cert_dir = self.renew_cert(domain_name)
        if not cert_dir:
            logger.info(f"证书没有成功获取")
            return

        nginx_conf = nginx_conf_tpl\
            .replace("@@DOMAIN_NAME@@", domain_name)\
            .replace("@@PROXY_PASS@@", target_url)
            # .replace("@@www_root@@", site_root)\

        with open(f"/etc/nginx/sites-enabled/{domain_name}", 'w') as fd:
            fd.write(nginx_conf)

