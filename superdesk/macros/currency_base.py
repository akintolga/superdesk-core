# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import requests
import re
from . import macro_replacement_fields

RATE_SERVICE = 'http://download.finance.yahoo.com/d/quotes.csv?s={}=X&f=nl1d1'


def get_rate(from_currency, to_currency):
    """Get the exchange rate."""
    r = requests.get(RATE_SERVICE.format(from_currency + to_currency), timeout=5)
    return float(r.text.split(',')[1])


def do_conversion(item, rate, prefix, search_param):
    """
    Performs the conversion
    :param item: story
    :param rate: exchange rate
    :param prefix: to be used in the results
    :param search_param: search parameter to locate the original value.  It should
    be a valid regular expression pattern, and not just an arbitrary string.
    :return: modified story
    """
    diff = {}

    def convert(match):
        from_value = float(match.group(1))
        to_value = rate * from_value
        diff.setdefault(match.group(0), prefix % to_value)
        return diff[match.group(0)]

    for field in macro_replacement_fields:
        if item.get(field, None):
            item[field] = re.sub(search_param, convert, item[field])

    return (item, diff)
