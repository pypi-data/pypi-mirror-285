
import socket
from rich.progress import Progress
import ipaddress
import random
from urllib.parse import urljoin, urlparse
import faker
from requests.packages.urllib3.util.ssl_ import create_urllib3_context
from requests_cache import CachedSession
from requests.adapters import HTTPAdapter
from concurrent import futures
from concurrent.futures import ThreadPoolExecutor
import os
import functools
import http.client as http_client
import json
import logging
import requests
import tldextract
import urllib3

from .strutil import *

import ssl
from socket import gethostbyname
from urllib.parse import urlparse
import requests
import urllib3
from requests.utils import to_native_string

def get_redirect_target(self, resp):
    """hook requests.Session.get_redirect_target method"""
    if resp.is_redirect:
        location = resp.headers['location']
        location = location.encode('latin1')
        encoding = resp.encoding if resp.encoding else 'utf-8'
        return to_native_string(location, encoding)
    return None


def patch_redirect():
    requests.Session.get_redirect_target = get_redirect_target


def remove_ssl_verify():
    ssl._create_default_https_context = ssl._create_unverified_context


def patch_getproxies():
    # 高版本python已经修复了这个问题
    # https://bugs.python.org/issue42627
    # https://www.cnblogs.com/davyyy/p/14388623.html
    if os.name == 'nt':
        import urllib.request
        old_getproxies_registry = urllib.request.getproxies_registry
        def hook():
            proxies = old_getproxies_registry()
            if 'https' in proxies:
                proxies['https'] = proxies['https'].replace('https://', 'http://')
            return proxies
        urllib.request.getproxies_registry = hook


urllib3.disable_warnings()
remove_ssl_verify()
patch_redirect()
patch_getproxies()


class RequestsSession(requests.Session):
    """
    在请求之前修改或添加请求头信息
    Referer、Origin 还要判session有没有赋值
    """

    def prepare_request(self, request, *args, **kwargs):
        parsed_url = urlparse(request.url)
        if 'Referer' not in request.headers and 'Referer' not in self.headers:
            request.headers['Referer'] = f"{parsed_url.scheme}://{parsed_url.netloc}/"
        if 'Origin' not in request.headers and 'Origin' not in self.headers:
            request.headers['Origin'] = f"{parsed_url.scheme}://{parsed_url.netloc}"

        return super(RequestsSession, self).prepare_request(request, *args, **kwargs)

class BaseUrlSession(RequestsSession):
    """A Session with a URL that all requests will use as a base.
    .. note::
        The base URL that you provide and the path you provide are **very**
        important.
    Let's look at another *similar* example
    .. code-block:: python
        >>> from requests_toolbelt import sessions
        >>> s = sessions.BaseUrlSession(
        ...     base_url='https://example.com/resource/')
        >>> r = s.get('/sub-resource/', params={'foo': 'bar'})
        >>> print(r.request.url)
        https://example.com/sub-resource/?foo=bar
    The key difference here is that we called ``get`` with ``/sub-resource/``,
    i.e., there was a leading ``/``. This changes how we create the URL
    because we rely on :mod:`urllib.parse.urljoin`.
    To override how we generate the URL, sub-class this method and override the
    ``create_url`` method.
    Based on implementation from
    https://github.com/kennethreitz/requests/issues/2554#issuecomment-109341010

    作者一直没在requests上加这个功能, urljoin容易有缺陷
    https://stackoverflow.com/questions/42601812/python-requests-url-base-in-session
    """

    base_url = None

    def __init__(self, base_url=None):
        if base_url:
            self.base_url = base_url
        super(BaseUrlSession, self).__init__()

    def request(self, method, url, *args, **kwargs):
        """Send the request after generating the complete URL."""
        url = self.create_url(url)
        return super(BaseUrlSession, self).request(
            method, url, *args, **kwargs
        )

    def prepare_request(self, request, *args, **kwargs):
        """Prepare the request after generating the complete URL."""
        request.url = self.create_url(request.url)
        return super(BaseUrlSession, self).prepare_request(
            request, *args, **kwargs
        )

    def create_url(self, url):
        """Create the URL based off this partial path."""
        return urljoin(self.base_url.rstrip("/") + "/", url.lstrip("/"))




