'''
 * Author: Lukasz Jachym
 * Date: 11/1/13
 * Time: 2:21 PM
 *
 * This work is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License.
 * To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/3.0/.
'''

def fetch_items_from_category(categoryId, allegro_client):
    items_list = allegro_client.doShowCategory(categoryId)

    for item in items_list:
        item_id = item['s-it-id']
        item_extended = allegro_client.getItem(item_id)

        if item_extended:
            yield item_extended