import time

from kucoin_futures.client import Trade




def test_Lending():
    client1 = Trade(key='668aac1303b7f800017a7c33', secret='bcb25e2a-77db-4e39-85a2-4369f78edc9c', passphrase='abc,123*')
    #client2.TCP_NODELAY=1
    s=time.time_ns()
    ns=5
    for n in range(ns):
      res= client1.get_24h_done_order()
      #print(n)
    e1=time.time_ns()-s
    print(e1)
