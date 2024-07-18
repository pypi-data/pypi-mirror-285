import requests
import pickle, re
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from .utils import (templates, cookie_to_string)

class Login:
    def __init__(self, subdomain: str='mbasic'):
        '''
        Login using several Facebook methods.
        '''
        self.session = requests.session()
        self.session.headers.update({'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7','Accept-Encoding': 'gzip, deflate','Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7','Content-Type': 'application/x-www-form-urlencoded','dpr': '2.25','Origin': 'https://mbasic.facebook.com','Referer': 'https://mbasic.facebook.com/login.php?next=https%3A%2F%2Fmbasic.facebook.com%2F%3Fstype%3Dlo%26deoia%3D1%26jlou%3DAfdSmcCA6K0Mupy0d8n-B7KTXxEKX0HTxIY9EhjthO9sYUuBlD10HJ7nRDEWULlFzTaXSKHuPMCd0mhdXRQ032zGdaXk55-QgHCyetWMNvk8zg%26smuh%3D34845%26lh%3DAc8fz3ZmFcs0McAEcjQ%26refid%3D8%26ref_component%3Dmbasic_footer&refsrc=deprecated&refid=8&ref_component=mbasic_footer&_rdr','sec-ch-prefers-color-scheme': 'dark','sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="117", "Google Chrome";v="117"','sec-ch-ua-mobile': '?0','sec-ch-ua-platform': '"Windows"','Sec-Fetch-Dest': 'document','Sec-Fetch-Mode': 'navigate','Sec-Fetch-Site': 'same-origin','Sec-Fetch-User': '?1','Upgrade-Insecure-Requests': '1','User-Agent': UserAgent().chrome,'viewport-width': '980'})
        self.domain = f'https://{subdomain}.facebook.com/'
    
    def __regular__(self, email: str, password: str) -> dict:
        '''
        Regular methods.
        '''
        login_forms = BeautifulSoup(self.session.get(self.domain +'login').text, 'html.parser').find('form')
        try:
            payload = {tags.get('name'): tags.get('value') for tags in login_forms('input')}
            payload.update({'email': email, 'pass': password})
            del payload['sign_up']

            post_payload = BeautifulSoup(self.session.post(self.domain + login_forms['action'], data=payload).text, 'html.parser')
            open('/sdcard/src.html', 'w').write(str(post_payload))
            return templates(status=True, data={'session': pickle.dumps(self.session), 'useragent': self.session.headers['User-Agent'], 'email': email, 'password': password, 'cookies_string': cookie_to_string(self.session.cookies.get_dict())})
        except Exception as e:
            return templates(status=False, error=str(e))

class Api:
    islogin = False
    token = None

    def __init__(self, cookies: str=None, mailpass: dict=None):
        self.session = requests.session()
        self.graph = 'https://graph.facebook.com/'
        try: 
            self.session.cookies['cookie'] = cookies if cookies is not None else Login(subdomain='mbasic').__regular__(email=mailpass['email'], password=mailpass['password'])['data']['cookies_string']
            self.islogin = True
            self.token = self.scrape_token()['data']['token']
        except KeyError:
            self.islogin = False

    def scrape_token(self) -> str:
        '''
        Scrape EAAB Token.
        For access graph api.
        '''
        try:
            wrizz = re.search(r'location\.replace\("(.*?)"\)', self.session.get('https://adsmanager.facebook.com/adsmanager/manage').text).group(1)
            lrizz = re.search(r'__accessToken="(EAAB.*?)"', self.session.get(wrizz.replace('\\','')).text).group(1)
            return templates(status=True, data={'token': lrizz, 'cookies': self.session.cookies['cookie']})
        except Exception as e:
            return templates(status=False, error=str(e))

    def dump_friendlist(self, id: str, cursor: str = None) -> dict:
        '''
        Take a list of your friends or friends of someone whose friend's account privacy is public.
        Please use facebook id only, not facebook username.
        '''
        wrizz = self.session.get(self.graph + (id if id.isdigit() else self.username_toid(id))['data']['id'], params={'access_token': self.token, 'fields': 'name,friends.fields(id, name, birthday)' if cursor is None else +f'after({cursor})'}).json()
        print(wrizz)
        try:
            aura = wrizz['friends']['data']
            return templates(status=True, data={'friends': aura, 'name': wrizz['name'], 'cursor': wrizz['friends']['paging']['cursors']['after']})
        except Exception as e:
            return templates(status=False, error=str(e))

    def account_info(self, id: str=None):
        '''
        Retrieve your Facebook account info or other people's accounts based on ID.
        '''
        wrizz = self.session.get(self.graph + ((id if id.isdigit() else self.username_toid(id)) if id is not None else 'me') +'?fields=id,name&access_token='+ self.token).json()
        try: 
            return templates(status=True, data={'name': wrizz['name'], 'id': wrizz['id'], 'token': self.token, 'cookies': self.session.cookies['cookie']})
        except Exception as e: 
            return templates(status=False, error=str(e))

    def username_toid(self, username: str) -> dict:
        '''
        Convert from username to id via mbasic.
        '''
        wrizz = self.session.get('https://mbasic.facebook.com/'+ username).text
        try: 
            lrizz = re.search(r'block/confirm/\?bid=(.*?)\&', wrizz).group(1)
            name = re.search(r'<title>(.*?)</title>', wrizz).group(1)
            return templates(status=True, data={'id': lrizz, 'username': username, 'name': name})
        except Exception as e:
            return templates(status=False, error=str(e))

    

    




