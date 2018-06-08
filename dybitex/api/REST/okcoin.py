"""
Contains all API Client sub-classes, which store exchange specific details
and feature the respective exchanges authentication method (sign()).
"""
# Import Built-ins
import logging
import hashlib
import hmac
import json
import requests
import datetime
# Import Homebrew
from dybitex.api.REST.api import APIClient
# Import third-party library
import pandas as pd

log = logging.getLogger(__name__)


class OKCoinREST(APIClient):
    def __init__(self, key=None, secret=None, api_version='v1',
                 url='https://www.okex.com/api', timeout=5,
                 headers={"contentType": "application/x-www-form-urlencoded"}):
        super(OKCoinREST, self).__init__(url, api_version=api_version,
                                         key=key, secret=secret,
                                         timeout=timeout)
        self.url = url
        self.version = api_version
        self.headers = headers
        self.timeout = timeout

    def change_timeout(self, timeout):
        self.timeout = timeout

    def sign(self, dictionary):
        data = self._chg_dic_to_sign(dictionary)
        signature = self.__md5(data)
        return signature.upper()

    def _chg_dic_to_str(self, dictionary):
        keys = list(dictionary.keys())
        keys.remove("self")
        keys.sort()
        strings = []
        for key in keys:
            if dictionary[key] != None:
                if not isinstance(dictionary[key], str):
                    strings.append(key + "=" + str(dictionary[key]))
                    continue
                strings.append(key + "=" + dictionary[key])

        return ".do?" + "&".join(strings)

    def _chg_dic_to_sign(self, dictionary):
        keys = list(dictionary.keys())
        if "self" in keys:
            keys.remove("self")
        keys.sort()
        strings = []
        for key in keys:
            if dictionary[key] != None:
                if not isinstance(dictionary[key], str):
                    strings.append(key + "=" + str(dictionary[key]))
                    continue
                strings.append(key + "=" + dictionary[key])
        strings.append("secret_key" + "=" + self.secret)
        return "&".join(strings)

    def _chg_mktime_to_datetime_ms(self, string):
        pass

    def _chg_mktime_to_datetime_s(self, string):
        pass

    def kline(self, symbol, type, size=None, since=None):
        pass

    def ticker(self, symbol):
        pass

    def depth(self, symbol, size=None):
        pass

    def trades(self, symbol, since=None):
        pass

    def _get_url_func(self, url, params=""):
        return self.url + "/" + self.version + "/" + url + params

    def _post_url_func(self, url):
        return self.url + "/" + self.version + "/" + url + ".do"

    def __md5(self, string):
        m = hashlib.md5()
        m.update(string.encode("utf-8"))
        return m.hexdigest()

    def exchange_rate(self):
        r = requests.get(self._get_url_func("exchange_rate.do"))
        return r.json()


