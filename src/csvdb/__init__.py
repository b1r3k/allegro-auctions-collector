'''
 * Author: Lukasz Jachym
 * Date: 11/6/13
 * Time: 7:30 PM
 *
 * This work is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License.
 * To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/3.0/.
'''
import sys

if sys.version_info[0] == 3 and sys.version_info[1] >= 3:
    from .struct import AllegroItem
    from .struct import AllegroUser
    from .struct import get_item_hash
    from .struct import get_hash

    from .io import read_items
    from .io import dump_items_coroutine
else:
    from struct import AllegroItem
    from struct import AllegroUser
    from struct import get_item_hash
    from struct import get_hash

    from io import read_items
    from io import dump_items_coroutine

