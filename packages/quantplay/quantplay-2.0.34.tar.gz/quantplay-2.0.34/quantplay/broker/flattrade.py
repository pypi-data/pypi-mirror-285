import binascii
import hashlib
from queue import Queue

import requests

from quantplay.broker.ft_utils.flattrade_utils import FlatTradeUtils
from quantplay.broker.ft_utils.ft_noren import FT_NorenApi
from quantplay.broker.noren import Noren
from quantplay.exception.exceptions import InvalidArgumentException, RetryableException
from quantplay.model.order_event import OrderUpdateEvent


class FlatTrade(Noren):
    def __init__(
        self,
        order_updates: Queue[OrderUpdateEvent] | None = None,
        api_secret: str | None = None,
        password: str | None = None,
        totp_key: str | None = None,
        user_id: str | None = None,
        user_token: str | None = None,
        api_key: str | None = None,
        load_instrument: bool = True,
    ):
        super().__init__(order_updates=order_updates, load_instrument=load_instrument)
        self.api = FT_NorenApi(
            "https://piconnect.flattrade.in/PiConnectTP/",
            "wss://piconnect.flattrade.in/PiConnectWSTp/",
        )

        try:
            if user_token and user_id:
                self.api.set_session(userid=user_id, usertoken=user_token)

            elif user_id and password and totp_key and api_key and api_secret:
                token = self.login(
                    user_id=user_id,
                    password=password,
                    totp_key=totp_key,
                    api_key=api_key,
                    api_secret=api_secret,
                )

                self.api.set_session(userid=user_id, usertoken=token)

            else:
                raise InvalidArgumentException("Missing Arguments")

            response = {
                "susertoken": user_token,
                "actid": user_id,
                "email": None,
                "uname": None,
            }

        except InvalidArgumentException:
            raise
        except binascii.Error:
            raise InvalidArgumentException("Invalid TOTP key provided")
        except Exception as e:
            raise RetryableException(str(e))

        self.set_attributes(response)

    def login(
        self,
        user_id: str,
        password: str,
        totp_key: str,
        api_key: str,
        api_secret: str,
    ):
        reqCode = FlatTradeUtils.get_request_code(
            api_key=api_key, user_id=user_id, password=password, totp=totp_key
        )

        secret_code = api_key + reqCode + api_secret
        payload = {
            "api_key": api_key,
            "request_code": reqCode,
            "api_secret": hashlib.sha256(secret_code.encode()).hexdigest(),
        }
        url3 = "https://authapi.flattrade.in/trade/apitoken"

        res3 = requests.post(url3, json=payload)
        token = res3.json()["token"]

        return token
