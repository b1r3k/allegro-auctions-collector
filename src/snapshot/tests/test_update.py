import unittest
from csvdb import get_hash
import snapshot
import mock

import allegro_client

class Test_update(unittest.TestCase):

    def setUp(self):
        self.allegro_api = allegro_client.AllegroClient()


    def test_fetch_all_add_five_new(self):

        # make ten item mocks
        mocked_cat_items = [ {'s-it-id': 1000 + i,'s-it-ending-time': 1383826866 + i} for i in range(0, 10) ]

        self.allegro_api.doShowCategory = mock.MagicMock(name='doShowCategory')
        self.allegro_api.doShowCategory.return_value = mocked_cat_items

        self.allegro_api.getItem = mock.MagicMock(name='getItem')

        # make only 5 of those items as items we already fetched, therefore there is only 5 new items to be fetched
        test_items_ids = range(1000, 1006)
        test_items_ending_times = range(1383826866, 1383826866 + 5)

        test_items_unique_ids = [ get_hash(pair[0], pair[1]) for pair in zip(test_items_ids, test_items_ending_times) ]

        test_items = dict(zip(test_items_unique_ids, test_items_ids))

        result = snapshot.fetch_all_add_new(self.allegro_api, 0, test_items)

        self.assertEqual(self.allegro_api.getItem.call_count, 5)
        self.assertEqual(len(test_items), 10)

if __name__ == '__main__':
    unittest.main()
