import requests

# Получаем массив всех прокси proxy-bunker
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


# Генерация 3proxy.cfg
def config_gen():
    # Получаем ip нашего сервера
    server_ip = requests.get('https://ifconfig.me/ip').text

    server_port = 15000

    proxy_list = get_proxy_list()

    f = open('3proxy.cfg', 'w')

    f.write('auth none\n')

    i = 0
    for proxy in proxy_list:

        proxy = proxy.split('|')
        if proxy[0] != "":
            current_proxy = proxy[0].split(':')

            if i > 0:
                f.write('flush\n')

            f.write('allow *\n')
            f.write('parent 1000 http ' + current_proxy[0] + ' ' + current_proxy[1] + '\n')
            f.write('proxy -n -p' + str(server_port) + '\n\n')

            server_port += 1
            i += 1

    return True


# Получаем и записываем в файл список всех прокси
config_gen()