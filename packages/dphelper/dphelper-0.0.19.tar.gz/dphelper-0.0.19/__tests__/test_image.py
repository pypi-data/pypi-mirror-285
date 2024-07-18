import unittest   # The test framework
from src.dphelper.helper import DPHelper

class TestDPHelperImageService(unittest.TestCase):

    def test_single_image_upload(self):
        dphelper = DPHelper(api_key='ADD_YOUR_KEY_TO_TEST')
        # self.assertEqual(dphelper.get_key_for_image_service(), 'ADD_YOUR_API_KEY_TO_TEST')
        result = dphelper.upload_image_from_url('https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_92x30dp.png')
        self.assertGreater(len(result['id']), 0)
   
    def test_bulk_image_upload(self):
        dphelper = DPHelper(api_key='ADD_YOUR_KEY_TO_TEST')
        image_urls = [
            'https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_92x30dp.png',
            'https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_92x30dp.png',
        ]
        results = dphelper.upload_all_images(image_urls, max_concurrent=10)
        self.assertGreater(len(results["https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_92x30dp.png"]["id"]), 5)

if __name__ == '__main__':
    unittest.main()
