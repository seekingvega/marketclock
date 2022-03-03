# MarketClock

knowing when the market is open is non-trival! You can pay for services like [market-clock](https://www.market-clock.com/) or [TradingHours.com](https://www.tradinghours.com/markets/hkex/hours) because trading holidays and hours do change!

But thankfully, there's [`pandas_market_calendars`](https://github.com/rsheftel/pandas_market_calendars) but if you are not familiar with python or pandas, then this might not be accessible to you! That's why we created `marketclock` as a python package and a free API so that we can all know when a market is closed or open!

## Usage
### List of Exchange: https://marketclock.herokuapp.com/exchanges
### Check your exchange
Exchange names are case sensitive. Using `HKEX` as an example, query https://marketclock.herokuapp.com/exchanges/HKEX
