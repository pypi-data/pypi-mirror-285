import httpx
from botframework.cex_proxy import CEXProxy
from datetime import datetime, timedelta
import logging
import asyncio
import websockets
import uuid
import json
import os


logger = logging.getLogger('app')


class MarketMgr:
    """Price and Candle Manager"""
    
       
    def get_market_data_service_url_ws(self) -> str:
        return os.getenv("TKS_MARKET_DATA_SERVICE_API_WS", "ws://localhost:8400")
        
    def get_market_data_service_url_http(self) -> str:
        return os.getenv("TKS_MARKET_DATA_SERVICE_API_HTTP", "http://localhost:8400/")

    async def get_real_time_data(self, markets, callback, max_retries=6, short_interval=10, long_interval=600):
        # Ensure markets is a list
        if isinstance(markets, str):
            markets = [markets]
        logger.info(f"Starting to listen for real-time market data for {markets}.")
        
        uri = f"{self.get_market_data_service_url_ws()}/stream/price"
        retry_count = 0
        initial_retries = max_retries  # Store initial max_retries value

        while True:
            try:
                async with websockets.connect(uri) as websocket:
                    # Construct and send the market watch request message
                    message = {
                        "client_id": str(uuid.uuid4()),
                        "watch_type": "real-time",
                        "action": "request",
                        "markets": [market.upper() for market in markets]
                    }
                    await websocket.send(json.dumps(message))
                    # Continuously listen for and process market data updates
                    while True:
                        try:
                            response = await websocket.recv()
                            data = json.loads(response)
                            try:
                                await callback(data)
                            except Exception as e:
                                logger.error(f"Error in callback: {e}, Data: {data}")
                        except websockets.ConnectionClosed as e:
                            logger.error(f"WebSocket connection closed: {e}")
                            break
                        except asyncio.TimeoutError:
                            logger.error("Timeout error while waiting for WebSocket data")
                        except json.JSONDecodeError as e:
                            logger.error(f"JSON decode error: {e}")
                        except Exception as e:
                            logger.error(f"Exception while receiving WebSocket data: {e}")
            except Exception as e:
                logger.error(f"WebSocket connection error: {e}")
                if "WinError 1225" in str(e):
                    logger.error("The WebSocket is not available. The remote computer refused the network connection.")
                
                retry_count += 1
                if retry_count <= initial_retries:
                    retry_interval = short_interval
                    if retry_count < initial_retries:
                        logger.info(f"WebSocket connection currently unavailable, not able to fetch real-time data. Retrying in {retry_interval} seconds...")
                    else:
                        logger.info(f"WebSocket connection currently unavailable, switching to retry every {long_interval / 60} minutes.")
                else:
                    retry_interval = long_interval
                    logger.info(f"WebSocket connection currently unavailable, not able to fetch real-time data. Retrying in {retry_interval / 60} minutes...")

                await asyncio.sleep(retry_interval)

    async def get_last_price(self, market, exchange=None):
        # This method expects the "market" argument in the shape "ETH-USDT".
        """Returns the last close price from the market and the desired exchange (if specified)."""
        url = f"{self.get_market_data_service_url_http()}price/{market.upper()}"
        if exchange:
            url += f"?exchange={exchange}"  # Use query parameter for optional 'exchange'
        async with httpx.AsyncClient() as client:
            async with client.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('price')
                else:
                    logger.error(f"Failed to fetch last price: {response.status} {response.reason}")
                    return None

    async def get_historical_data(self, exchange, market_symbol, timeframe, limit=1000):
        try:
            cex_proxy = CEXProxy()
            ccxt_exchange = await cex_proxy.get_exchange_proxy(exchange)
            if limit <= 1000:
                since = None
                return await ccxt_exchange.fetch_ohlcv(symbol=market_symbol, timeframe=timeframe, since=since, limit=limit)            
            elif limit > 1000:
                if timeframe=="1m":
                    start_date = datetime.now() - timedelta(hours=limit/60)
                elif timeframe=="5m":
                    start_date = datetime.now() - timedelta(hours=limit/12)
                elif timeframe=="15m":
                    start_date = datetime.now() - timedelta(hours=limit/4)
                elif timeframe=="1h":
                    start_date = datetime.now() - timedelta(hours=limit)
                elif timeframe=="4h":
                    start_date = datetime.now() - timedelta(hours=limit*4)
                elif timeframe=="6h":
                    start_date = datetime.now() - timedelta(hours=limit*6)
                elif timeframe=="1d":
                    start_date = datetime.now() - timedelta(hours=limit*24)
                elif timeframe=="1w":
                    start_date = datetime.now() - timedelta(hours=limit*24*7)
              
                start_date = str(start_date.replace(minute=0, second=0, microsecond=0))
                start_date_parsed = ccxt_exchange.parse8601(start_date)
                ohlcv = await ccxt_exchange.fetch_ohlcv(symbol=market_symbol, timeframe=timeframe, since=start_date_parsed, limit=limit)  
                while True:
                    start_date_parsed = ohlcv[-1][0]
                    new_ohlcv = await ccxt_exchange.fetch_ohlcv(symbol=market_symbol, timeframe=timeframe, since=start_date_parsed, limit=limit)  
                    new_ohlcv.pop(0)
                    new_ohlcv
                    ohlcv.extend(new_ohlcv)
                    await asyncio.sleep(0.25)
                    if len(new_ohlcv) != (1000 - 1):
                        break
                return ohlcv
        except Exception as ex:
            await ccxt_exchange.close()
            raise Exception(f"Failed to fetch historical OHLCV data. {ex}")
        finally:
            await ccxt_exchange.close()  
    
    async def get_meta_market_indicator_data(self, callback):
        url = f"{self.get_market_data_service_url_ws()}/tv/meta_market_indicator"
        try:
            async with websockets.connect(url) as websocket:
                while True:  # Loop to keep connection open
                    response = await websocket.recv()
                    data = json.loads(response)
                    logger.info(f"Processing incoming Meta Market Indicator data: {data}")
                    await callback(data)
                    # Handle data here rather than returning immediately
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
 
        

