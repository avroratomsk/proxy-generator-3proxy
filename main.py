from multiprocessing import Pool
import requests


def get_location(proxy):
    proxy = {'https': proxy}

    if proxy['https'] != '':
        try:
            response = requests.get('https://whoer.net/v2/geoip2-city', headers={'Accept': 'application/json'}, proxies=proxy, timeout=5)
            response_json = response.json()
            location = str(response_json['subdivision1_name']).replace('́с', 'с') + '|' + str(response_json['city_name']).replace('́с', 'с')

            if str(response_json['country_code']) == 'RU':
                if str(response_json['subdivision1_name']) != 'None' or str(response_json['city_name']) != 'None':
                    return str(proxy['https']) + '|' + location

        except Exception as e:
            pass


def get_proxy_list():
    response = requests.get('https://proxy-bunker.com/api2.php')
    response_html = response.text.replace('\n', '')

    return response_html.split('\r')


def get_trusted_ip_list():
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    response = requests.get('https://xn----otbbagxddjeiea.xn--p1ai/tasks/checkUsers/', headers=headers)
    response_html = response.text.replace('\n', '')

    return response_html.split('<br>')


def config_gen(checking_result):

    trusted_ip_list = get_trusted_ip_list()
    trusted_ip_str = ''

    i = 0

    for trusted_ip in trusted_ip_list:
        if trusted_ip != "":
            if i > 0:
                trusted_ip_str += ', ' + str(trusted_ip)
            else:
                trusted_ip_str += trusted_ip
            i += 1

    server_ip = requests.get('https://ifconfig.me/ip').text
    server_port = 49152

    config_file = open('3proxy.cfg', 'w+')

    config_file.write('setgid 125\n')
    config_file.write('setuid 117\n\n')
    config_file.write('nserver 8.8.8.8\n')
    config_file.write('nserver 77.88.8.8\n\n')
    config_file.write('nscache 65536\n\n')
    config_file.write('timeouts 1 5 30 60 180 1800 15 60\n\n')
    config_file.write('daemon\n\n')
    config_file.write('log /var/log/3proxy/3proxy.log D\n')
    config_file.write('logformat "- +_L%t.%. %N.%p %E %U %C:%c %R:%r %O %I %h %T"\n\n')
    config_file.write('auth iponly\n\n')

    proxy_list_file = open('proxy_list.txt', 'w+', encoding="utf-8")
    proxy_list_file.write('')

    i = 0

    for subdivision_proxys in checking_result:
        subdivision_start_port = server_port + i * 100

        print(subdivision_proxys['subdivision'])
        k = 0
        for proxy in subdivision_proxys['data']:
            print(str(subdivision_start_port) + ' - ' + proxy)
            proxy_str = proxy
            proxy = proxy.split('|')
            if proxy[0] != "":
                current_proxy = proxy[0].split(':')

                if subdivision_start_port > server_port:
                    config_file.write('flush\n')

                config_file.write('allow *\n')
                config_file.write('parent 1000 socks5 ' + current_proxy[0] + ' ' + current_proxy[1] + '\n')
                config_file.write('proxy -n -p' + str(subdivision_start_port) + '\n\n')

                proxy_list_file.write(server_ip + ':' + str(subdivision_start_port) + '|' + proxy_str + '\n')

                subdivision_start_port += 1
                k += 1
        
        print('=======================')
        i += 1


if __name__ == '__main__':
    proxy_list = get_proxy_list()

    p = Pool(30)
    checking_result = p.map(get_location, proxy_list)

    subdivisions_list = []
    subdivisions_proxy_list = []

    for proxy_data in checking_result:
        if proxy_data:
            current_proxy = proxy_data.split('|')
            subdivisions_list.append(current_proxy[1])

    subdivisions_list = list(set(subdivisions_list))
    subdivisions_list.sort()

    for subdivision in subdivisions_list:
        proxy_list = []
        for proxy_data in checking_result:
            if proxy_data:
                current_proxy = proxy_data.split('|')

                if current_proxy[1] == subdivision:
                    proxy_list.append(proxy_data)
        subdivisions_proxy_list.append({
            "subdivision": subdivision,
            "data" : proxy_list
        })

    config_gen(subdivisions_proxy_list)

    url = 'https://xn----otbbagxddjeiea.xn--p1ai/tasks/addNewProxy/'
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

    fp = open('proxy_list.txt', 'rb')

    files = {'file': fp}

    resp = requests.post(url, files=files, headers=headers)
    fp.close()
    print(resp.text)