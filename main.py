import requests
from bs4 import BeautifulSoup
import sys


def get_ip():
    response = requests.get('https://2ip.ru/')
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        ip_address = soup.find('div', class_='ip')
        return ip_address.text.split()[0]
    else:
        return None


def get_time_zone(ip, token):
    url_table = 'https://geoip.maxmind.com/geoip/v2.1/city/' + ip + '?demo=1'
    token_in_request = 'Bearer ' + token
    headers = {
        'Authorization': token_in_request
        }
    response = requests.get(url_table, headers=headers)
    if response.status_code == 200:
        time_zone = response.json()['location']['time_zone']
        return time_zone
    else:
        return None


def get_token(x_csrf_token, cookie):
    url = 'https://www.maxmind.com/en/geoip2/demo/token'
    headers = {
                'X-Csrf-Token': x_csrf_token,
                'Cookie': cookie
                }
    session = requests.Session()
    response = session.post(url, headers=headers)
    if response.status_code == 201:
        token = response.json()['token']
        return token
    else:
        return None


def get_regions_in_timezone(time_zone):
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


def write_to_file(time_zone, regions):
    with open('regions.txt', 'w') as file:
        file.write(time_zone + '\n')
        for i in range(len(regions)):
            if i < len(regions)-1:
                file.write(regions[i] + ', ')
            else:
                file.write(regions[i] + '\n')


def get_x_csrf_token():
    x_csrf_token = input("Enter X-Csrf-Token: ")
    return x_csrf_token


def get_cookie_val():
    cookie = input("Enter cookie: ")
    return cookie


def test_task():
    ip = get_ip()
    if ip is None:
        print("ip not received")
        sys.exit(1)

    x_csrf_token = get_x_csrf_token()
    cookie = get_cookie_val()

    token = get_token(x_csrf_token, cookie)  # this is necessary to correctly formulate a get-request for time_zone
    if token is None:
        print("token not received")
        sys.exit(1)

    time_zone = get_time_zone(ip, token)
    if time_zone is None:
        print("time zone not received")
        sys.exit(1)

    regions = get_regions_in_timezone(time_zone)
    write_to_file(time_zone, regions)


def main():
    test_task()


if __name__ == main():
    main()
