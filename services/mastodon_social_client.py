import inspect
import traceback

import settings
from services.httpx_client import HTTPXClient, httpx_context_manager

settings = settings.get_settings()


@httpx_context_manager
class HTTPXMastodonInstanceServiceClient(HTTPXClient):
    mastodon_instance = settings.MASTODON_INSTANCE_ENDPOINT
    api_endpoint = "/api/v1/"

    def __init__(self):
        super().__init__(self.mastodon_instance, self.api_endpoint)

    @property
    def headers(self):
        return {"Content-Type": "application/json"}

    def get_tag_info(self, tag: str):
        try:
            url = f"{self.mastodon_instance}{self.api_endpoint}tags/{tag}"
            response = self.client.get(url=url, headers=self.headers)
            result = response.json()

            # calculate the number of usages in last 7 days and aggregate number of accounts
            accounts = 0
            uses = 0

            if "error" in result:
                return None, None, None, {"error": "Too Many Requests"}

            for day in result["history"]:
                accounts += int(day["accounts"])
                uses += int(day["uses"])

            return result["url"], accounts, uses, None
        except Exception as e:
            traceback.print_exc()
            return None, None, None, {format(inspect.currentframe().f_code.co_name): [str(e)]}
