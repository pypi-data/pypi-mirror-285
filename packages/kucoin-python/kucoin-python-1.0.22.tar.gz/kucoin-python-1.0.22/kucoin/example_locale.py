import time

from kucoin.client import Margin, Trade, Lending, Earn


def test_Trade():

    trade = Trade(key='', secret='', passphrase='')
    #res=client.get_interest_rates("BTC")
    res =trade.create_market_order(symbol='FRM-USDT',side='buy',clientOid=f'clientid-{time.time()*1000}',size=5)
    print(res)

def test_Lending():
    lending = Lending(key='668aac1303b7f800017a7c33', secret='bcb25e2a-77db-4e39-85a2-4369f78edc9c', passphrase='abc,123*')
    #client2.TCP_NODELAY=1
    s=time.time_ns()
    ns=5
    for n in range(ns):
      res= lending.get_currency_information(currency='BTC')
      #print(n)
    e1=time.time_ns()-s
    print(e1)

    trade = Trade(key='668aac1303b7f800017a7c33', secret='bcb25e2a-77db-4e39-85a2-4369f78edc9c', passphrase='abc,123*')
    #client2.TCP_NODELAY=1
    s=time.time_ns()
    for n in range(ns):
        res= trade.get_recent_orders()
        #print(n)
    e1=time.time_ns()-s
    print(e1)



def test_Lending():
    client1 = Lending(key='668aac1303b7f800017a7c33', secret='bcb25e2a-77db-4e39-85a2-4369f78edc9c', passphrase='abc,123*')
    #client2.TCP_NODELAY=1
    s=time.time_ns()
    ns=5
    for n in range(ns):
        res= client1.get_currency_information(currency='BTC')
        #print(n)
    e1=time.time_ns()-s
    print(e1)

    client2 = Lending(key='668aac1303b7f800017a7c33', secret='bcb25e2a-77db-4e39-85a2-4369f78edc9c', passphrase='abc,123*')
    client2.TCP_NODELAY=1
    s2=time.time_ns()
    for n in range(ns):
        res= client2.get_currency_information(currency='BTC')
        #print(res)
        #time.sleep(60)

    e2=time.time_ns()-s2
    print(f'连续请求 {ns} 次 复用:{e2}， 非复用{e1}   e2-e1:{(e2-e1)/1000000} 毫秒 如果小于0 则说明复用更快')




def test_Earn():
    #earn = Earn(key='668aac1303b7f800017a7c33', secret='bcb25e2a-77db-4e39-85a2-4369f78edc9c', passphrase='abc,123*')
    earn = Earn(key='668ab8122d2e920001dc579c', secret='77bdf571-993a-4e6d-9a64-49ea6f243a51', passphrase='1234567',url='https://openapi-v2.sit.kucoin.net')

    # res= earn.get_earn_eth_staking_products()
    # print(res)
    # res= earn.get_earn_savings_products()
    # print(res)
    # res= earn.get_earn_fixed_income_current_holdings(currency='USDT')
    # print(res)
    # res= earn.get_earn_kcs_staking_products(currency='KCS')
    # print(res)

    # res= earn.get_earn_limited_time_promotion_products(currency='ADA')
    # print(res)
    res= earn.get_earn_staking_products()
    print(res)

    # res= earn.subscribe_to_earn_fixed_income_products(productId='994',amount='10',accountType='MAIN')
    # print(res)



