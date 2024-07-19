import unittest
from heytextual import HeyTextualClient

class TestHeyTextualClient(unittest.TestCase):
    def setUp(self):
        self.client = HeyTextualClient(api_key="your_test_api_key")

    def test_extract(self):
        # Add your test cases
        pass

    def test_documents(self):
        # Add your test cases
        pass

    def test_document(self):
        # Add your test cases
        pass

    def test_templates(self):
        # Add your test cases
        pass

if __name__ == '__main__':
    unittest.main()