class CustomSslContextHttpAdapter(HTTPAdapter):
    # https://github.com/urllib3/urllib3/issues/2653
    # openssl 3.0 bug --> (Caused by SSLError(SSLError(1, '[SSL: UNSAFE_LEGACY_RENEGOTIATION_DISABLED] unsafe legacy renegotiation disabled (_ssl.c:1006)')))
    """"Transport adapter" that allows us to use a custom ssl context object with the requests."""

    def init_poolmanager(self, connections, maxsize, block=False):
        ctx = create_urllib3_context()
        ctx.load_default_certs()
        ctx.check_hostname = False # ValueError: Cannot set verify_mode to CERT_NONE when check_hostname is enabled
        ctx.options |= 0x4  # ssl.OP_LEGACY_SERVER_CONNECT
        self.poolmanager = urllib3.PoolManager(ssl_context=ctx)



def requests_session(proxies=False, max_retries=1, timeout=None, debug=False, base_url=None, user_agent=None, use_cache=None):
    """
    返回一个requests创建的session, 添加伪造的ua, 初始化请求头
    @return:
    """
    if use_cache:
        if use_cache == True:
            session = CachedSession()
        else:
            session = CachedSession(**use_cache)
    elif base_url:
        session = BaseUrlSession(base_url)
    else:
        session = RequestsSession()

    fake = faker.Faker('zh_CN')
    session.headers.update({
        'Upgrade-Insecure-Requests': '1',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache',
        'User-Agent': user_agent or fake.chrome(),
        'X-Forwarded-For': fake.ipv4(),
    })
    session.verify = False
    session.mount('http://', HTTPAdapter(max_retries=max_retries))
    session.mount('https://', CustomSslContextHttpAdapter(max_retries=max_retries))

    if timeout is not None:
        session.request = functools.partial(session.request, timeout=timeout)

    if proxies:
        if isinstance(proxies, dict):
            session.proxies = proxies
        elif isinstance(proxies, int):
            session.proxies = {"http": "http://127.0.0.1:" + str(proxies), "https": "http://127.0.0.1:" + str(proxies)}
        else:
            proxies = {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}
            session.proxies = proxies

    if debug:
        http_client.HTTPConnection.debuglevel = 1
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True

    return session


ORIGIN_CIPHERS = 'ECDH+AESGCM:DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:ECDH+HIGH:DH+HIGH:ECDH+3DES:DH+3DES:RSA+AESGCM:RSA+AES:RSA+HIGH:RSA+3DES'


class DESAdapter(HTTPAdapter):
    """
    https://blog.csdn.net/god_zzZ/article/details/123010576
    反爬虫检测TLS指纹
    https://ja3er.com/json
    """

    def __init__(self, *args, **kwargs):
        # 在请求中重新启用 3DES 支持的 TransportAdapter
        CIPHERS = ORIGIN_CIPHERS.split(":")
        random.shuffle(CIPHERS)
        # print("1:", CIPHERS)
        CIPHERS = ":".join(CIPHERS)
        # print("2:", CIPHERS)
        self.COPHERS = CIPHERS + ":!aNULL:!eNULL:!MD5"
        super(DESAdapter, self).__init__(*args, **kwargs)

    # 在一般情况下，当我们实现一个子类的时候，__init__的第一行应该是super().__init__(*args, **kwargs)，
    # 但是由于init_poolmanager和proxy_manager_for是复写了父类的两个方法，
    # 这两个方法是在执行super().__init__(*args, **kwargs)的时候就执行的。
    # 所以，我们随机设置 Cipher Suits 的时候，需要放在super().__init__(*args, **kwargs)的前面。
    def init_poolmanager(self, *args, **kwargs):
        context = create_urllib3_context(ciphers=self.COPHERS)
        kwargs["ssl_context"] = context
        return super(DESAdapter, self).init_poolmanager(*args, **kwargs)

    def proxy_manager_for(self, *args, **kwargs):
        context = create_urllib3_context(ciphers=self.COPHERS)
        kwargs["ssl_context"] = context



