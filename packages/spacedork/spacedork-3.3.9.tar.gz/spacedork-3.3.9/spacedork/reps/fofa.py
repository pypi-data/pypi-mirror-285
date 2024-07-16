import base64
import logging
import typing

import requests
from spacedork.reps.base import SearchBase

logger = logging.getLogger("dork")


class Fofa(SearchBase):
    URL = 'https://fofa.info/api/v1/search/all'

    def __init__(self, session: requests.session, token=None, limit=10, **kwargs):
        super().__init__(**kwargs)
        self.token = token
        self.client = session
        self.limit = limit
        self._total = 0

    @staticmethod
    def format_fofa(item: dict) -> typing.Dict:
        new_item = {
            "url": f'{item[0]}://{item[1]}:{item[2]}',
            "ip": item[1],
            "port": item[2],
        }
        return new_item

    def _query(self, dork: str, page: int) -> typing.Optional[typing.List[dict]]:
        resp = requests.Response()
        items = []
        for i in range(3):
            try:
                resp = self.client.get(self.URL, timeout=60,
                                       params={"qbase64": base64.b64encode(dork.encode()).decode(),
                                               "page": page, "key": self.token,
                                               "fields": "protocol,ip,port"})
                break
            except Exception as e:
                logger.debug(f"Req Error:{e} to continue")
                break
        if resp.status_code is None:
            return
        if resp and resp.status_code == 200:
            content = resp.json()
            if content["error"]:
                logger.error(f"Fofa Error:{content['errmsg']}")
                return
            try:
                total = content['size']
                self._total = total
            except Exception as e:
                logger.debug(e)
                return
            for match in content['results']:
                item = self.format_fofa(match)
                items.append(item)
            return items
        else:
            logger.debug(f"req Error:{resp}")


if __name__ == "__main__":
    fofa = Fofa("")
    fofa.query('')
