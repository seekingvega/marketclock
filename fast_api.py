import os, sys, json, datetime
from fastapi import FastAPI, File, UploadFile, Request, Response, HTTPException
from typing import List, Tuple, Union
from pydantic import BaseModel

app_version = 0.02
b_add_app_name = os.getenv("ADD_APP_NAME", 'False').lower() in ['true', '1', 't']
app_name = '/marketclock' if b_add_app_name else '' # This is for applications routing with $uri in ngnix config
app = FastAPI(
	title = 'marketclock API',
	description = "free API to check market status",
	version = app_version,
	docs_url = f'{app_name}/docs', redoc_url = None,
	openapi_url = f'{app_name}/openapi.json'
)

class MarketClockResult(BaseModel):
	exchange_name: str
	exchange_timezone: str
	ref_date_time: datetime.datetime
	ref_date: datetime.date
	is_trading_day: bool
	status: str
	next_trading_date: datetime.date
	previous_trading_date: datetime.date
	coming_event: str
	status_img_url: str
	market_schedule: dict

from main import Main, get_avail_exchanges

@app.get(app_name +"/exchanges/{exchange}",
	response_model = Union[MarketClockResult,dict], response_model_exclude_unset = True)
async def check_by_exchange(exchange: str):
	'''check the trading status of your exchange

	* `exchange_name`: must be a valid exchange name (see `/exchanges` endpoint)
	'''
	return Main(exchange_name = exchange, datetime_obj= datetime.datetime.now())

@app.get(f"{app_name}/exchanges")
def get_exchanges():
	return get_avail_exchanges()

@app.get(f"{app_name}" if app_name else '/')
def read_root():
	return {"MarketClock API": app_version,
			'status': 'Healthy',
			'message': f'see {app_name}/docs/ endpoint for help',
			}
