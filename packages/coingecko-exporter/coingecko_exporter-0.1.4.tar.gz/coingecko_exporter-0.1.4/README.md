
# CoinGecko Exporter

CoinGecko Exporter is a Python package that allows you to fetch and export cryptocurrency data from the CoinGecko API. The data can be exported in various formats including Pandas DataFrame, SQLite, and DuckDB.

## Features

- Fetch cryptocurrency market data asynchronously.
- Retrieve historical timeseries data for multiple cryptocurrencies.
- Export data in Pandas DataFrame, SQLite, or DuckDB format.

## Installation

You can install the package using pip:

```bash
pip install coingecko-exporter
```

## Usage

Below is an example of how to use the CoinGecko Exporter package:

```python
import asyncio
from coingecko_exporter import CoinGecko as cg 

api_key = "YOUR_API_KEY"
cg = CoinGecko(api_key=api_key)

# Number of coins to fetch
coins = 3000

# Fetch data and export as DataFrame
coins_df, historical_data_df = cg.export_data(coins=coins, export_format='df')

# Export data to SQLite
cg.export_data(coins=coins, export_format='sqlite')

# Export data to DuckDB
cg.export_data(coins=coins, export_format='duckdb')

cg.get_historical_data("ethereum")
```

## API Reference

### CoinGeckoExporter

#### `__init__(self, api_key)`

Initializes the CoinGeckoExporter with the provided API key.

- `api_key`: Your CoinGecko API key.

#### `export_data(self, coins, export_format='df')`

Fetches and exports CoinGecko data.

- `coins`: Number of coins to fetch.
- `export_format`: Export format. Options are 'df', 'sqlite', or 'duckdb'. Default is 'df'.

#### `get_historical_data(self, coingecko_id: str, type: str = 'df')`

## License

This project is licensed under the MIT License.
