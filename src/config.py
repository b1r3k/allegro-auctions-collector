'''
 * Author: Lukasz Jachym
 * Date: 9/27/13
 * Time: 10:47 PM
 *
 * This work is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License.
 * To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/3.0/.
'''

import logging

from csvdb import AllegroUser

user = AllegroUser('XXXX',
                    'YYYY-PASS',
                    'zzz-API-key'
)

LOG_LEVEL = logging.DEBUG