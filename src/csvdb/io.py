'''
 * Author: Lukasz Jachym
 * Date: 11/6/13
 * Time: 7:34 PM
 *
 * This work is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License.
 * To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/3.0/.
'''
import sys

if sys.version_info[0] == 3 and sys.version_info[1] >= 3:
    from .struct import AllegroItem
    from .struct import get_item_hash

else:
    from struct import AllegroItem
    from struct import get_item_hash


def coroutine(func):
    def start(*args,**kwargs):
        cr = func(*args,**kwargs)
        cr.next()
        return cr
    return start

@coroutine
def dump_items_coroutine(output_stream):
    output_stream.writeheader()

    try:
        while True:
            item = (yield)
            item_asdict = item._asdict()
            output_stream.writerow(item_asdict)

    except GeneratorExit:
        pass

def read_items(input_stream):
    input_stream.next()

    for item_row in input_stream:
        try:
            item = AllegroItem(**item_row)
            item_hash = get_item_hash(item)
            if not item.unique_id == item_hash:
                item_row['unique_id'] = item_hash
                item = AllegroItem(**item_row)

        except TypeError as e:
            item_row['unique_id'] = ''
            item = AllegroItem(**item_row)
            item_row['unique_id'] = get_item_hash(item)
            item = AllegroItem(**item_row)

        yield item

def dump_items(output_stream, items):
    output_stream.writeheader()
    output_stream.writerows(map(lambda item: item._asdict(), items.itervalues()))