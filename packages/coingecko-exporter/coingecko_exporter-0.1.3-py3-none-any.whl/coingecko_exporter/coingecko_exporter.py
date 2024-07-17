import httpx
import asyncio
import logging
import pandas as pd
import sqlite3
import duckdb
from aiolimiter import AsyncLimiter
import requests 

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CoinGecko:
    def __init__(self, api_key: str, rate_limit = 500):
        """
        Initialize CoinGecko with API key.
        
        :param api_key: CoinGecko API key
        """
        self.api_key = api_key
        self.base_url = "https://pro-api.coingecko.com/api/v3"
        self.limiter = AsyncLimiter(rate_limit, 60)

    async def fetch_page_data(self, client: httpx.AsyncClient, params: dict, page: int) -> dict:
        """ Fetches a single page of data asynchronously. """
        try:
            response = await client.get(f"{self.base_url}/coins/markets", params={**params, "page": page}, timeout=10)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logging.error(f"HTTP error occurred: {e.response.status_code}")
        except httpx.RequestError as e:
            logging.error(f"Request error occurred: {e}")
        except Exception as e:
            logging.error(f"An error occurred: {e}")
        return None

    async def get_all_pages(self, params: dict, max_pages: int) -> list:
        """ Retrieves all pages of data asynchronously. """
        async with httpx.AsyncClient() as client:
            tasks = [self.fetch_page_data(client, params, page) for page in range(1, max_pages + 1)]
            results = await asyncio.gather(*tasks)
            all_results = [item for sublist in results for item in sublist if sublist]
            return all_results

    async def get_coins(self, coins: int) -> pd.DataFrame:
        """
        Gets full list of assets from CoinGecko API asynchronously.
        
        :param coins: Number of top coins by market cap to fetch
        :return: DataFrame with coin data
        """
        if coins <= 250:
            pages = 1
            per_page = coins
        else:
            per_page = 250
            pages = coins // 250 + (0 if coins % 250 == 0 else 1)

        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": per_page,
            "sparkline": False,
            "locale": "en",
            "x_cg_pro_api_key": self.api_key,
        }

        data = await self.get_all_pages(params, pages)

        df = pd.DataFrame(data)
        df.drop(columns=['roi'], inplace=True)
        df.rename(columns={"id": "coingecko_id"}, inplace=True)
        return df

    async def fetch_timeseries_data(self, client: httpx.AsyncClient, coingecko_id: str) -> pd.DataFrame:
        """Asynchronously fetches historical timeseries data from the Coingecko API with shared rate limit handling."""
        
        url = f"{self.base_url}/coins/{coingecko_id}/market_chart"
        params = {
            "vs_currency": "usd",
            "days": "max",
            "interval": "daily",
            "x_cg_pro_api_key": self.api_key
        }
        retries = 0
        while retries < 10:
            try:
                await self.limiter.acquire()
                response = await client.get(url, params=params, timeout=10)
                response.raise_for_status()
                return self.clean_timeseries_data(response.json(), coingecko_id)
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    retries += 1
                    await asyncio.sleep(30 + retries * 5)
                else:
                    logging.error(f"HTTP error for {coingecko_id}: {e.response.status_code}")
                    return None
            except Exception as e:
                logging.error(f"Error fetching data for {coingecko_id}: {e}")
                return None
        logging.error(f"Exceeded maximum retries for {coingecko_id}.")
        return None

    def clean_timeseries_data(self, data: dict, coingecko_id: str) -> pd.DataFrame:
        """Cleans and transforms raw JSON timeseries data into a DataFrame."""
        if not data:
            return pd.DataFrame()
        prices = pd.DataFrame(data['prices'], columns=['date', 'price'])
        market_cap = pd.DataFrame(data['market_caps'], columns=['date', 'market_cap'])
        volume = pd.DataFrame(data['total_volumes'], columns=['date', 'volume'])
        merged_df = prices.merge(market_cap, on='date').merge(volume, on='date')
        merged_df['date'] = pd.to_datetime(merged_df['date'], unit='ms')
        merged_df['coingecko_id'] = coingecko_id
        return merged_df

    async def get_historical_data(self, coingecko_ids: list) -> pd.DataFrame:
        async with httpx.AsyncClient() as client:
            tasks = [self.fetch_timeseries_data(client, coingecko_id) for coingecko_id in coingecko_ids]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            results = [result for result in results if result is not None]
            return pd.concat(results)
        
    def export_data(self, coins: int, export_format: str = 'df'):
        """
        Main method to fetch and export CoinGecko data.
        
        :param coins: Number of top coins by market cap to fetch
        :param export_format: Export format ('df', 'sqlite', 'duckdb', or 'parquet')
        :return: DataFrame(s) if export_format is 'df', else None
        """
        coins_df = asyncio.run(self.get_coins(coins))
        historical_data_df = asyncio.run(self.get_historical_data(coins_df["coingecko_id"].tolist()))

        if export_format == 'df':
            return coins_df, historical_data_df
        elif export_format == 'sqlite':
            conn = sqlite3.connect("coingecko_data.sqlite")
            coins_df.to_sql("coins", conn, if_exists="replace", index=False)
            historical_data_df.to_sql("historical_data", conn, if_exists="replace", index=False)
            conn.close()
        elif export_format == 'duckdb':
            conn = duckdb.connect("coingecko_data.duckdb")
            conn.execute("CREATE OR REPLACE TABLE coins AS SELECT * FROM coins_df")
            conn.execute("CREATE OR REPLACE TABLE historical_data AS SELECT * FROM historical_data_df")
            conn.close()
        elif export_format == 'parquet':
            coins_df.to_parquet("coins.parquet", index=False)
            historical_data_df.to_parquet("historical_data.parquet", index=False)
        else:
            raise ValueError("Invalid export format. Choose 'df', 'sqlite', 'duckdb', or 'parquet'.")

    def get_historical_data(self, coingecko_id: str, type: str = 'df') -> pd.DataFrame:
        """
        Fetches the historical data of a crypto asset. 
        """
        url = f"https://pro-api.coingecko.com/api/v3/coins/{coingecko_id}/market_chart"

        params = {
            "vs_currency": "usd",
            "days": "max",
            "interval": "daily",
            "x_cg_pro_api_key": self.api_key
        }
        data = requests.get(url, params=params).json()

        prices = pd.DataFrame(data['prices'], columns=['date', 'price'])
        market_cap = pd.DataFrame(data['market_caps'], columns=['date', 'market_cap'])
        volume = pd.DataFrame(data['total_volumes'], columns=['date', 'volume'])
        merged_df = prices.merge(market_cap, on='date').merge(volume, on='date')
        merged_df['date'] = pd.to_datetime(merged_df['date'], unit='ms').dt.normalize()

        if type == 'df':
            return merged_df
        elif type == 'dict' or type == 'json':
            return merged_df.to_dict(orient='records')
        

if __name__ == "__main__":
    import os
    cg = CoinGecko(api_key="CG-api-key")
    coins = 1000
    data = cg.export_data(coins, export_format='parquet')
