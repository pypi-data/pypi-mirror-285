from binance.spot import Spot

client = Spot()

# Get server timestamp
# Get klines of BTCUSDT at 1m interval
# Get last 10 klines of BNBUSDT at 1h interval

# API key/secret are required for user data endpoints
# client = Spot(api_key='<api_key>', api_secret='<api_secret>')
#
# # Get account and balance information
# print(client.account())
#
# # Post a new order
# params = {
#     'symbol': 'BTCUSDT',
#     'side': 'SELL',
#     'type': 'LIMIT',
#     'timeInForce': 'GTC',
#     'quantity': 0.002,
#     'price': 9500
# }
#
# response = client.new_order(**params)
# print(response)
