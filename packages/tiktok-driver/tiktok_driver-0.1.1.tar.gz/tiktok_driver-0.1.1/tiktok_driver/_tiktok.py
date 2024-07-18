from nodriver import Browser, Tab, start
from asyncio import TimeoutError
from time import sleep
from random import random
from re import compile, match
from dataclasses import dataclass

@dataclass
class TiktokPost:
    url: str
    id: str

class TiktokErrors:
    class ProfilePrivate(RuntimeError):
        pass
            
    class ProfileNonexistent(RuntimeError):
        pass

class TiktokResult:
    def __init__(self, tab: Tab, username: str) -> None:
        self.__tab = tab
        self.__username = username
        self.__pattern = compile(rf'https://www.tiktok.com/@{username}/.*/(\d*)')

    async def get_posts(self) -> list[TiktokPost]:
        try:
            a_elements = await self.__tab.select_all(f'[href^="https://www.tiktok.com/@{self.__username}/"]', timeout=3)
            hrefs = list(set([str(element.attrs['href']) for element in a_elements]))
            pairs = map(lambda href: (href, match(self.__pattern, href).groups()), hrefs)
            return [TiktokPost(pair[0], pair[1][0]) for pair in pairs if pair[1] and len(pair[1]) > 0]
        except TimeoutError:
            return []
        
    async def raise_for_error(self):
        try:
            error = await self.__tab.select("p[class*=emuynwa1]", timeout=3)
        except TimeoutError:
            return
        
        match error.text:
            case "This account is private":
                raise TiktokErrors.ProfilePrivate()
            case "Couldn't find this account":
                raise TiktokErrors.ProfileNonexistent()

class TiktokDriver:
    async def get_instance():
        browser = await start()
        return TiktokDriver(browser)
    
    def __init__(self, browser: Browser) -> None:
        self.browser = browser
        
    async def get_user(self, username: str):
        tab = await self.browser.get(f'https://tiktok.com/@{username}')
        await self.__answer_prompts(tab)
        return TiktokResult(tab, username)
        
    async def __answer_prompts(self, tab: Tab):
        # Sign in as guest if prompt blocks screen
        while True:
            try:
                buttons = await tab.select_all('div[class*=css-1cp64nz-DivTextContainer]', timeout=5)
                await buttons[-1].click()
            except TimeoutError:
                break
            
        # Press try again button until 'Something went wrong' screen disappears.
        while True:
            try:
                button = await tab.select('button[class*=emuynwa3]', timeout=3)
                sleep(random()/2)
                await button.click()
            except TimeoutError:
                break