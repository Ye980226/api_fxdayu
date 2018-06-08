# encoding: UTF-8

from __future__ import absolute_import
# from vnokex import *

# 在OkCoin网站申请这两个Key，分别对应用户名和密码
apiKey = '38918639-07c9-40f0-8ccc-289de132d01c'
secretKey = '0A38E3F0D3155CD025654DDCB94505C7'
spot_host = 'wss://real.okex.com:10441/websocket'

# 创建API对象
api = OkexSpotApi()

api.connect(spot_host,apiKey, secretKey, True)
sleep(3)

api.login()
# api.subscribeSpotTicker("ltc_btc")
# api.subscribeSpotDepth("ltc_btc")
# api.subscribeSpotDepth("ltc_btc", 5)
# api.subscribeSpotDeals("ltc_btc")
# api.subscribeSpotKlines("ltc_btc","30min")

# order = api.spotOrder("ltc_btc","buy", "0.000015" , "0.001")

# api.spotOrderInfo("ltc_btc",order["orderId"])
# api.spotCancelOrder("ltc_btc",order["orderId"])

api.spotUserInfo()
# api.subSpotBalance('ltc_btc')
# api.spotOrderInfo("ltc_btc", 415122191)



future_host='wss://real.okex.com:10440/websocket/okexapi'
api = OkexFuturesApi()
api.connect(future_host, apiKey, secretKey, True)

sleep(3)
# api.subsribeFuturesTicker("ltc_btc","this_week")
api.subscribeFuturesKline("btc","this_week", "30min")
# api.subscribeFuturesDepth("btc","this_week")
# api.subscribeFuturesDepth("btc","this_week", 5)

#api.subscribeFuturesTrades("btc","this_week")
# api.subscribeFuturesIndex("btc")
# api.subscribeFuturesForecast_price("btc")

api.login()
# order = api.futuresTrade( "ltc_btc", "this_week" ,"1" , 20 , 1 , matchPrice = '0' , leverRate = '1')  # 14245727693
# api.futuresCancelOrder("ltc_btc",order['order_id'], "this_week")
# api.futuresUserInfo()
#api.futuresOrderInfo("ltc_btc" , "14245727693" , "this_week" , '1', '1'  , '10')
# api.subscribeFuturesTrades()
# api.subscribeFuturesUserInfo()
# api.subscribeFuturesPositions()


'''
合约账户信息、 持仓信息等，在登录后都会自动推送。。。官方文档这样写的，还没实际验证过
'''
