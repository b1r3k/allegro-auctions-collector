# -*- coding: UTF-8 -*-

'''
This work is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License.
To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/3.0/.

Created on Oct 7, 2011

@author: b1r3k

'''
import logging
import time
import sys
from functools import wraps
from httplib import BadStatusLine
import socket

from csvdb import AllegroItem, AllegroUser, get_hash

import config

LOG_LEVEL = config.LOG_LEVEL
WSDL_URL = 'http://webapi.allegro.pl/uploader.php?wsdl'
API_RETRY_TIME = 5 # secs
API_MAX_RETRIES = 10

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

hdl = logging.StreamHandler()
hdl.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', '%Y-%m-%d %H:%M'))

logger.addHandler(hdl)

import suds

def exception_hook(excType, excValue, traceback, logger=logger):
    logger.error("Logging an uncaught exception",
                 exc_info=(excType, excValue, traceback))

if LOG_LEVEL == logging.DEBUG:
    sys.excepthook = exception_hook

def handle_common_exception(method):
    @wraps(method)
    def wrapper(self, *args, **kwds):
        try:
            return method(self, *args, **kwds)

        except suds.WebFault as e:
            if (e.fault['faultcode'] in [ 'ERR_NO_SESSION', 'ERR_SESSION_EXPIRED' ]):
                logger.debug('Session expired while in method: %s, args: %s, kwds: %s' % (method, args, kwds))
                self.login(self._allegro_user)
                return method(self, *args, **kwds)
            else:
                raise e

        except BadStatusLine as e:
            logger.warning('Unknown HTTP response, skipping API call')
            logger.debug('Method: %s, args: %s, kwds: %s' % (method, args, kwds))

        except socket.error as e:
            if self._retry_count > API_MAX_RETRIES:
                raise e

            errno = e[0]
            if errno == 104:
                logger.debug('%s: %s, args: %s, kwds: %s, retrying...' % (e[1],method, args, kwds))
                time.sleep(API_RETRY_TIME)
                self._retry_count += 1
                result = method(self, *args, **kwds)
                self._retry_count = 0
                return result

    return wrapper

class SOAPClient(suds.client.Client):

    _default_country_code = 1
    _session = None
    _allegro_user = None
    _retry_count = 0

    def __init__(self, wsdl_url=WSDL_URL, cache=None):
        super(SOAPClient, self).__init__(wsdl_url)
        self.set_options(cache=cache)
        self._default_country_code = 1
        self._session = None
        self._allegro_user = None
        self._retry_count = 0

    def login(self, allegro_user):
        # Fetch the latest version key
        sys_status = self.service.doQuerySysStatus(1, self._default_country_code, allegro_user.apikey)
        version_key = getattr(sys_status, 'ver-key')

        response = self.service.doLoginEnc(allegro_user.username,
                                           allegro_user.password,
                                           self._default_country_code,
                                           allegro_user.apikey,
                                           version_key)

        self._session = getattr(response, 'session-handle-part')
        self._allegro_user = allegro_user

    @handle_common_exception
    def doShowItemInfoExt(self, itemId):
        rValue = self.service.doShowItemInfoExt(self._session, itemId)

        return rValue

    @handle_common_exception
    def doGetBidItem2(self, itemId):
        rValue = self.service.doGetBidItem2(self._session, itemId)

        return rValue

    @handle_common_exception
    def doShowCat(self, categoryId, **kwargs):
        rValue = self.service.doShowCat(self._session, categoryId, **kwargs)

        return rValue

    @handle_common_exception
    def doSearch(self, *args, **kwds):
        rValue = self.service.doSearch(self._session, *args, **kwds)

        return rValue


