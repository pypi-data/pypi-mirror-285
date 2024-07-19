# -*- coding: utf-8 -*-

"""ccxt_zagrava: CryptoCurrency eXchange Trading Library"""

# MIT License
# Copyright (c) 2017 Igor Kroitor
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# ----------------------------------------------------------------------------

__version__ = '4.3.62'

# ----------------------------------------------------------------------------

from ccxt_zagrava.base.exchange import Exchange                     # noqa: F401
from ccxt_zagrava.base.precise import Precise                       # noqa: F401

from ccxt_zagrava.base.decimal_to_precision import decimal_to_precision  # noqa: F401
from ccxt_zagrava.base.decimal_to_precision import TRUNCATE              # noqa: F401
from ccxt_zagrava.base.decimal_to_precision import ROUND                 # noqa: F401
from ccxt_zagrava.base.decimal_to_precision import ROUND_UP              # noqa: F401
from ccxt_zagrava.base.decimal_to_precision import ROUND_DOWN            # noqa: F401
from ccxt_zagrava.base.decimal_to_precision import DECIMAL_PLACES        # noqa: F401
from ccxt_zagrava.base.decimal_to_precision import SIGNIFICANT_DIGITS    # noqa: F401
from ccxt_zagrava.base.decimal_to_precision import TICK_SIZE             # noqa: F401
from ccxt_zagrava.base.decimal_to_precision import NO_PADDING            # noqa: F401
from ccxt_zagrava.base.decimal_to_precision import PAD_WITH_ZERO         # noqa: F401

from ccxt_zagrava.base import errors
from ccxt_zagrava.base.errors import BaseError                                # noqa: F401
from ccxt_zagrava.base.errors import ExchangeError                            # noqa: F401
from ccxt_zagrava.base.errors import AuthenticationError                      # noqa: F401
from ccxt_zagrava.base.errors import PermissionDenied                         # noqa: F401
from ccxt_zagrava.base.errors import AccountNotEnabled                        # noqa: F401
from ccxt_zagrava.base.errors import AccountSuspended                         # noqa: F401
from ccxt_zagrava.base.errors import ArgumentsRequired                        # noqa: F401
from ccxt_zagrava.base.errors import BadRequest                               # noqa: F401
from ccxt_zagrava.base.errors import BadSymbol                                # noqa: F401
from ccxt_zagrava.base.errors import OperationRejected                        # noqa: F401
from ccxt_zagrava.base.errors import NoChange                                 # noqa: F401
from ccxt_zagrava.base.errors import MarginModeAlreadySet                     # noqa: F401
from ccxt_zagrava.base.errors import MarketClosed                             # noqa: F401
from ccxt_zagrava.base.errors import InsufficientFunds                        # noqa: F401
from ccxt_zagrava.base.errors import InvalidAddress                           # noqa: F401
from ccxt_zagrava.base.errors import AddressPending                           # noqa: F401
from ccxt_zagrava.base.errors import InvalidOrder                             # noqa: F401
from ccxt_zagrava.base.errors import OrderNotFound                            # noqa: F401
from ccxt_zagrava.base.errors import OrderNotCached                           # noqa: F401
from ccxt_zagrava.base.errors import OrderImmediatelyFillable                 # noqa: F401
from ccxt_zagrava.base.errors import OrderNotFillable                         # noqa: F401
from ccxt_zagrava.base.errors import DuplicateOrderId                         # noqa: F401
from ccxt_zagrava.base.errors import ContractUnavailable                      # noqa: F401
from ccxt_zagrava.base.errors import NotSupported                             # noqa: F401
from ccxt_zagrava.base.errors import InvalidProxySettings                     # noqa: F401
from ccxt_zagrava.base.errors import ExchangeClosedByUser                     # noqa: F401
from ccxt_zagrava.base.errors import OperationFailed                          # noqa: F401
from ccxt_zagrava.base.errors import NetworkError                             # noqa: F401
from ccxt_zagrava.base.errors import DDoSProtection                           # noqa: F401
from ccxt_zagrava.base.errors import RateLimitExceeded                        # noqa: F401
from ccxt_zagrava.base.errors import ExchangeNotAvailable                     # noqa: F401
from ccxt_zagrava.base.errors import OnMaintenance                            # noqa: F401
from ccxt_zagrava.base.errors import InvalidNonce                             # noqa: F401
from ccxt_zagrava.base.errors import RequestTimeout                           # noqa: F401
from ccxt_zagrava.base.errors import BadResponse                              # noqa: F401
from ccxt_zagrava.base.errors import NullResponse                             # noqa: F401
from ccxt_zagrava.base.errors import CancelPending                            # noqa: F401
from ccxt_zagrava.base.errors import error_hierarchy                          # noqa: F401

