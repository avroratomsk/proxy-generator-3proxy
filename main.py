import requests


def get_proxy_list():
    response = requests.get('https://proxy-bunker.com/api4.php?&socks=1')
    response_html = response.text.replace('\n', '')

    response_html = response_html.split('<br />')

    errors_count = len(response_html)

    if errors_count > 1:
        response_html = response_html[errors_count - 1]
    else:
        response_html = response_html[0]

    return response_html.split('\r')


def config_gen():
    server_ip = requests.get('https://ifconfig.me/ip').text

    server_port = 49152

    proxy_list = get_proxy_list()
    proxy_list_file = open('proxy_list.txt', 'w+')
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

    i = 0
    for proxy in proxy_list:

        proxy = proxy.split('|')
        if proxy[0] != "":
            current_proxy = proxy[0].split(':')

            proxy_list_file.write(server_ip + ':' + str(server_port) + '|' + proxy[1] + '\n')

            if i > 0:
                config_file.write('flush\n')

            config_file.write('allow *\n')
            config_file.write('parent 1000 socks5 ' + current_proxy[0] + ' ' + current_proxy[1] + '\n')
            config_file.write('proxy -n -p' + str(server_port) + '\n\n')

            server_port += 1
            i += 1


config_gen()

url = 'https://xn----otbbagxddjeiea.xn--p1ai/tasks/addNewProxy/'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

fp = open('proxy_list.txt', 'rb')

files = {'file': fp}

resp = requests.post(url, files=files, headers=headers)
fp.close()
print(resp.text)