import requests
import json
import logging
logger = logging.getLogger(__name__)

def torIpCheck(proxyurl):
    """
        通过指定tor官方页面检测当前代理的ip情况。        
        检查代理服务是否有效，
        注意这里试用的是requests 的proxy url 方式的字符串。
        例如：  socks5h://mt:password@8.210.5.18:41080
                http://mt:password@8.210.5.18:8080
                https://abc.com
    """
    targetUrl='https://check.torproject.org/api/ip'
    logger.info(f"proxy check {proxyurl}, ".format(proxyurl=proxyurl))
    try:
        response = requests.get(targetUrl,
                                proxies={
                                    "http": proxyurl,
                                    "https": proxyurl,
                                },
                                verify=False)
        logger.debug(f"proxyCheck 响应: {response.content}")
        return response.json()
    
    except Exception as e:
        logger.exception(e)
    return None