from ccxt_zagrava.ace import ace                                              # noqa: F401
from ccxt_zagrava.alpaca import alpaca                                        # noqa: F401
from ccxt_zagrava.ascendex import ascendex                                    # noqa: F401
from ccxt_zagrava.bequant import bequant                                      # noqa: F401
from ccxt_zagrava.bigone import bigone                                        # noqa: F401
from ccxt_zagrava.binance import binance                                      # noqa: F401
from ccxt_zagrava.binancecoinm import binancecoinm                            # noqa: F401
from ccxt_zagrava.binanceus import binanceus                                  # noqa: F401
from ccxt_zagrava.binanceusdm import binanceusdm                              # noqa: F401
from ccxt_zagrava.bingx import bingx                                          # noqa: F401
from ccxt_zagrava.bit2c import bit2c                                          # noqa: F401
from ccxt_zagrava.bitbank import bitbank                                      # noqa: F401
from ccxt_zagrava.bitbay import bitbay                                        # noqa: F401
from ccxt_zagrava.bitbns import bitbns                                        # noqa: F401
from ccxt_zagrava.bitcoincom import bitcoincom                                # noqa: F401
from ccxt_zagrava.bitfinex import bitfinex                                    # noqa: F401
from ccxt_zagrava.bitfinex2 import bitfinex2                                  # noqa: F401
from ccxt_zagrava.bitflyer import bitflyer                                    # noqa: F401
from ccxt_zagrava.bitget import bitget                                        # noqa: F401
from ccxt_zagrava.bithumb import bithumb                                      # noqa: F401
from ccxt_zagrava.bitmart import bitmart                                      # noqa: F401
from ccxt_zagrava.bitmex import bitmex                                        # noqa: F401
from ccxt_zagrava.bitopro import bitopro                                      # noqa: F401
from ccxt_zagrava.bitpanda import bitpanda                                    # noqa: F401
from ccxt_zagrava.bitrue import bitrue                                        # noqa: F401
from ccxt_zagrava.bitso import bitso                                          # noqa: F401
from ccxt_zagrava.bitstamp import bitstamp                                    # noqa: F401
from ccxt_zagrava.bitteam import bitteam                                      # noqa: F401
from ccxt_zagrava.bitvavo import bitvavo                                      # noqa: F401
from ccxt_zagrava.bl3p import bl3p                                            # noqa: F401
from ccxt_zagrava.blockchaincom import blockchaincom                          # noqa: F401
from ccxt_zagrava.blofin import blofin                                        # noqa: F401
from ccxt_zagrava.btcalpha import btcalpha                                    # noqa: F401
from ccxt_zagrava.btcbox import btcbox                                        # noqa: F401
from ccxt_zagrava.btcmarkets import btcmarkets                                # noqa: F401
from ccxt_zagrava.btcturk import btcturk                                      # noqa: F401
from ccxt_zagrava.bybit import bybit                                          # noqa: F401
from ccxt_zagrava.cex import cex                                              # noqa: F401
from ccxt_zagrava.coinbase import coinbase                                    # noqa: F401
from ccxt_zagrava.coinbaseadvanced import coinbaseadvanced                    # noqa: F401
from ccxt_zagrava.coinbaseexchange import coinbaseexchange                    # noqa: F401
from ccxt_zagrava.coinbaseinternational import coinbaseinternational          # noqa: F401
from ccxt_zagrava.coincheck import coincheck                                  # noqa: F401
from ccxt_zagrava.coinex import coinex                                        # noqa: F401
from ccxt_zagrava.coinlist import coinlist                                    # noqa: F401
from ccxt_zagrava.coinmate import coinmate                                    # noqa: F401
from ccxt_zagrava.coinmetro import coinmetro                                  # noqa: F401
from ccxt_zagrava.coinone import coinone                                      # noqa: F401
from ccxt_zagrava.coinsph import coinsph                                      # noqa: F401
from ccxt_zagrava.coinspot import coinspot                                    # noqa: F401
from ccxt_zagrava.cryptocom import cryptocom                                  # noqa: F401
from ccxt_zagrava.currencycom import currencycom                              # noqa: F401
from ccxt_zagrava.delta import delta                                          # noqa: F401
from ccxt_zagrava.deribit import deribit                                      # noqa: F401
from ccxt_zagrava.digifinex import digifinex                                  # noqa: F401
from ccxt_zagrava.exmo import exmo                                            # noqa: F401
from ccxt_zagrava.fmfwio import fmfwio                                        # noqa: F401
from ccxt_zagrava.gate import gate                                            # noqa: F401
from ccxt_zagrava.gateio import gateio                                        # noqa: F401
from ccxt_zagrava.gemini import gemini                                        # noqa: F401
from ccxt_zagrava.hitbtc import hitbtc                                        # noqa: F401
from ccxt_zagrava.hitbtc3 import hitbtc3                                      # noqa: F401
from ccxt_zagrava.hollaex import hollaex                                      # noqa: F401
from ccxt_zagrava.htx import htx                                              # noqa: F401
from ccxt_zagrava.huobi import huobi                                          # noqa: F401
from ccxt_zagrava.huobijp import huobijp                                      # noqa: F401
from ccxt_zagrava.hyperliquid import hyperliquid                              # noqa: F401
from ccxt_zagrava.idex import idex                                            # noqa: F401
from ccxt_zagrava.independentreserve import independentreserve                # noqa: F401
from ccxt_zagrava.indodax import indodax                                      # noqa: F401
from ccxt_zagrava.kraken import kraken                                        # noqa: F401
from ccxt_zagrava.krakenfutures import krakenfutures                          # noqa: F401
from ccxt_zagrava.kucoin import kucoin                                        # noqa: F401
from ccxt_zagrava.kucoinfutures import kucoinfutures                          # noqa: F401
from ccxt_zagrava.kuna import kuna                                            # noqa: F401
from ccxt_zagrava.latoken import latoken                                      # noqa: F401
from ccxt_zagrava.lbank import lbank                                          # noqa: F401
from ccxt_zagrava.luno import luno                                            # noqa: F401
from ccxt_zagrava.lykke import lykke                                          # noqa: F401
from ccxt_zagrava.mercado import mercado                                      # noqa: F401
from ccxt_zagrava.mexc import mexc                                            # noqa: F401
from ccxt_zagrava.ndax import ndax                                            # noqa: F401
from ccxt_zagrava.novadax import novadax                                      # noqa: F401
from ccxt_zagrava.oceanex import oceanex                                      # noqa: F401
from ccxt_zagrava.okcoin import okcoin                                        # noqa: F401
from ccxt_zagrava.okx import okx                                              # noqa: F401
from ccxt_zagrava.onetrading import onetrading                                # noqa: F401
from ccxt_zagrava.oxfun import oxfun                                          # noqa: F401
from ccxt_zagrava.p2b import p2b                                              # noqa: F401
from ccxt_zagrava.paymium import paymium                                      # noqa: F401
from ccxt_zagrava.phemex import phemex                                        # noqa: F401
from ccxt_zagrava.poloniex import poloniex                                    # noqa: F401
from ccxt_zagrava.poloniexfutures import poloniexfutures                      # noqa: F401
from ccxt_zagrava.probit import probit                                        # noqa: F401
from ccxt_zagrava.timex import timex                                          # noqa: F401
from ccxt_zagrava.tokocrypto import tokocrypto                                # noqa: F401
from ccxt_zagrava.tradeogre import tradeogre                                  # noqa: F401
from ccxt_zagrava.upbit import upbit                                          # noqa: F401
from ccxt_zagrava.vertex import vertex                                        # noqa: F401
from ccxt_zagrava.wavesexchange import wavesexchange                          # noqa: F401
from ccxt_zagrava.wazirx import wazirx                                        # noqa: F401
from ccxt_zagrava.whitebit import whitebit                                    # noqa: F401
from ccxt_zagrava.woo import woo                                              # noqa: F401
from ccxt_zagrava.woofipro import woofipro                                    # noqa: F401
from ccxt_zagrava.xt import xt                                                # noqa: F401
from ccxt_zagrava.yobit import yobit                                          # noqa: F401
from ccxt_zagrava.zaif import zaif                                            # noqa: F401
from ccxt_zagrava.zonda import zonda                                          # noqa: F401