class AllegroClient(SOAPClient):
    def doPagedSearch(self, keywords, items_per_req=50):
        searchOptType = self.factory.create('SearchOptType')

        setattr(searchOptType, 'search-country', 1)
        setattr(searchOptType, 'search-string', keywords)
        setattr(searchOptType, 'search-limit', items_per_req)

        search_results = self.doSearch(searchOptType)

        search_items_count = getattr(search_results, 'search-count')
        search_items = getattr(search_results, 'search-array')

        print('Search results: count = %d' % search_items_count)
        print('Search results: array length = %d' % len(search_items))

        result_page = 1
        all_items = []
        all_items.extend(search_items)

        while len(all_items) < search_items_count:
            print('Offset: %d, total items: %d' % (result_page, len(all_items)))

            setattr(searchOptType, 'search-offset', result_page)

            search_results = self.doSearch(searchOptType)

            search_items = getattr(search_results, 'search-array')

            all_items.extend(search_items)
            result_page += 1

        return all_items

    def doShowCategory(self, categoryId):

        doShowCat_request = {'cat-items-offset': 0,
                             'cat-items-limit': 100,
        }

        cat_items_response = self.doShowCat(categoryId, **doShowCat_request)
        all_items_count = cat_items_response['cat-items-count']

        fetched_items_count = 0

        logger.debug('Ilosc itemow w kategorii = %d' % all_items_count)
        while (fetched_items_count < all_items_count):
            items_list = cat_items_response['cat-items-array']
            if len(items_list):
                [(yield item) for item in items_list]

                fetched_items_count += len(items_list)

                logger.debug('Stopien zakonczenia: %.2f' % ((fetched_items_count/float(all_items_count)) * 100))
                doShowCat_request['cat-items-offset'] += 1
                cat_items_response = self.doShowCat(categoryId, **doShowCat_request)
            else:
                logger.warning('Brak rezultatow, pobrano itemow: %d, spodziewano sie: %d' % (fetched_items_count, all_items_count))
                raise StopIteration

    def getQuantitySold(self, itemBidsList):

        total_quantity_sold = 0

        try:
            for itemBid in itemBidsList:
                itemBidsList = itemBid['bids-array']
                # 1 - oferta zakończona sprzedażą
                if (int(itemBidsList[8]) == 1):
                    # liczba zakupionych przedmiotów w ofercie,
                    total_quantity_sold += int(itemBidsList[5])

        except TypeError as e:
            # sounds like no one bought anything
            pass

        finally:
            return total_quantity_sold

    def getItem(self, itemId):
        item = None
        try:
            itemInfoExt = self.doShowItemInfoExt(itemId)['item-list-info-ext']
            itemBids = self.doGetBidItem2(itemId)

            # construct Item object and fill it with data from both queries, compute if needed

            item_bid_count = getattr(itemInfoExt, 'it-bid-count')
            item_quantity_available = getattr(itemInfoExt, 'it-quantity')
            item_quantity_sold = self.getQuantitySold(itemBids)

            item_seller_name = unicode(getattr(itemInfoExt, 'it-seller-login'))
            item_seller_location = unicode(getattr(itemInfoExt, 'it-location'))
            item_seller_rating = getattr(itemInfoExt, 'it-seller-rating')

            item_foto_count = getattr(itemInfoExt, 'it-foto-count')
            item_buy_now_price = getattr(itemInfoExt, 'it-buy-now-price')
            item_hit_count = getattr(itemInfoExt, 'it-hit-count')

            item_ending_info = getattr(itemInfoExt, 'it-ending-info')
            item_is_allegro_standard = getattr(itemInfoExt, 'it-is-allegro-standard')
            item_is_new = getattr(itemInfoExt, 'it-is-new-used')

            item_title = unicode(getattr(itemInfoExt, 'it-name'))
            item_description = unicode(getattr(itemInfoExt, 'it-description'))
            item_ending_timestamp = getattr(itemInfoExt, 'it-ending-time')
            item_fetched_timestamp = int(time.time())

            item = AllegroItem( get_hash(itemId, item_ending_timestamp),
                                itemId,
                                item_bid_count,
                                item_quantity_available,
                                item_quantity_sold,
                                item_seller_name,
                                item_seller_location,
                                item_seller_rating,
                                item_foto_count,
                                item_buy_now_price,
                                item_hit_count,
                                item_ending_info,
                                item_is_allegro_standard,
                                item_is_new,
                                item_title,
                                item_description,
                                item_ending_timestamp,
                                item_fetched_timestamp
            )

        except (suds.WebFault, Exception) as e:
            logger.debug(unicode(e))
            logger.warning('Skipping item ID = %s' % itemId)

            return None

        return item

