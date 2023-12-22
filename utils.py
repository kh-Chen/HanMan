import requests

def download(link, filepath, headers, proxies):
    for i in range(3):
        try:
            r = requests.get(url=link, headers=headers, proxies=proxies)
            if r.status_code == 200:
                with open(filepath, 'wb') as f:
                    f.write(r.content)
                break
            else:
                print(f'获取失败。code: {r.status_code} link: {link}')
        except Exception as e:
            print(f'获取失败。code: {r.status_code} link: {link} error: {e}')
    print(filepath + "download end.")