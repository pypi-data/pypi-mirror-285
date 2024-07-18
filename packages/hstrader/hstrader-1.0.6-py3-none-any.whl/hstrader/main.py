from hstrader import HsTrader

# https://hackingthemarkets.com/interactive-brokers-tws-api-tutorial/
# https://www.youtube.com/watch?v=ZEtsLuXdC-g&ab_channel=PartTimeLarry
import logging
from threading import Thread
from hstrader.models import HistoryTick, Tick

# logging.basicConfig(level=logging.DEBUG)
import pandas as pd
from lightweight_charts import Chart

USERNAME = "24100099_4117243167"
SECRET = "c3efbd1047edd3ab827d8ac315f621d6bb88c7783693abc2b0655930440ed612"

client = HsTrader(USERNAME, SECRET)

EURUSD = client.get_symbol("Bitcoin")

data = client.get_market_history(EURUSD, count_back=1000)
bars = [bar.dict() for bar in data]

df = pd.DataFrame(bars)
chart = Chart()

# Columns: time | open | high | low | close | volume

chart.set(df)


@client.subscribe("market")
def on_market(tick: Tick):

    if tick.symbol_id == EURUSD.id:
        print(tick)
        t = HistoryTick()
        t.close = tick.close
        t.open = tick.open
        t.high = tick.high
        t.low = tick.low
        t.volume = tick.volume
        t.time = tick.time

        df.loc[len(df)] = t.dict()

        print(df["time"].name)
        chart.set(df)


if __name__ == "__main__":

    websocket_thread = Thread(
        target=client.start,
        daemon=True,
    )
    websocket_thread.start()

    chart.show(block=True)
