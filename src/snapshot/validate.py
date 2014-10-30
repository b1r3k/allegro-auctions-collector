'''
 * Author: Lukasz Jachym
 * Date: 11/18/13
 * Time: 6:39 PM
 *
 * This work is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License.
 * To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/3.0/.
'''

import itertools
from functools import partial


def check_for_duplicates(csv_reader):

    validation_ok = True

    items = {}
    item_counter = 0
    collision_counter = 0

    for item in csv_reader:
        if items.has_key(item.unique_id):
            collision_counter += 1

        items[item.unique_id] = item
        item_counter += 1

    print('Read %d items, stored %d items' % (item_counter, len(items)))
    print('Detected collisions, len = %s' % collision_counter)

    # check if item record is duplicated
    # compare item id (assigned by allegro) and items ending_timestamp
    for unique_item_id in items:
        is_the_same = lambda itemA_uid, itemB_uid: True if items[itemA_uid].unique_id == items[itemB_uid].unique_id and items[itemA_uid].ending_timestamp == items[itemB_uid].ending_timestamp else False
        is_the_same_as = partial(is_the_same, unique_item_id)
        duplicates_counter = len(list(itertools.ifilter(is_the_same_as, items)))

        if duplicates_counter > 1:
            print('Found duplicate, id = %d, ending_timestamp = %s, itemA_hash: %s' % (items[unique_item_id].id, items[unique_item_id].ending_timestamp, unique_item_id))

    return bool(collision_counter or duplicates_counter)