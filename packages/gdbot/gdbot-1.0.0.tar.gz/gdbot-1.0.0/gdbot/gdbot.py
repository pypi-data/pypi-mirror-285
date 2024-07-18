import requests, base64, hashlib, itertools, time
from typing import Callable, List, Optional, Dict, Any

class GDBot:
    def __init__(self, username: str, password: str, lvl: str, config: Optional[Config] = None):
        self.username = username
        self.password = password
        self.lvl = lvl
        self.accID = self.getID(username)
        self.commands = {}
        self.ready = []
        self.errs = []
        self.banned = []
        self.config = config if config else Config()

    def base64_encode(self, s: str) -> str:
        return base64.urlsafe_b64encode(s.encode('utf-8')).decode('utf-8')

    def getID(self, user: str) -> str:
        r = requests.get(f"https://gdbrowser.com/api/profile/{user}")
        r.raise_for_status()
        data = r.json()
        if 'accountID' in data:
            return data['accountID']
        else:
            raise ValueError(f"LoginError: User {user} not found")

    def comment(self, msg: str, perc: str = "0") -> requests.Response:
        xor = lambda data, key: ''.join(chr(ord(x) ^ ord(y)) for (x, y) in zip(data, itertools.cycle(key)))
        gjp = lambda pw: base64.b64encode(xor(pw, "37526").encode()).decode().replace("+", "-").replace("/", "_")

        def generate_chk(values: List[str], key: str, salt: str) -> str:
            values.append(salt)
            string = "".join(map(str, values))
            return base64.urlsafe_b64encode(xor(hashlib.sha1(string.encode()).hexdigest(), key).encode()).decode()

        data = {
            "accountID": self.accID,
            "userName": self.username,
            "comment": base64.b64encode(msg.encode()).decode(),
            "gjp": gjp(self.password),
            "levelID": self.lvl,
            "percent": perc,
            "secret": "Wmfd2893gb7"
        }

        data["chk"] = generate_chk([self.username, base64.b64encode(msg.encode()).decode(), self.lvl, perc], "29481", "0xPT6iUrtws0J")

        proxies = self.config.get("proxy")
        response = requests.post("http://www.boomlings.com/database/uploadGJComment21.php", data=data, headers={"User-Agent": ""}, proxies=proxies if proxies else None)

        if response.text == "-10" or response.text.startswith("temp_"):
            for callback in self.banned:
                callback(self)
        print(response.text)
        return response.text

    def command(self, name: str) -> Callable:
        def decorator(func: Callable):
            self.commands[name] = func
            return func
        return decorator

    def on_ready(self, func: Callable[[Any], None]) -> None:
        self.ready.append(func)

    def on_error(self, func: Callable[[Any, Exception], None]) -> None:
        self.errs.append(func)

    def on_banned(self, func: Callable[[Any], None]) -> None:
        self.banned.append(func)

    def run(self):
        for callback in self.ready:
            callback(self)
        while True:
            try:
                proxies = self.config.get("proxy")
                r = requests.get(f"https://gdbrowser.com/api/comments/{self.lvl}?count=1", proxies={"http": proxies, "https": proxies} if proxies else None)
                if r.status_code == 200:
                    comment = r.json()[0].get('content')
                    for cmd, func in self.commands.items():
                        if comment.startswith(cmd):
                            func(self, comment)
            except requests.RequestException as e:
                for callback in self.errs:
                    callback(self, e)
            time.sleep(2)