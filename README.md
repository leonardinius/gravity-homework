# README

## How-to try it out locally

###  Configuration

- Copy `.env.example` to `.env`
- Provide `BINANCE_API_KEY` and `BINANCE_API_SECRET`

### How to execute locally

```shell
python3 -m venv venv
source venv/bin/activate
python setup.py install
pip install -r requirements.txt
pip install -e '.[tests]'

# to run tests
./venv/bin/pytest 

cd src/homework && python main.py
```

Example output
```
2021-10-25 09:44:01,511 - INFO - Symbol pair: BTCUSDT
2021-10-25 09:44:01,511 - INFO - Please wait approximately 10 seconds
2021-10-25 09:44:12,403 - ERROR - bet={bid=62004.44 ask=62004.45} // best={bid=62000.04000000 ask=62000.05000000}
2021-10-25 09:44:22,482 - ERROR - bet={bid=62004.44 ask=62004.45} // best={bid=62000.04000000 ask=62000.05000000}
2021-10-25 09:44:32,585 - ERROR - bet={bid=62006.07 ask=62006.08} // best={bid=62001.67000000 ask=62001.68000000}
2021-10-25 09:44:42,695 - ERROR - bet={bid=62032.41 ask=62032.42} // best={bid=62028.01000000 ask=62028.02000000}
2021-10-25 09:44:52,843 - ERROR - bet={bid=62052.85 ask=62048.11} // best={bid=62048.44000000 ask=62048.45000000}
```
bet - calculate at what price you should place an order, so that with 50% probability it would be filled in next 10 seconds.
best - best bid, best ask price

## Solution

### Assumptions

- We can ignore bet order quantity, it is sufficient if order will be matched partially.
- Market is efficient and most of the trades will concentrate around min spread.
- For the scope of this homework: The BTC/USDT pair is the active pair and there is enough activity to not worry about idle periods.
- For the scope of this homework: the static price increment ratios are good enough to demonstrate the approach and intent. 

### High Level algorithm description

- The approach is pretty much bruteforce, based on monte carlo simulation principle.  
- I start to observe market in the mainapp for ticker price changes and real time trades.
- I use the sliding time window for last N (configurable) seconds and place "bet orders" with different "depth ratio"
  (price change coefficient) to place an order with.
  "Depth ratio" - is a term I used across the homework and description, most likely wrong one. 
- Within the time window, app regularly places the "bet" (simulation) orders with different "depth ratio" adjusted prices 
  and monitor the real time trades to mark these bet orders as executed or not.
- For regular 10sec report, 
  - app calculates the percentiles of executed "depth ratio" orders and use the threshold of 50%.
  - app uses the current price market and 50% threshold "depth ratio" to calculate bid and ask prices for the report.  

### Algorithm critics

- In efficient market the majority of trades focus around minimal spread. The static threshold, static "depth ratio"
  bruteforce value probabilities tend to cluster around minimal price change (0.01 in BTC/USDT pair).
  The more dynamic "depth ratio" selection algorithm is needed for real life application.
- Alternative approach to consider, which I have not had time to experiment more - to use plain price deltas, 
  not coefficients, to some sort of log scale and place bets accordingly.
  E.g. 0.01, 0.02, 0.03, .., 0.10, 0.13, 0.15, 0.20,...
- Time/space complexity of the algorithm is high. 
  E.g. for 10 seconds of market observation, for each simulation tick, N bet simulation orders. 
  The more time it takes to process, the more is probability of us missing price/trade updates from Binance WS. 


### Not finished parts

- Monitoring of efficiency of algorithm and self-correcting feedback loop.
  E.g. every 10 seconds I report what is the values which should be used. 
  What I could do - for the next 10 seconds monitor and check if the "bet" placement worked out. If not, that could be 
  used as a signal either to adjust the algorithm/model, or stop the system after the threshold of errors is recorded.    
- Monitoring of the solution performance, e.g. backpressure on Binance WS API. There is a chance some updates are 
  missing and ignored. 
- Handling of market idle periods (unlikely) or Network issues(more likely). E.g. handling cases when the system does 
  not get updates from Binance WS API for some period of time due to network or similar issues.
- Tests: reporting part, the bet placing ranges, price calculations, etc... 
  The classic pyramid of tests: unit tests, integration tests, system tests.
  The tests included are way too few to reliably maintain the system over the time. 
- ... Much, much more on adjusting the algorithm, feedback cycle and operations.  

---

# Gravity team coding task 

## Description.

- Use binance rest and/or websocket api.
- Keep track of BTC/USDT pair.
- For both sides (bid and ask) calculate at what price you should place an order, so that with 50% probability it would be filled in next 10 seconds.
- Each 10 seconds print out these prices and best bid, best ask price.
- Use python language.
- Add tests.

## What gets evaluated.

- Algorithm efficiency.
- Algorithm correctness.
- Code cleanness.

## How to submit solution.

Create a git repo. Archive project together with git history. Send it in this conversation.
