import os
import unittest
import shop

class BasicTest(unittest.TestCase):

    def setUp(self):
      self.app = shop.app.test_client()
      self.assertEqual(shop.app.debug, False)

    def test_home_page(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()