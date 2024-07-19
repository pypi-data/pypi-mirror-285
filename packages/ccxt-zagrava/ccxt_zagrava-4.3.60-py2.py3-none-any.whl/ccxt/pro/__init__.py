# -*- coding: utf-8 -*-

"""ccxt_zagrava: CryptoCurrency eXchange Trading Library (Async)"""

# ----------------------------------------------------------------------------

__version__ = '4.3.62'

# ----------------------------------------------------------------------------

from ccxt_zagrava.async_support.base.exchange import Exchange  # noqa: F401

# ccxt_zagrava Pro exchanges (now this is mainly used for importing exchanges in WS tests)

from ccxt_zagrava.pro.alpaca import alpaca                                        # noqa: F401
from ccxt_zagrava.pro.ascendex import ascendex                                    # noqa: F401
from ccxt_zagrava.pro.bequant import bequant                                      # noqa: F401
from ccxt_zagrava.pro.binance import binance                                      # noqa: F401
from ccxt_zagrava.pro.binancecoinm import binancecoinm                            # noqa: F401
from ccxt_zagrava.pro.binanceus import binanceus                                  # noqa: F401
from ccxt_zagrava.pro.binanceusdm import binanceusdm                              # noqa: F401
from ccxt_zagrava.pro.bingx import bingx                                          # noqa: F401
from ccxt_zagrava.pro.bitcoincom import bitcoincom                                # noqa: F401
from ccxt_zagrava.pro.bitfinex import bitfinex                                    # noqa: F401
from ccxt_zagrava.pro.bitfinex2 import bitfinex2                                  # noqa: F401
from ccxt_zagrava.pro.bitget import bitget                                        # noqa: F401
from ccxt_zagrava.pro.bithumb import bithumb                                      # noqa: F401
from ccxt_zagrava.pro.bitmart import bitmart                                      # noqa: F401
from ccxt_zagrava.pro.bitmex import bitmex                                        # noqa: F401
from ccxt_zagrava.pro.bitopro import bitopro                                      # noqa: F401
from ccxt_zagrava.pro.bitpanda import bitpanda                                    # noqa: F401
from ccxt_zagrava.pro.bitrue import bitrue                                        # noqa: F401
from ccxt_zagrava.pro.bitstamp import bitstamp                                    # noqa: F401
from ccxt_zagrava.pro.bitvavo import bitvavo                                      # noqa: F401
from ccxt_zagrava.pro.blockchaincom import blockchaincom                          # noqa: F401
from ccxt_zagrava.pro.bybit import bybit                                          # noqa: F401
from ccxt_zagrava.pro.cex import cex                                              # noqa: F401
from ccxt_zagrava.pro.coinbase import coinbase                                    # noqa: F401
from ccxt_zagrava.pro.coinbaseexchange import coinbaseexchange                    # noqa: F401
from ccxt_zagrava.pro.coinbaseinternational import coinbaseinternational          # noqa: F401
from ccxt_zagrava.pro.coincheck import coincheck                                  # noqa: F401
from ccxt_zagrava.pro.coinex import coinex                                        # noqa: F401
from ccxt_zagrava.pro.coinone import coinone                                      # noqa: F401
from ccxt_zagrava.pro.cryptocom import cryptocom                                  # noqa: F401
from ccxt_zagrava.pro.currencycom import currencycom                              # noqa: F401
from ccxt_zagrava.pro.deribit import deribit                                      # noqa: F401
from ccxt_zagrava.pro.exmo import exmo                                            # noqa: F401
from ccxt_zagrava.pro.gate import gate                                            # noqa: F401
from ccxt_zagrava.pro.gateio import gateio                                        # noqa: F401
from ccxt_zagrava.pro.gemini import gemini                                        # noqa: F401
from ccxt_zagrava.pro.hitbtc import hitbtc                                        # noqa: F401
from ccxt_zagrava.pro.hollaex import hollaex                                      # noqa: F401
from ccxt_zagrava.pro.htx import htx                                              # noqa: F401
from ccxt_zagrava.pro.huobi import huobi                                          # noqa: F401
from ccxt_zagrava.pro.huobijp import huobijp                                      # noqa: F401
from ccxt_zagrava.pro.hyperliquid import hyperliquid                              # noqa: F401
from ccxt_zagrava.pro.idex import idex                                            # noqa: F401
from ccxt_zagrava.pro.independentreserve import independentreserve                # noqa: F401
from ccxt_zagrava.pro.kraken import kraken                                        # noqa: F401
from ccxt_zagrava.pro.krakenfutures import krakenfutures                          # noqa: F401
from ccxt_zagrava.pro.kucoin import kucoin                                        # noqa: F401
from ccxt_zagrava.pro.kucoinfutures import kucoinfutures                          # noqa: F401
from ccxt_zagrava.pro.lbank import lbank                                          # noqa: F401
from ccxt_zagrava.pro.luno import luno                                            # noqa: F401
from ccxt_zagrava.pro.mexc import mexc                                            # noqa: F401
from ccxt_zagrava.pro.ndax import ndax                                            # noqa: F401
from ccxt_zagrava.pro.okcoin import okcoin                                        # noqa: F401
from ccxt_zagrava.pro.okx import okx                                              # noqa: F401
from ccxt_zagrava.pro.onetrading import onetrading                                # noqa: F401
from ccxt_zagrava.pro.oxfun import oxfun                                          # noqa: F401
from ccxt_zagrava.pro.p2b import p2b                                              # noqa: F401
from ccxt_zagrava.pro.phemex import phemex                                        # noqa: F401
from ccxt_zagrava.pro.poloniex import poloniex                                    # noqa: F401
from ccxt_zagrava.pro.poloniexfutures import poloniexfutures                      # noqa: F401
from ccxt_zagrava.pro.probit import probit                                        # noqa: F401
from ccxt_zagrava.pro.upbit import upbit                                          # noqa: F401
from ccxt_zagrava.pro.vertex import vertex                                        # noqa: F401
from ccxt_zagrava.pro.wazirx import wazirx                                        # noqa: F401
from ccxt_zagrava.pro.whitebit import whitebit                                    # noqa: F401
from ccxt_zagrava.pro.woo import woo                                              # noqa: F401
from ccxt_zagrava.pro.woofipro import woofipro                                    # noqa: F401
from ccxt_zagrava.pro.xt import xt                                                # noqa: F401

