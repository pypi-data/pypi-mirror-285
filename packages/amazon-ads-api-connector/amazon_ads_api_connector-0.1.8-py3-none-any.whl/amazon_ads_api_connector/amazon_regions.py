from enum import Enum


class Region(Enum):
    NA = {
        "url": "https://advertising-api.amazon.com",
        "authorization_url": "https://api.amazon.com/auth/o2/token",
    }
    EU = {
        "url": "https://advertising-api-eu.amazon.com",
        "authorization_url": "https://api.amazon.co.uk/auth/o2/token",
    }
    FE = {
        "url": "https://advertising-api-fe.amazon.com",
        "authorization_url": "https://api.amazon.co.jp/auth/o2/token",
    }
