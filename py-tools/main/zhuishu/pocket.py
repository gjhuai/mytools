# coding=utf-8

import requests


# 参考: https://www.cnblogs.com/febwave/p/4242333.html
class Pocket(object):
    CONSUMER_KEY = '85393-d3bffe654b01e25ccc62075f'
    redirect_uri = "gjh-subscriber:authorizationFinished"
    headers={'X-Accept': 'application/json'}
    pocket_url_prefix = 'https://getpocket.com/v3'


class AccessTokenHandler(Pocket):
    def __init__(self):
        pass

    def get_access_token(self):
        request_token = self.get_request_token(self.redirect_uri)
        resp = requests.post(
            self.pocket_url_prefix + '/oauth/authorize',
            headers=self.headers,
            json={
                'consumer_key': self.CONSUMER_KEY,
                'code': request_token,
            })

        if resp.status_code in (400, 403):
            return None, None

        access_token = resp.json()['access_token'] # , resp.json()['username']
        with open('.pocket_access_token','w', encoding='UTF-8') as f:
            f.write(access_token)
        return access_token

    def get_request_token(self, redirect_uri:str):
        # get request token
        resp = requests.post(
            self.pocket_url_prefix + '/oauth/request',
            headers=self.headers,
            json={
                'consumer_key': self.CONSUMER_KEY,
                'redirect_uri': redirect_uri,
            })
        resp.raise_for_status()
        request_token = resp.json()['code']

        # 手动在浏览器上认证
        self.authenticate_in_browser(request_token, redirect_uri)

        return request_token

    def authenticate_in_browser(self, request_token, redirect_uri):
        print("请在浏览器中到此链接：")
        print(f'https://getpocket.com/auth/authorize?request_token={request_token}&redirect_uri={redirect_uri}')
        print("是否已在浏览器中打开[Y/n]：")
        yes = input();
        if yes!='Y':
            self.authenticate_in_browser(request_token, redirect_uri)

class PagePoster(Pocket):
    def read_local_access_token(self):
        access_token = None
        try:
            with open('.pocket_access_token','r', encoding='UTF-8') as f:
                access_token = f.readline()
        except Exception as exc:
            print("app catch: %s\n" % ( exc))
            print("请重新获取access-token。是否已获取到正确的access-token[Y/n]：")
            yes = input();
            if yes!='Y':
                return self.read_local_access_token()

        return access_token

    def post_page(self, url):
        access_token = self.read_local_access_token()

        resp = requests.post(
            self.pocket_url_prefix + '/add',
            headers=self.headers,
            json={
                'consumer_key': self.CONSUMER_KEY,
                'access_token': access_token,
                'url' : url
            })

        if resp.status_code in (400, 401, 403):
            print("Posting "+url+" 失败")
            return -1
        else:
            return 1


if __name__ == '__main__':
    pu = AccessTokenHandler()
    access_token = pu.get_access_token()
    print(access_token);

    poster = PagePoster()
    poster.post_page('https://www.cnblogs.com/panwenbin-logs/p/5521358.html')

