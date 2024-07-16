# Health

Types:

```python
from cadenza_sdk.types import HealthGetResponse
```

Methods:

- <code title="get /api/v2/health">client.health.<a href="./src/cadenza_sdk/resources/health.py">get</a>() -> str</code>

# Clients

## Info

Types:

```python
from cadenza_sdk.types.clients import InfoGetResponse
```

Methods:

- <code title="get /api/v2/client/getInfo">client.clients.info.<a href="./src/cadenza_sdk/resources/clients/info.py">get</a>() -> <a href="./src/cadenza_sdk/types/clients/info_get_response.py">InfoGetResponse</a></code>

# ExchangeAccounts

Types:

```python
from cadenza_sdk.types import (
    ExchangeAccount,
    ExchangeAccountCreateResponse,
    ExchangeAccountUpdateResponse,
    ExchangeAccountListResponse,
    ExchangeAccountRemoveResponse,
    ExchangeAccountSetExchangePriorityResponse,
)
```

Methods:

- <code title="post /api/v2/exchange/addExchangeAccount">client.exchange_accounts.<a href="./src/cadenza_sdk/resources/exchange_accounts.py">create</a>(\*\*<a href="src/cadenza_sdk/types/exchange_account_create_params.py">params</a>) -> <a href="./src/cadenza_sdk/types/exchange_account_create_response.py">ExchangeAccountCreateResponse</a></code>
- <code title="post /api/v2/exchange/updateExchangeAccount">client.exchange_accounts.<a href="./src/cadenza_sdk/resources/exchange_accounts.py">update</a>(\*\*<a href="src/cadenza_sdk/types/exchange_account_update_params.py">params</a>) -> <a href="./src/cadenza_sdk/types/exchange_account_update_response.py">ExchangeAccountUpdateResponse</a></code>
- <code title="get /api/v2/exchange/listExchangeAccounts">client.exchange_accounts.<a href="./src/cadenza_sdk/resources/exchange_accounts.py">list</a>() -> <a href="./src/cadenza_sdk/types/exchange_account_list_response.py">ExchangeAccountListResponse</a></code>
- <code title="post /api/v2/exchange/removeExchangeAccount">client.exchange_accounts.<a href="./src/cadenza_sdk/resources/exchange_accounts.py">remove</a>(\*\*<a href="src/cadenza_sdk/types/exchange_account_remove_params.py">params</a>) -> <a href="./src/cadenza_sdk/types/exchange_account_remove_response.py">ExchangeAccountRemoveResponse</a></code>
- <code title="post /api/v2/exchange/setExchangePriority">client.exchange_accounts.<a href="./src/cadenza_sdk/resources/exchange_accounts.py">set_exchange_priority</a>(\*\*<a href="src/cadenza_sdk/types/exchange_account_set_exchange_priority_params.py">params</a>) -> <a href="./src/cadenza_sdk/types/exchange_account_set_exchange_priority_response.py">ExchangeAccountSetExchangePriorityResponse</a></code>

# Market

## Instrument

Types:

```python
from cadenza_sdk.types.market import Instrument, InstrumentListResponse
```

Methods:

- <code title="get /api/v2/market/listSymbolInfo">client.market.instrument.<a href="./src/cadenza_sdk/resources/market/instrument.py">list</a>(\*\*<a href="src/cadenza_sdk/types/market/instrument_list_params.py">params</a>) -> <a href="./src/cadenza_sdk/types/market/instrument_list_response.py">InstrumentListResponse</a></code>

## Ticker

Types:

```python
from cadenza_sdk.types.market import Ticker, TickerGetResponse
```

Methods:

- <code title="get /api/v2/market/ticker">client.market.ticker.<a href="./src/cadenza_sdk/resources/market/ticker.py">get</a>(\*\*<a href="src/cadenza_sdk/types/market/ticker_get_params.py">params</a>) -> <a href="./src/cadenza_sdk/types/market/ticker_get_response.py">TickerGetResponse</a></code>

## Orderbook

Types:

```python
from cadenza_sdk.types.market import Orderbook, OrderbookGetResponse
```

Methods:

- <code title="get /api/v2/market/orderbook">client.market.orderbook.<a href="./src/cadenza_sdk/resources/market/orderbook.py">get</a>(\*\*<a href="src/cadenza_sdk/types/market/orderbook_get_params.py">params</a>) -> <a href="./src/cadenza_sdk/types/market/orderbook_get_response.py">OrderbookGetResponse</a></code>

## Kline

Types:

```python
from cadenza_sdk.types.market import Ohlcv, KlineGetResponse
```

