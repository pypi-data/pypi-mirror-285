import requests
import pickle


class AjaxRequester:
    def __init__(self, cookie_file=None):
        self.session = requests.Session()
        if cookie_file:
            self.load_cookies_from_file(cookie_file)

    def load_cookies_from_file(self, file_path):
        """从文件加载cookies"""
        with open(file_path, 'rb') as file:
            cookies_dict = pickle.load(file)
        self.session.cookies.update(self.cookies_to_requests(cookies_dict))

    def save_cookies_to_file(self, file_path):
        """将cookies保存到文件"""
        with open(file_path, 'wb') as file:
            pickle.dump(self.session.cookies, file)

    def cookies_to_requests(self, cookies_dict):
        """将cookie字典转换为requests库可以使用的cookie"""
        jar = requests.cookies.RequestsCookieJar()
        for cookie in cookies_dict:
            jar.set(cookie['name'], cookie['value'], domain=cookie['domain'], path=cookie['path'])
        return jar

    def make_request(self, url, headers, data):
        """发送带cookie的POST请求"""
        response = self.session.post(url, headers=headers, data=data)
        return response.text
