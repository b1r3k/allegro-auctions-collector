from _mysql import result
import unittest
from allegro_client import AllegroClient

class TestCase_getItem(unittest.TestCase):

    def setUp(self):
        self.allegroClient = AllegroClient()

    def test_quantity_sold_computation_simple(self):
        itemBids = [{"bids-array":
            ["3541106112",
             "0",
             "l...1",
             "4",
             "0",
             "1", #
             "46.4",
             "1378877910",
             "1",
             "",
             "",
             "0",
            ]},
            {"bids-array": ["3541106112",
             "0",
             "m...i",
             "165",
             "0",
             "1", #
             "46.4",
             "1378883622",
             "1",
             "",
             "",
             "0",
            ]},
            {"bids-array": ["3541106112",
               "0",
               "p...0",
               "32",
               "0",
               "2", #
               "46.4",
               "1378900035",
               "1",
               "",
               "",
               "0",
            ]}
        ]

        expected = 4
        result = self.allegroClient.getQuantitySold(itemBids)

        self.assertEqual(expected, result)

    def test_quantity_sold_computation_cancelled_orders(self):
        itemBids = [{"bids-array":
            ["3541106112",
             "0",
             "l...1",
             "4",
             "0",
             "1", #
             "46.4",
             "1378877910",
             "1",
             "",
             "",
             "0",
            ]},
            {"bids-array": ["3541106112",
             "0",
             "m...i",
             "165",
             "0",
             "1", #
             "46.4",
             "1378883622",
             "-1",
             "",
             "",
             "0",
            ]},
            {"bids-array": ["3541106112",
               "0",
               "p...0",
               "32",
               "0",
               "2", #
               "46.4",
               "1378900035",
               "1",
               "",
               "",
               "0",
            ]}
        ]

        expected = 3
        result = self.allegroClient.getQuantitySold(itemBids)

        self.assertEqual(expected, result)


if __name__ == '__main__':
    unittest.main()
