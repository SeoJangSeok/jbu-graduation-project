import re
import socket
from datetime import datetime, timedelta
from urllib.parse import urlparse

import pandas as pd
import requests
import tld
import whois
from bs4 import BeautifulSoup
from tld import get_tld

# URL 단축 서비스 도메인 목록
SHORTENER_DOMAINS = [
    "bit.ly",
    "kl.am",
    "cli.gs",
    "bc.vc",
    "po.st",
    "v.gd",
    "bkite.com",
    "shorl.com",
    "scrnch.me",
    "to.ly",
    "adf.ly",
    "x.co",
    "1url.com",
    "ad.vu",
    "migre.me",
    "su.pr",
    "smallurl.co",
    "cutt.us",
    "filoops.info",
    "shor7.com",
    "yfrog.com",
    "tinyurl.com",
    "u.to",
    "ow.ly",
    "ff.im",
    "rubyurl.com",
    "r2me.com",
    "post.ly",
    "twitthis.com",
    "buzurl.com",
    "cur.lv",
    "tr.im",
    "bl.lnk",
    "tiny.cc",
    "lnkd.in",
    "q.gs",
    "is.gd",
    "hurl.ws",
    "om.ly",
    "prettylinkpro.com",
    "qr.net",
    "qr.ae",
    "snipurl.com",
    "ity.im",
    "t.co",
    "db.tt",
    "link.zip.net",
    "doiop.com",
    "url4.eu",
    "poprl.com",
    "tweez.me",
    "short.ie",
    "me2.do",
    "bit.do",
    "shorte.st",
    "go2l.ink",
    "yourls.org",
    "wp.me",
    "goo.gl",
    "j.mp",
    "twurl.nl",
    "snipr.com",
    "shortto.com",
    "vzturl.com",
    "u.bb",
    "shorturl.at",
    "han.gl",
    "wo.gl",
    "wa.gl",
]


# 1. URL에 IP 주소가 포함되어 있는지 확인
def having_ip_address(url):
    ipv4_pattern = re.compile(r"^https?://(\d{1,3}\.){3}\d{1,3}(:\d+)?(/|$)")

    hex_ipv4_pattern = re.compile(
        r"^https?://0x([0-9a-fA-F]{1,2})\."
        r"(0x[0-9a-fA-F]{1,2})\."
        r"(0x[0-9a-fA-F]{1,2})\."
        r"(0x[0-9a-fA-F]{1,2})(:\d+)?(/|$)"
    )

    ipv6_pattern = re.compile(r"^https?://([0-9a-fA-f:]+)(:\d+)?(/|$)")

    if (
        ipv4_pattern.match(url)
        or hex_ipv4_pattern.match(url)
        or ipv6_pattern.match(url)
    ):
        return -1

    return 1


# 2. URL 길이
def url_length(url):
    if len(url) < 54:
        return 1
    elif len(url) <= 75:
        return 0
    else:
        return -1


# 3. URL 단축 서비스 사용 여부
def shortening_service(url):
    domain = urlparse(url).netloc

    if domain in SHORTENER_DOMAINS:
        return -1

    return 1


# 4. '@' 기호 포함 여부
def having_at_symbol(url):
    if "@" in url or "%40" in url:
        return -1

    return 1


# 5. '//'를 이용한 리다이렉션 여부
def double_slash_redirecting(url):
    if "//" in url[7:]:
        return -1

    return 1


# 6. 도메인 또는 서브도메인에 '-' 포함 여부
def prefix_suffix(url):
    if having_ip_address(url) == -1:
        return 0

    try:
        domain = get_tld(url, as_object=True)

        if "-" in domain.domain:
            return -1
        elif "-" in domain.subdomain:
            return -1

        return 1

    except tld.exceptions.TldDomainNotFound:
        return -1


# 7. 서브도메인 사용 여부
def having_sub_domain(url):
    if having_ip_address(url) == -1:
        return 0

    # www. 제거
    if "www." in url[:12]:
        url = url.replace("www.", "")

    try:
        domain = get_tld(url, as_object=True)

        # 서브도메인이 없는 경우
        if domain.subdomain == "":
            return 1

        dot_count = domain.subdomain.count(".")

        # 서브도메인이 1개인 경우
        if dot_count == 0:
            return 0

        return -1

    except tld.exceptions.TldDomainNotFound:
        return -1


# 도메인 등록 기간 계산을 위한 보조 함수
def get_total_date(url):
    domain = whois.whois(url)

    expiration_date = domain.expiration_date

    if isinstance(expiration_date, list):
        expiration_date = expiration_date[0]

    updated_date = domain.updated_date

    if isinstance(updated_date, list):
        updated_date = updated_date[0]

    if expiration_date is None or updated_date is None:
        return None

    total_date = (expiration_date - updated_date).days

    return total_date


