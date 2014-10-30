# -*- coding: UTF-8 -*-

'''
 * Author: Lukasz Jachym
 * Date: 9/18/13
 * Time: 10:35 PM
 *
 * This work is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License.
 * To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/3.0/.
'''

import argparse
import sys
import csv

PYTHON_3_3 = True if sys.version_info >= (3, 3, 0) else False

import csvdb
import snapshot
import config
import allegro_client

if not PYTHON_3_3:
    import UnicodeCSV

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--fetch', dest='mode', action='store_const', const = 'fetch')
    parser.add_argument('-v', '--validate', dest='mode', action='store_const', const = 'validate')
    parser.add_argument('-u', '--update', dest='mode', action='store_const', const = 'update')
    parser.add_argument('-c', '--categoryId', dest='category_id', action='store')
    args = parser.parse_args()

    data_input = csv.DictReader(sys.stdin, dialect='excel-tab')

    if not PYTHON_3_3:
        data_output = UnicodeCSV.UnicodeDictWriter(sys.stdout, csvdb.AllegroItem._fields, dialect='excel-tab', quoting=csv.QUOTE_ALL)
    else:
        data_output = csv.DictWriter(sys.stdout, csvdb.AllegroItem._fields, dialect='excel-tab', quoting=csv.QUOTE_ALL)

    if args.mode == 'fetch':
        api_client = allegro_client.AllegroClient()
        api_client.login(config.user)

        fetch_item_generator = snapshot.fetch_items_from_category(args.category_id, api_client)
        output_stream = csvdb.dump_items_coroutine(data_output)
        for item in fetch_item_generator:
            output_stream.send(item)

    elif args.mode == 'update':
        api_client = allegro_client.AllegroClient()
        api_client.login(config.user)

        snapshot.update_items(csvdb.read_items(data_input), data_output, api_client, args.category_id)
    elif args.mode == 'validate':
        snapshot.check_for_duplicates(csvdb.read_items(data_input))

