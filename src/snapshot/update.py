'''
 * Author: Lukasz Jachym
 * Date: 11/1/13
 * Time: 4:23 PM
 *
 * This work is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License.
 * To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/3.0/.
'''

import itertools
import logging
from csvdb.io import dump_items
from csvdb.struct import get_item_hash, get_hash

import config

logger = logging.getLogger(__name__)
logger.setLevel(config.LOG_LEVEL)

hdl = logging.StreamHandler()
hdl.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', '%Y-%m-%d %H:%M'))

logger.addHandler(hdl)

def fetch_all_add_new(api_client, categoryId, items):

    current_category_items = api_client.doShowCategory(categoryId)


    current_category_items_dict = {}

    for current_category_item in current_category_items:
        current_item_id = current_category_item['s-it-id']
        items_ending_time = current_category_item['s-it-ending-time']

        item_unique_id = get_hash(current_item_id, items_ending_time)

        if not item_unique_id in current_category_items_dict:
            current_category_items_dict[item_unique_id] = current_item_id
        else:
            logger.warning('Collision occurred for uid: %s [ id: %d, ending-timestamp: %d ]' %(item_unique_id, current_item_id,
                                                                                                items_ending_time))

    new_items = itertools.ifilterfalse(items.has_key, current_category_items_dict.iterkeys())
    new_items_added_count = 0
    new_items_skipped_count = 0

    for new_items_unique_id in new_items:
        new_item = api_client.getItem(current_category_items_dict[new_items_unique_id])

        if new_item:
            items[new_items_unique_id] = new_item
            new_items_added_count += 1
        else:
            new_items_skipped_count += 1

    return new_items_added_count, new_items_skipped_count

def update_items(item_reader, csv_writer, api_client, categoryId):
    items = {}

    for item in item_reader:
        items[item.unique_id] = item

    initial_items_len = len(items)
    logger.debug('Read %d items' % initial_items_len)

    # wybierz tylko te rekordy ktorych czas zakonczenia jest w przyszlosci w stosunku do daty pobrania danych
    to_be_fetched = lambda item: item.ending_timestamp > item.fetched_timestamp
    not_expired = itertools.ifilter(to_be_fetched, items.itervalues())

    updated_items_counter = 0
    missed_updated_items_counter = 0

    for current_category_item in not_expired:
        newly_fetched_item = api_client.getItem(current_category_item.id)

        if newly_fetched_item:
            items[current_category_item.unique_id] = newly_fetched_item
            updated_items_counter += 1
        else:
            missed_updated_items_counter += 1

    logger.info('Updated data for %d items' % updated_items_counter)
    logger.info('Couldn\'t update data for %d items' % missed_updated_items_counter)

    assert initial_items_len - len(items) == missed_updated_items_counter
    ##

    new_items_len, missed_new_items_len = fetch_all_add_new(api_client, categoryId, items)
    logger.debug('Added new items: %d' % new_items_len)
    logger.debug('Missed new items: %d' % missed_new_items_len)

    total_items_len = initial_items_len + new_items_len - missed_updated_items_counter
    assert total_items_len == len(items)

    logger.debug('Final amount of items: %d' % (total_items_len))

    dump_items(csv_writer, items)