class OKCoinSpotREST(OKCoinREST):
    def __init__(self):
        super(OKCoinSpotREST, self).__init__()
        self.__get_url_dic = {"kline": "kline", "ticker": "ticker", "kline": "kline", "depth": "depth",
                              "trades": "trades"}
        self.__post_url_dic = {"trade": "trade", "userinfo": "userinfo",
                               "wallet_info": "wallet_info", "orders_info": "orders_info",
                               "order_history": "order_history", "batch_trade": "batch_trade",
                               "cancel_order": "cancel_order", "order_info": "order_info",
                               "withdraw": "withdraw", "cancel_withdraw": "cancel_withdraw",
                               "withdraw_info": "withdraw_info", "account_records": "account_records",
                               "funds_transfer": "funds_transfer"}

    def kline(self, symbol, type, size=None, since=None):
        params = self._chg_dic_to_str(locals())
        url = self._get_url_func(self.__get_url_dic["kline"], params=params)
        print(url)
        r = requests.get(url, headers=self.headers, timeout=self.timeout)
        text = eval(r.text)
        df = pd.DataFrame(text, columns=["trade_date", "open", "high", "low", "close", "volume"])
        df["trade_date"] = df["trade_date"].map(
            lambda x: datetime.datetime.fromtimestamp(x / 1000).strftime("%Y-%m-%d %H:%M:%S"))
        df = df.set_index("trade_date")
        return df.to_dict()

    def ticker(self, symbol):
        params = self._chg_dic_to_str(locals())
        url = self._get_url_func(self.__get_url_dic["ticker"], params=params)
        print(url)
        r = requests.get(url, headers=self.headers, timeout=self.timeout)
        data = r.json()
        data["date"] = datetime.datetime.fromtimestamp(int(data["date"])).strftime("%Y-%m-%d %H:%M:%S")
        return data

    def depth(self, symbol, size=None):
        params = self._chg_dic_to_str(locals())
        url = self._get_url_func(self.__get_url_dic["depth"], params=params)
        print(url)
        r = requests.get(url, headers=self.headers, timeout=self.timeout)
        data = r.json()
        return data

    def trades(self, symbol, since=None):
        params = self._chg_dic_to_str(locals())
        url = self._get_url_func(self.__get_url_dic["trades"], params=params)
        print(url)
        r = requests.get(url, headers=self.headers, timeout=self.timeout)
        data = pd.DataFrame(r.json())
        data=data.set_index("date_ms")
        return data.to_dict()

    def userinfo(self):
        signed_data = {"api_key": self.key}
        data = {"api_key": self.key, "sign": self.sign(signed_data)}
        url = self._post_url_func(self.__post_url_dic["userinfo"])
        print(url)
        r = requests.post(url, data=data, timeout=self.timeout)
        return r.json()

    def trade(self, symbol, type, price=None, amount=None):
        signed_data = {"api_key": self.key, "symbol": symbol, "type": type, "price": price, "amount": amount}
        data = {"api_key": self.key, "sign": self.sign(signed_data), "symbol": symbol, "type": type}
        url = self._post_url_func(self.__post_url_dic["trade"])
        print(url)
        if price != None:
            data["price"] = price
        if amount != None:
            data["amount"] = amount
        r = requests.post(url, data=data, timeout=self.timeout)
        return r.json()

    def order_info(self, symbol, order_id):
        signed_data = {"api_key": self.key, "symbol": symbol, "order_id": order_id}
        url = self._post_url_func(self.__post_url_dic["order_info"])
        print(url)
        data = {"api_key": self.key, "symbol": symbol, "order_id": order_id}
        data["sign"] = self.sign(signed_data)
        r = requests.post(url, data=data, timeout=self.timeout)
        return r.json()

    def orders_info(self, type, symbol, order_id):
        signed_data = {"api_key": self.key, "symbol": symbol, "order_id": order_id, "type": type}
        url = self._post_url_func(self.__post_url_dic["orders_info"])
        print(url)
        data = {"api_key": self.key, "symbol": symbol, "type": type, "order_id": order_id}
        data["sign"] = self.sign(signed_data)
        r = requests.post(url, data=data, timeout=self.timeout)
        return r.json()

    def cancel_order(self, symbol, order_id):
        signed_data = {"api_key": self.key, "symbol": symbol, "order_id": order_id}
        url = self._post_url_func(self.__post_url_dic["cancel_order"])
        print(url)
        data = {"api_key": self.key, "symbol": symbol, "order_id": order_id}
        data["sign"] = self.sign(signed_data)
        r = requests.post(url, data=data, timeout=self.timeout)
        return r.json()

    def order_history(self, symbol, status, current_page, page_length):
        signed_data = {"api_key": self.key, "symbol": symbol, "status": status, "current_page": current_page,
                       "page_length": page_length}
        url = self._post_url_func(self.__post_url_dic["order_history"])
        print(url)
        data = {"api_key": self.key, "symbol": symbol, "status": status, "current_page": current_page,
                "page_length": page_length}
        data["sign"] = self.sign(signed_data)
        r = requests.post(url, data=data, timeout=self.timeout)
        return r.json()

    def wallet_info(self):
        signed_data = {"api_key": self.key}
        data = {"api_key": self.key, "sign": self.sign(signed_data)}
        url = self._post_url_func(self.__post_url_dic["wallet_info"])
        print(url)
        r = requests.post(url, data=data, timeout=self.timeout)
        print(r.status_code)
        return r.json()

    def batch_trade(self, symbol, orders_data, type=None):
        signed_data = {"api_key": self.key, "symbol": symbol, "type": type, "orders_data": orders_data}
        data = {"api_key": self.key, "sign": self.sign(signed_data)}
        url = self._post_url_func(self.__post_url_dic["batch_trade"])
        print(url)
        data["symbol"] = symbol
        data["orders_data"] = orders_data
        if type != None:
            data["type"] = type
        r = requests.post(url, data=data, timeout=self.timeout)
        return r.json()

    def withdraw(self, symbol, chargefee, trade_pwd, withdraw_address, withdraw_amount, target):
        signed_data = {"api_key": self.key, "chargefee": chargefee, "symbol": symbol, "trade_pwd": trade_pwd,
                       "withdraw_address": withdraw_address, "withdraw_amount": withdraw_amount, "target": target}
        data = {"api_key": self.key,"symbol":symbol, "sign": self.sign(signed_data), "chargefee": chargefee, "trade_pwd": trade_pwd,
                "withdraw_address": withdraw_address, "withdraw_amount": withdraw_amount, "target": target}
        url = self._post_url_func(self.__post_url_dic["withdraw"])
        print(url)
        r = requests.post(url, data=data, timeout=self.timeout)
        return r.json()

    def cancel_withdraw(self, symbol, withdraw_id):
        signed_data = {"api_key": self.key, "symbol": symbol, "withdraw_id": withdraw_id}
        data = {"api_key": self.key, "sign": self.sign(signed_data), "symbol": symbol, "withdraw_id": withdraw_id}
        url = self._post_url_func(self.__post_url_dic["cancel_withdraw"])
        print(url)
        r = requests.post(url, data=data, timeout=self.timeout)
        return r.json()

    def withdraw_info(self, symbol, withdraw_id):
        signed_data = {"api_key": self.key, "symbol": symbol, "withdraw_id": withdraw_id}
        data = {"api_key": self.key, "sign": self.sign(signed_data), "symbol": symbol, "withdraw_id": withdraw_id}
        url = self._post_url_func(self.__post_url_dic["withdraw_info"])
        print(url)
        r = requests.post(url, data=data, timeout=self.timeout)
        return r.json()

    def account_records(self, symbol, type, current_page, page_length):
        signed_data = {"api_key": self.key, "symbol": symbol, "type": type, "current_page": current_page,
                       "page_length": page_length}
        data = {"api_key": self.key, "sign": self.sign(signed_data), "symbol": symbol, "type": type,
                "current_page": current_page, "page_length": page_length}
        url = self._post_url_func(self.__post_url_dic["account_records"])
        print(url)
        r = requests.post(url, data=data, timeout=self.timeout)
        return r.json()

    def funds_transfer(self, symbol, amount, from_account, to_account):
        signed_data = {"api_key": self.key, "symbol": symbol, "amount": amount, "from": from_account, "to": to_account}
        data = {"api_key": self.key, "sign": self.sign(signed_data), "symbol": symbol,
                "amount": amount, "from": from_account, "to": to_account}
        url = self._post_url_func(self.__post_url_dic["funds_transfer"])
        print(url)
        r = requests.post(url, data=data, timeout=self.timeout)
        return r.json()