def httpraw(raw: str, ssl: bool = False, **kwargs):
    """
    代码来源Pocsuite, 修复postData只发送一行的bug
    发送原始HTTP封包请求,如果你在参数中设置了例如headers参数，将会发送你设置的参数
    请求头需要用: 补上空格隔开

    :param raw:原始封包文本
    :param ssl:是否是HTTPS
    :param kwargs:支持对requests中的参数进行设置
    :return:requests.Response
    """
    raw = raw.strip()
    # Clear up unnecessary spaces
    raws = list(map(lambda x: x.strip(), raw.splitlines()))
    try:
        method, path, protocol = raws[0].split(" ")
    except Exception:
        raise Exception("Protocol format error")
    post = None
    _json = None
    if method.upper() == "POST":
        index = 0
        for i in raws:
            index += 1
            if i.strip() == "":
                break
        if len(raws) == index:
            raise Exception
        tmp_headers = raws[1:index - 1]
        tmp_headers = extract_dict('\n'.join(tmp_headers), '\n', ": ")
        postData = '\r\n'.join(raws[index:])
        try:
            json.loads(postData)
            _json = postData
        except ValueError:
            post = postData
    else:
        tmp_headers = extract_dict('\n'.join(raws[1:]), '\n', ": ")
    netloc = "http" if not ssl else "https"
    host = tmp_headers.get("Host", None)
    if host is None:
        raise Exception("Host is None")
    del tmp_headers["Host"]
    if 'Content-Length' in tmp_headers:
        del tmp_headers['Content-Length']
    url = "{0}://{1}".format(netloc, host + path)

    kwargs.setdefault('allow_redirects', True)
    kwargs.setdefault('data', post)
    kwargs.setdefault('headers', tmp_headers)
    kwargs.setdefault('json', _json)

    with requests_session() as session:
        return session.request(method=method, url=url, **kwargs)


requests.httpraw = httpraw




def is_private_ip(ip):
    """
    判断IP地址是否是内网IP，如果传入的不是有效IP则也会返回False
    """
    try:
        ip_obj = ipaddress.ip_address(ip)
        return ip_obj.is_private
    except ValueError:
        return False


def is_internal_url(url):
    """
    判断URL是否是内网IP对应的URL
    """
    # 提取URL中的IP地址
    parsed_url = urlparse(url)
    netloc = parsed_url.netloc.split(':')[0]
    ip = netloc if netloc else parsed_url.hostname
    # 判断IP地址是否是内网IP
    return is_private_ip(ip)


def is_wildcard_dns(domain):
    """
    传入主域名
    判断域名是否有泛解析
    """
    import dns
    nonexistent_domain = rand_base(8) + '.' + domain
    try:
        answers = dns.resolver.resolve(nonexistent_domain, 'A')
        ip_list = [j for i in answers.response.answer for j in i.items]
        return True
    except Exception as e:
        return False


def is_valid_ip(ip: str) -> bool:
    """
    判断是否是有效的IP地址，支持IPv4Address、IPv6Address
    """
    try:
        ip_address = ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def is_wildcard_dns_batch(domain_list: iter, thread_num: int = 10, show_progress: bool = True) -> dict:
    """
    多线程批量判断域名是否泛解析
    传入域名或者URL列表、，支持解析成主域名
    """
    result = {}
    with ThreadPoolExecutor(max_workers=thread_num) as executor:

        future_map = {}
        for domain in domain_list:
            if domain.startswith(('http://', 'https://')):
                domain = urlparse(domain).hostname

            if is_valid_ip(domain):
                result[domain] = False
            else:
                main_domain = get_maindomain(domain)
                if main_domain not in result:
                    result[main_domain] = False
                    future_map[executor.submit(is_wildcard_dns, main_domain)] = main_domain

        if show_progress:
            with Progress() as progress:
                task_id = progress.add_task("[red]is_wildcard_dns_batch", total=len(future_map))
                for future in futures.as_completed(future_map):
                    result[future_map[future]] = future.result()
                    progress.update(task_id, advance=1)
        else:
            for future in futures.as_completed(future_map):
                result[future_map[future]] = future.result()

    return result



def get_maindomain(subdomain):
    # get the main domain from subdomain
    tld = tldextract.extract(subdomain)
    if tld.suffix != '':
        domain = f'{tld.domain}.{tld.suffix}'
    else:
        domain = tld.domain
    return domain



def url2ip(url, with_port=False):
    """
    works like turning 'http://baidu.com' => '180.149.132.47'
    """

    url_prased = urlparse(url)
    if url_prased.port:
        ret = gethostbyname(url_prased.hostname), url_prased.port
    elif not url_prased.port and url_prased.scheme == 'https':
        ret = gethostbyname(url_prased.hostname), 443
    else:
        ret = gethostbyname(url_prased.hostname), 80

    return ret if with_port else ret[0]


def is_port_in_use(port: int) -> bool:
    """Check if a port is already in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0