Methods:

- <code title="get /api/v2/market/kline">client.market.kline.<a href="./src/cadenza_sdk/resources/market/kline.py">get</a>(\*\*<a href="src/cadenza_sdk/types/market/kline_get_params.py">params</a>) -> <a href="./src/cadenza_sdk/types/market/kline_get_response.py">KlineGetResponse</a></code>

# Trading

## Order

Types:

```python
from cadenza_sdk.types.trading import Order, OrderCreateResponse
```

Methods:

- <code title="post /api/v2/trading/placeOrder">client.trading.order.<a href="./src/cadenza_sdk/resources/trading/order.py">create</a>(\*\*<a href="src/cadenza_sdk/types/trading/order_create_params.py">params</a>) -> <a href="./src/cadenza_sdk/types/trading/order_create_response.py">OrderCreateResponse</a></code>
- <code title="get /api/v2/trading/listOrders">client.trading.order.<a href="./src/cadenza_sdk/resources/trading/order.py">list</a>(\*\*<a href="src/cadenza_sdk/types/trading/order_list_params.py">params</a>) -> <a href="./src/cadenza_sdk/types/trading/order.py">SyncOffset[Order]</a></code>
- <code title="post /api/v2/trading/cancelOrder">client.trading.order.<a href="./src/cadenza_sdk/resources/trading/order.py">cancel</a>(\*\*<a href="src/cadenza_sdk/types/trading/order_cancel_params.py">params</a>) -> <a href="./src/cadenza_sdk/types/trading/order.py">Order</a></code>

## Quote

Types:

```python
from cadenza_sdk.types.trading import QuoteWithOrderCandidates, QuoteRequestForQuoteResponse
```

Methods:

- <code title="post /api/v2/trading/fetchQuotes">client.trading.quote.<a href="./src/cadenza_sdk/resources/trading/quote.py">request_for_quote</a>(\*\*<a href="src/cadenza_sdk/types/trading/quote_request_for_quote_params.py">params</a>) -> <a href="./src/cadenza_sdk/types/trading/quote_request_for_quote_response.py">QuoteRequestForQuoteResponse</a></code>

## ExecutionReport

Types:

```python
from cadenza_sdk.types.trading import ExecutionReport, QuoteExecutionReport
```

Methods:

- <code title="get /api/v2/trading/listExecutionReports">client.trading.execution_report.<a href="./src/cadenza_sdk/resources/trading/execution_report.py">list</a>(\*\*<a href="src/cadenza_sdk/types/trading/execution_report_list_params.py">params</a>) -> <a href="./src/cadenza_sdk/types/trading/execution_report.py">ExecutionReport</a></code>
- <code title="get /api/v2/trading/getQuoteExecutionReport">client.trading.execution_report.<a href="./src/cadenza_sdk/resources/trading/execution_report.py">get_quote_execution_report</a>(\*\*<a href="src/cadenza_sdk/types/trading/execution_report_get_quote_execution_report_params.py">params</a>) -> <a href="./src/cadenza_sdk/types/trading/quote_execution_report.py">QuoteExecutionReport</a></code>

# Portfolio

Types:

```python
from cadenza_sdk.types import (
    ExchangeAccountBalance,
    ExchangeAccountCredit,
    ExchangeAccountPosition,
    PortfolioListBalancesResponse,
    PortfolioListCreditResponse,
    PortfolioListPositionsResponse,
)
```

Methods:

- <code title="get /api/v2/portfolio/listBalances">client.portfolio.<a href="./src/cadenza_sdk/resources/portfolio.py">list_balances</a>(\*\*<a href="src/cadenza_sdk/types/portfolio_list_balances_params.py">params</a>) -> <a href="./src/cadenza_sdk/types/portfolio_list_balances_response.py">PortfolioListBalancesResponse</a></code>
- <code title="get /api/v2/portfolio/listCredit">client.portfolio.<a href="./src/cadenza_sdk/resources/portfolio.py">list_credit</a>(\*\*<a href="src/cadenza_sdk/types/portfolio_list_credit_params.py">params</a>) -> <a href="./src/cadenza_sdk/types/portfolio_list_credit_response.py">PortfolioListCreditResponse</a></code>
- <code title="get /api/v2/portfolio/listPositions">client.portfolio.<a href="./src/cadenza_sdk/resources/portfolio.py">list_positions</a>(\*\*<a href="src/cadenza_sdk/types/portfolio_list_positions_params.py">params</a>) -> <a href="./src/cadenza_sdk/types/portfolio_list_positions_response.py">PortfolioListPositionsResponse</a></code>
