from requests import ConnectionError, HTTPError, post
from fake_useragent import FakeUserAgent
from time import sleep
from bs4 import BeautifulSoup
from tiktok_driver._classes import DownloadInformation, DownloadType

headers = {
    "authority": "tiksave.io",
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "dnt": "1",
    "origin": "https://tiksave.io",
    "referer": "https://tiksave.io/en",
    "x-requested-with": "XMLHttpRequest"
}

fua = FakeUserAgent()

def get_download_info(post_url: str):
    global headers, fua
    
    # Set user agent.
    my_headers = headers.copy()
    
    # Post until success.
    response = None
    while response is None:
        my_headers['User-Agent'] = fua.random
        try:
            response = post(
                url='https://tiksave.io/api/ajaxSearch',
                headers=my_headers,
                data={
                    'q': post_url,
                    'lang': 'en'
                }
            )
            response.raise_for_status()
            break
        except (HTTPError, ConnectionError):
            sleep(5)
    
    # Parse html and convert to soup.
    html = response.json()['data']
    soup = BeautifulSoup(html, features='html.parser')
    
    # Check for 'Download MP4 HD' button. Return if present.
    buttons = soup.find_all('a', attrs={'class': 'tik-button-dl button dl-success'})
    buttons = list(filter(lambda button: 'Download MP4 HD' in button.text, buttons))
    if len(buttons) > 0:
        return list(map(lambda button: DownloadInformation(button.get('href'), DownloadType.VIDEO), buttons))
    
    # If no video button is present, return any image download buttons.
    buttons = soup.find_all('a', attrs={'class': 'btn-premium'})
    return list(map(lambda button: DownloadInformation(button.get('href'), DownloadType.IMAGE), buttons))