exchanges = [
    'alpaca',
    'ascendex',
    'bequant',
    'binance',
    'binancecoinm',
    'binanceus',
    'binanceusdm',
    'bingx',
    'bitcoincom',
    'bitfinex',
    'bitfinex2',
    'bitget',
    'bithumb',
    'bitmart',
    'bitmex',
    'bitopro',
    'bitpanda',
    'bitrue',
    'bitstamp',
    'bitvavo',
    'blockchaincom',
    'bybit',
    'cex',
    'coinbase',
    'coinbaseexchange',
    'coinbaseinternational',
    'coincheck',
    'coinex',
    'coinone',
    'cryptocom',
    'currencycom',
    'deribit',
    'exmo',
    'gate',
    'gateio',
    'gemini',
    'hitbtc',
    'hollaex',
    'htx',
    'huobi',
    'huobijp',
    'hyperliquid',
    'idex',
    'independentreserve',
    'kraken',
    'krakenfutures',
    'kucoin',
    'kucoinfutures',
    'lbank',
    'luno',
    'mexc',
    'ndax',
    'okcoin',
    'okx',
    'onetrading',
    'oxfun',
    'p2b',
    'phemex',
    'poloniex',
    'poloniexfutures',
    'probit',
    'upbit',
    'vertex',
    'wazirx',
    'whitebit',
    'woo',
    'woofipro',
    'xt',
]