class OKCoinFuturesREST(OKCoinREST):
    def __init__(self):
        super(OKCoinFuturesREST, self).__init__()
        self.__get_url_dic = {"future_ticker": "future_ticker", "future_depth": "future_depth",
                              "future_trades": "future_trades",
                              "future_index": "future_index", "future_estimated_price": "future_estimated_price",
                              "future_kline": "future_kline", "future_hold_amount": "future_hold_amount",
                              "future_price_limit": "future_price_limit"}
        self.__post_url_dic = {"future_userinfo": "future_userinfo_4fix", "future_position": "future_position_4fix",
                               "future_trade": "future_trade", "future_trades_history": "future_trades_history",
                               "future_batch_trade": "future_batch_trade", "future_cancel": "future_cancel",
                               "future_order_info": "future_order_info", "future_orders_info": "future_orders_info",
                               "future_userinfo_4fix": "future_userinfo_4fix",
                               "future_position_4fix": "future_position_4fix",
                               "future_explosive": "future_explosive", "future_devolve": "future_devolve"}

    def future_ticker(self, symbol, contract_type):
        params = self._chg_dic_to_str(locals())
        url = self._get_url_func(self.__get_url_dic["future_ticker"], params=params)
        print(url)
        r = requests.get(url, headers=self.headers)
        data = r.json()
        data["date"] = datetime.datetime.fromtimestamp(int(data["date"])).strftime("%Y-%m-%d %H:%M:%S")
        return data

    def future_depth(self, symbol, size, contract_type, merge=None, ):
        params = self._chg_dic_to_str(locals())
        url = self._get_url_func(self.__get_url_dic["future_depth"], params=params)
        print(url)
        r = requests.get(url, headers=self.headers)
        data = r.json()
        return data

    def future_trades(self, symbol, contract_type):
        params = self._chg_dic_to_str(locals())
        url = self._get_url_func(self.__get_url_dic["future_trades"], params=params)
        print(url)
        r = requests.get(url, headers=self.headers)
        return r.json()

    def future_index(self, symbol):
        params = self._chg_dic_to_str(locals())
        url = self._get_url_func(self.__get_url_dic["future_index"], params=params)
        print(url)
        r = requests.get(url, headers=self.headers)
        return r.json()

    def future_estimated_price(self, symbol):
        params = self._chg_dic_to_str(locals())
        url = self._get_url_func(self.__get_url_dic["future_estimated_price"], params=params)
        print(url)
        r = requests.get(url, headers=self.headers)
        return r.json()

    def future_kline(self,symbol, type, contract_type, size=None, since=None):
        params = self._chg_dic_to_str(locals())
        url = self._get_url_func(self.__get_url_dic["future_kline"], params=params)
        print(url)
        r = requests.get(url, headers=self.headers, timeout=self.timeout)
        text = eval(r.text)
        df = pd.DataFrame(text, columns=["trade_date", "open", "high", "low", "close", "volume","%s_volume"%(symbol[:3])])
        df["trade_date"] = df["trade_date"].map(
            lambda x: datetime.datetime.fromtimestamp(x / 1000).strftime("%Y-%m-%d %H:%M:%S"))
        df = df.set_index("trade_date")
        return df.to_dict()

    def future_hold_amount(self, symbol, contract_type):
        params = self._chg_dic_to_str(locals())
        url = self._get_url_func(self.__get_url_dic["future_hold_amount"], params=params)
        print(url)
        r = requests.get(url, headers=self.headers)
        return r.json()

    def future_price_limit(self, symbol, contract_type):
        params = self._chg_dic_to_str(locals())
        url = self._get_url_func(self.__get_url_dic["future_price_limit"], params=params)
        print(url)
        r = requests.get(url, headers=self.headers)
        return r.json()

    def future_userinfo(self):
        api_key = self.key
        data = {"api_key": self.key, "sign": self.sign(locals())}
        url = self._post_url_func(self.__post_url_dic["future_userinfo"])
        print(url)
        r = requests.post(url, data=data, timeout=self.timeout)
        return r.json()

    def future_position(self, symbol, contract_type):
        api_key = self.key
        data = {"api_key": self.key, "sign": self.sign(locals()), "symbol": symbol, "contract_type": contract_type}
        url = self._post_url_func(self.__post_url_dic["future_position"])
        print(url)
        r = requests.post(url, data=data, timeout=self.timeout)
        return r.json()

    def future_trade(self, symbol, contract_type, price, amount, type, match_price=None, lever_rate=None):
        api_key = self.key
        data = {"api_key": self.key, "sign": self.sign(locals()), "symbol": symbol, "contract_type": contract_type,
                "price": price, "amount": amount, "type":type}
        if match_price != None:
            data["match_price"] = match_price
        if lever_rate != None:
            data["lever_rate"] = lever_rate
        print(data)
        url = self._post_url_func(self.__post_url_dic["future_trade"])
        print(url)
        r = requests.post(url, data=data, timeout=self.timeout)
        return r.json()

    def future_trades_history(self, symbol, date, since):
        api_key = self.key
        data = {"api_key": self.key, "sign": self.sign(locals()), "symbol": symbol, "date": date, "since": since}
        url = self._post_url_func(self.__post_url_dic["future_trades_history"])
        print(url)
        r = requests.post(url, data=data, timeout=self.timeout)
        return r.json()

    def future_batch_trade(self, symbol, contract_type, orders_data, lever_rate=None):
        api_key = self.key
        data = {"api_key": self.key, "sign": self.sign(locals()), "symbol": symbol, "contract_type": contract_type,
                "orders_data": orders_data}
        if lever_rate != None:
            data["lever_rate"] = lever_rate
        url = self._post_url_func(self.__post_url_dic["future_batch_trade"])
        print(url)
        r = requests.post(url, data=data, timeout=self.timeout)
        return r.json()

    def future_cancel(self, symbol, order_id, contract_type):
        api_key = self.key
        data = {"api_key": self.key, "sign": self.sign(locals()), "symbol": symbol, "contract_type": contract_type,"order_id":order_id}
        url = self._post_url_func(self.__post_url_dic["future_cancel"])
        print(url)
        r = requests.post(url, data=data, timeout=self.timeout)
        return r.json()

    def future_order_info(self, symbol, contract_type, order_id, status=None, current_page=None, page_length=None):
        api_key = self.key
        data = {"api_key": self.key, "sign": self.sign(locals()), "symbol": symbol, "contract_type": contract_type,
                "order_id": order_id}
        if status != None:
            data["status"] = status
        if current_page != None:
            data["current_page"] = current_page
        if page_length != None:
            data["page_length"] = page_length
        url = self._post_url_func(self.__post_url_dic["future_order_info"])
        print(url)
        r = requests.post(url, data=data, timeout=self.timeout)
        return r.json()

    def future_orders_info(self, symbol, contract_type, order_id):
        api_key = self.key
        data = {"api_key": self.key, "sign": self.sign(locals()), "symbol": symbol, "contract_type": contract_type,
                "order_id": order_id}
        url = self._post_url_func(self.__post_url_dic["future_orders_info"])
        print(url)
        r = requests.post(url, data=data, timeout=self.timeout)
        return r.json()

    def future_userinfo_4fix(self):
        api_key = self.key
        data = {"api_key": self.key, "sign": self.sign(locals())}
        url = self._post_url_func(self.__post_url_dic["future_userinfo_4fix"])
        print(url)
        r = requests.post(url, data=data, timeout=self.timeout)
        return r.json()

    def future_position_4fix(self, symbol, contract_type, lever_type=None):
        api_key = self.key
        data = {"api_key": self.key, "sign": self.sign(locals()), "symbol": symbol,
                "contract_type": contract_type}
        if lever_type != None:
            data["lever_type"] = lever_type
        url = self._post_url_func(self.__post_url_dic["future_position_4fix"])
        print(url)
        r = requests.post(url, data=data, timeout=self.timeout)
        return r.json()

    def future_explosive(self, symbol, contract_type, status, current_page=None, page_number=None, page_length=None):
        api_key = self.key
        data = {"api_key": self.key, "sign": self.sign(locals()), "symbol": symbol,
                "contract_type": contract_type, "status": status}
        if current_page != None:
            data["current_page"] = current_page
        if page_number != None:
            data["page_number"] = page_number
        if page_length != None:
            data["page_length"] = page_length
        url = self._post_url_func(self.__post_url_dic["future_explosive"])
        print(url)
        r = requests.post(url, data=data, timeout=self.timeout)
        return r.json()

    def future_devolve(self, symbol, transfer_type, amount):
        api_key = self.key
        data = {"api_key": self.key, "sign": self.sign(locals()), "symbol": symbol,
                "type": transfer_type, "amount": amount}
        url = self._post_url_func(self.__post_url_dic["future_devolve"])
        print(url)
        r = requests.post(url, data=data, timeout=self.timeout)
        return r.json()