exchanges = [
    'ace',
    'alpaca',
    'ascendex',
    'bequant',
    'bigone',
    'binance',
    'binancecoinm',
    'binanceus',
    'binanceusdm',
    'bingx',
    'bit2c',
    'bitbank',
    'bitbay',
    'bitbns',
    'bitcoincom',
    'bitfinex',
    'bitfinex2',
    'bitflyer',
    'bitget',
    'bithumb',
    'bitmart',
    'bitmex',
    'bitopro',
    'bitpanda',
    'bitrue',
    'bitso',
    'bitstamp',
    'bitteam',
    'bitvavo',
    'bl3p',
    'blockchaincom',
    'blofin',
    'btcalpha',
    'btcbox',
    'btcmarkets',
    'btcturk',
    'bybit',
    'cex',
    'coinbase',
    'coinbaseadvanced',
    'coinbaseexchange',
    'coinbaseinternational',
    'coincheck',
    'coinex',
    'coinlist',
    'coinmate',
    'coinmetro',
    'coinone',
    'coinsph',
    'coinspot',
    'cryptocom',
    'currencycom',
    'delta',
    'deribit',
    'digifinex',
    'exmo',
    'fmfwio',
    'gate',
    'gateio',
    'gemini',
    'hitbtc',
    'hitbtc3',
    'hollaex',
    'htx',
    'huobi',
    'huobijp',
    'hyperliquid',
    'idex',
    'independentreserve',
    'indodax',
    'kraken',
    'krakenfutures',
    'kucoin',
    'kucoinfutures',
    'kuna',
    'latoken',
    'lbank',
    'luno',
    'lykke',
    'mercado',
    'mexc',
    'ndax',
    'novadax',
    'oceanex',
    'okcoin',
    'okx',
    'onetrading',
    'oxfun',
    'p2b',
    'paymium',
    'phemex',
    'poloniex',
    'poloniexfutures',
    'probit',
    'timex',
    'tokocrypto',
    'tradeogre',
    'upbit',
    'vertex',
    'wavesexchange',
    'wazirx',
    'whitebit',
    'woo',
    'woofipro',
    'xt',
    'yobit',
    'zaif',
    'zonda',
]

base = [
    'Exchange',
    'Precise',
    'exchanges',
    'decimal_to_precision',
]

__all__ = base + errors.__all__ + exchanges
