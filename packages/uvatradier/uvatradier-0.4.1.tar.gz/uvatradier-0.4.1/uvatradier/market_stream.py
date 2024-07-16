from .base import Tradier
import os, dotenv;
import requests;
import time;

import asyncio;
import websockets;
import json;


class MarketStream (Tradier):
	def __init__ (self, account_number, auth_token):
		Tradier.__init__(self, account_number, auth_token);

		self.STREAM_SESSION_ENDPOINT = 'v1/markets/events/session';
		self.MARKET_STREAM_ENDPOINT = 'v1/markets/events';