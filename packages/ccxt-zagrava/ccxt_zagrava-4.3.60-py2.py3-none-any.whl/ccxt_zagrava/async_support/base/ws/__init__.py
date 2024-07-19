# -*- coding: utf-8 -*-

from ccxt_zagrava.base import errors

# -----------------------------------------------------------------------------

from ccxt_zagrava.base import decimal_to_precision

from ccxt_zagrava import BaseError                  # noqa: F401
from ccxt_zagrava import ExchangeError              # noqa: F401
from ccxt_zagrava import NotSupported               # noqa: F401
from ccxt_zagrava import AuthenticationError        # noqa: F401
from ccxt_zagrava import PermissionDenied           # noqa: F401
from ccxt_zagrava import AccountSuspended           # noqa: F401
from ccxt_zagrava import InvalidNonce               # noqa: F401
from ccxt_zagrava import InsufficientFunds          # noqa: F401
from ccxt_zagrava import InvalidOrder               # noqa: F401
from ccxt_zagrava import OrderNotFound              # noqa: F401
from ccxt_zagrava import OrderNotCached             # noqa: F401
from ccxt_zagrava import DuplicateOrderId           # noqa: F401
from ccxt_zagrava import CancelPending              # noqa: F401
from ccxt_zagrava import NetworkError               # noqa: F401
from ccxt_zagrava import DDoSProtection             # noqa: F401
from ccxt_zagrava import RateLimitExceeded          # noqa: F401
from ccxt_zagrava import RequestTimeout             # noqa: F401
from ccxt_zagrava import ExchangeNotAvailable       # noqa: F401
from ccxt_zagrava import OnMaintenance              # noqa: F401
from ccxt_zagrava import InvalidAddress             # noqa: F401
from ccxt_zagrava import AddressPending             # noqa: F401
from ccxt_zagrava import ArgumentsRequired          # noqa: F401
from ccxt_zagrava import BadRequest                 # noqa: F401
from ccxt_zagrava import BadResponse                # noqa: F401
from ccxt_zagrava import NullResponse               # noqa: F401
from ccxt_zagrava import OrderImmediatelyFillable   # noqa: F401
from ccxt_zagrava import OrderNotFillable           # noqa: F401


__all__ = decimal_to_precision.__all__ + errors.__all__  # noqa: F405
