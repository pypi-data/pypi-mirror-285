class Config:
    def __init__(self) -> None:
        # defining init, so IDE will think that all
        # Config instances, sub-instances has such inner values set
        self._init_config_values()

    def _init_config_values(self) -> None:
        self.PACKAGE_NAME = "dphelper"
        "Update this name after changing name in pyproject.toml"

        self.REQUEST_DROP_ON_FAILURE_COUNT = 4
        "How many `didnt connect` / `status >= 500` should occur sequentially before giving-up-on-request"

        self.REQUEST_INITIAL_SLEEP_AFTER_FAILURE_IN_S = 3
        "How many seconds to sleep after first request failure"

        self.REQUEST_SLEEP_INCREASE_POWER = 2
        "sleep time will be increased by this power. time ^ power"

        self.DP_URL = "https://dphelper.dataplatform.lt/"
        "url of server that stores snapshots, challenges, code runs. do not include ending slash"

        self.BACKEND_URL = "https://api.dataplatform.lt"
        "url of server that stores snapshots, challenges, code runs. do not include ending slash"

        self.BACKEND_SNAPSHOT_PATH = f"snapshots/"
        "backend url root for snapshots. it might be prepended in actual usage"

        self.BACKEND_UTILS_PATH = f"v1/utils/"
        "backend url root for utils. it might be appended in actual usage"

        self.IS_VERBOSE = False
        "verbose errors, warnings, etc.?"

        self.DEFAULT_HEADERS = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8,lt;q=0.7",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "sec-ch-ua": '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
        }

        self.HEADERS_UPDATE_ON_EMPTY = {
            "Referer": "https://google.com",
            "Cache-Control": "max-age=0",
            "Upgrade-Insecure-Requests": "1",
        }
        "what headers to append when generating auto-headers? auto-headers already include user agent, accept, connection"

        self.PROXY_PROVIDER = None
        "what proxy provider to use for outter requests? Snapshots would still be fetched directly"

        self.PROXY_PARAMS = {}
        "what params to use for proxying"

    def set_backend_url(self, new_backend_url: str) -> None:
        """Sets backend url. Do not forget http, https thingies.

        :param new_backend_url: the url where backend is located
        """
        if new_backend_url is None or new_backend_url == "":
            raise ValueError("Cannot set backend url to None or empty string")

        self.BACKEND_URL = new_backend_url

    def set_dp_url(self, new_dp_url: str) -> None:
        """Sets dp url. Do not forget http, https thingies.

        :param new_backend_url: the url where backend is located
        """
        if new_dp_url is None or new_dp_url == "":
            raise ValueError("Cannot set dp url to None or empty string")

        self.DP_URL = new_dp_url
