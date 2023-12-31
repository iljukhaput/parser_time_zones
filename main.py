import requests
from bs4 import BeautifulSoup
import sys
import logging


logging.basicConfig(filename='log.txt',
                    level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                    )
log = logging.getLogger()


def get_ip():
    response = requests.get('https://2ip.ru/')
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        ip_address = soup.find('div', class_='ip')
        return ip_address.text.split()[0]
    else:
        return None


def get_time_zone(session, ip, token):
    url_table = 'https://geoip.maxmind.com/geoip/v2.1/city/' + ip + '?demo=1'
    token_in_request = 'Bearer ' + token
    headers = {
        'Authorization': token_in_request
        }
    response = session.get(url_table, headers=headers)
    if response.status_code == 200:
        time_zone = response.json()['location']['time_zone']
        return time_zone
    else:
        return None


def get_x_csrf_token(session):
    url = 'https://www.maxmind.com/en/geoip2-precision-demo'
    try:
        response = session.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        content = soup.find('div', class_='content')
        token_str = content.find('script').text
        i = token_str.rfind('X_CSRF_TOKEN')  # looking for the token in the string
        x_csrf_token = token_str[i+len('X_CSRF_TOKEN = "'):-3]  # cut out the token value

        return x_csrf_token
    except Exception:
        return None


def get_token(session, x_csrf_token):
    url = 'https://www.maxmind.com/en/geoip2/demo/token'
    headers = {
                'X-Csrf-Token': x_csrf_token
                }
    response = session.post(url, headers=headers)
    if response.status_code == 201:
        token = response.json()['token']
        return token
    else:
        return None


def get_regions_in_timezone(time_zone):
    try:
        url = 'https://gist.github.com/salkar/19df1918ee2aed6669e2'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', class_='highlight tab-size js-file-line-container js-code-nav-container js-tagsearch-file')
        lines = table.find_all('tr')
        regions_in_timezone = []
        for line in lines:
            if time_zone in line.text:
                regions_in_timezone.append((line.text.split('"'))[1])
        return regions_in_timezone
    except Exception:
        return None


def write_to_file(time_zone, regions):
    try:
        with open('regions.txt', 'w') as file:
            file.write(time_zone + '\n')
            for i in range(len(regions)):
                if i < len(regions)-1:
                    file.write(regions[i] + ', ')
                else:
                    file.write(regions[i] + '\n')
        return True
    except Exception:
        return False

def log_and_check_result(var, name):
    if var is None:
        log.error("%s was not received", name)
        sys.exit(1)
    log.info("%s was received", name)


def test_task():
    log.info("start")

    # on the 2ip.ru
    ip = get_ip()
    log_and_check_result(ip, 'IP')

    # on the maxmind.com
    session = requests.Session()
    x_csrf_token = get_x_csrf_token(session)
    log_and_check_result(x_csrf_token, 'X-CSFR token')

    token = get_token(session, x_csrf_token)  # this is necessary to correctly formulate a get-request for time_zone
    log_and_check_result(token, 'token')

    time_zone = get_time_zone(session, ip, token)
    log_and_check_result(time_zone, 'timezone')

    # on the github.com
    regions = get_regions_in_timezone(time_zone)
    log_and_check_result(regions, 'regions in timezone')

    write_ok = write_to_file(time_zone, regions)
    if write_ok:
        log.info("data was recorded to the file")
    else:
        log.error("data was not recorded to the file")
        sys.exit(1)

    log.info("finish")


def main():
    test_task()


if __name__ == main():
    main()
