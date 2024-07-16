import logging
import typing

import requests

from spacedork.reps.base import SearchBase

logger = logging.getLogger("dork")


def format_zoomeye(item):
    service = item['portinfo']['service']
    port = str(item['portinfo']['port'])
    new_item = {

        "port": port,
    }
    if isinstance(item["ip"], list):
        if item["ip"]:
            new_item["ip"] = item["ip"][0]
        else:
            new_item["ip"] = ""
    else:
        new_item["ip"] = item['ip']

    if "site" in item and item["site"]:
        new_item["url"] = f"{service}://{item['site']}"
    else:
        if "443" in port:
            new_item["url"] = f"{service}://{item['ip']}:{port}"
        else:
            new_item["url"] = f"{service}://{item['ip']}:{port}"
    if "country_name_CN" in item:
        new_item["country"] = item.pop("country_name_CN")
    if "subdivisions_name_CN" in item:
        new_item["city"] = item.pop("subdivisions_name_CN")
    return new_item


class ZoomEye(SearchBase):
    URL = 'https://api.zoomeye.org/host/search'

    def __init__(self, session: requests.session, token=None, **kwargs):
        super().__init__(**kwargs)
        self.token = token
        self.resources = None
        self.client = session
        self.client.headers = {'User-Agent': 'Python Zoomeye Client 3.0', 'API-KEY': token}
        self.total = -1
        self.set_host()

    def set_host(self):
        r = self.client.get('https://api.zoomeye.org/resources-info')
        if r.status_code == 403 and "api.zoomeye.hk" in r.text:
            self.URL = "https://api.zoomeye.hk/host/search"
            logger.info("set host:{}".format(self.URL))

    def _query(self, dork: str, page, resource='host') -> typing.Optional[typing.List[dict]]:
        resp = requests.Response()
        for i in range(3):
            try:
                resp = self.client.get(self.URL, params={"query": dork, "page": page})
                break
            except Exception as e:
                logger.debug(f"Req Error:{e}")
                return
        items = []
        if resp and resp.status_code == 200 and 'matches' in resp.text:
            content = resp.json()
            total = content['total']
            self.total = total
            for match in content['matches']:
                item = format_zoomeye(match)
                items.append(item)
            return items
        else:
            logger.warning(f"req Error:{resp}")


if __name__ == "__main__":
    zoomeye = ZoomEye("", fields="url")
    zoomeye.query('weblogic')