# 8. 도메인 등록 기간
def domain_registration_length(url):
    try:
        total_date = get_total_date(url)

        if total_date is None:
            return 0

        if total_date <= 365:
            return -1

        return 1

    except whois.parser.PywhoisError:
        return -1

    except Exception:
        return 0


# 9. Favicon
def favicon(url):
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        favicon_tags = soup.find_all(
            "link", rel=lambda value: value and "icon" in value.lower()
        )

        if not favicon_tags:
            return 1

        for tag in favicon_tags:
            href = tag.get("href")

            if href:
                favicon_domain = urlparse(href).netloc

                if favicon_domain == "":
                    return 1

                return -1

        return 1

    except Exception:
        return -1


# URL에서 http / https 제거
def remove_schemes(url):
    if "http://" in url:
        return url.replace("http://", "")

    elif "https://" in url:
        return url.replace("https://", "")

    return url


# 10. 비표준 포트 사용 여부
def port(url):
    domain = remove_schemes(url)

    try:
        ip = socket.gethostbyname(domain)

    except Exception:
        return -1

    socket.setdefaulttimeout(2)

    ports = [80, 21, 22, 23, 445, 1433, 1521, 3306, 3389]

    for port_number in ports:
        sock = socket.socket()

        if port_number == 80:
            try:
                sock.connect((ip, port_number))
                sock.close()

            except Exception:
                return -1

        else:
            try:
                sock.connect((ip, port_number))
                sock.close()

                return -1

            except Exception:
                pass

    return 1


# 11. 도메인 이름에 https 문자열 포함 여부
def https_token(url):
    try:
        domain = url.split("/")[2]

    except IndexError:
        return 1

    if "https" in domain:
        return -1

    return 1


# 12. 도메인 수명
def age_of_domain(url):
    try:
        domain_info = whois.whois(url)

        expiration_date = domain_info.expiration_date

        if isinstance(expiration_date, list):
            expiration_date = expiration_date[0]

        current_date = datetime.now()

        remain_date = expiration_date - current_date

        if remain_date >= timedelta(days=182):
            return 1

        return -1

    except Exception:
        return 0


# 13. DNS 기록 확인
def dns_record(url):
    try:
        whois.whois(url)

    except Exception:
        return -1

    return 1


# 14. 리다이렉션 횟수 확인
def count_redirection(url):
    try:
        count = 0

        response = requests.head(url, allow_redirects=True, timeout=5)

        for history in response.history:
            if history.status_code in [301, 302]:
                count += 1

        if count <= 1:
            return 1

        elif count < 4:
            return 0

        return -1

    except Exception:
        return 0


# 15. 우클릭 방지 여부
def disabling_right_click(url):
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/58.0.3029.110 Safari/537.3"
            )
        }

        response = requests.get(url, timeout=5, headers=headers)

        if "event.button==2" in response.text:
            return -1

        return 1

    except Exception:
        return 0


# 모델 학습 당시 사용한 Feature 컬럼 순서
FEATURE_COLUMNS = [
    "having_ip_addr",
    "url_length",
    "shortening_service",
    "having_at_symbol",
    "double_slash_redirecting",
    "prefix_suffix",
    "having_sub_domain",
    "domain_registration_length",
    "Favicon",
    "Port",
    "HTTPS_token",
    "age_of_domain",
    "dns_record",
    "count_Redirection",
    "Disabling_Right_Click",
]


def extract_features(url):
    """
    URL에서 15개의 특징값을 추출합니다.

    컬럼명과 순서는 기존 머신러닝 모델이
    학습할 때 사용한 데이터셋과 동일하게 유지합니다.
    """

    features = {
        "having_ip_addr": having_ip_address(url),
        "url_length": url_length(url),
        "shortening_service": shortening_service(url),
        "having_at_symbol": having_at_symbol(url),
        "double_slash_redirecting": double_slash_redirecting(url),
        "prefix_suffix": prefix_suffix(url),
        "having_sub_domain": having_sub_domain(url),
        "domain_registration_length": domain_registration_length(url),
        "Favicon": favicon(url),
        "Port": port(url),
        "HTTPS_token": https_token(url),
        "age_of_domain": age_of_domain(url),
        "dns_record": dns_record(url),
        "count_Redirection": count_redirection(url),
        "Disabling_Right_Click": disabling_right_click(url),
    }

    # 기존 모델 학습 당시 Feature 순서를 명시적으로 유지
    features_df = pd.DataFrame([features], columns=FEATURE_COLUMNS)

    # 비지도학습 모델의 거리 계산에 사용하는 배열
    features_array = features_df.to_numpy().flatten()

    return features_df, features_array
