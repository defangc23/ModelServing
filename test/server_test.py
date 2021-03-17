sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import requests, json, unittest


'''Change by user'''
REQUEST_URL = "http://172.16.124.12:666/extract"
PARAM_DICT = {}


class TestServer(unittest.TestCase):
    def test_REST(self):
        response = requests.post(REQUEST_URL, json=PARAM_DICT)
        res = response.json()
        print(res)
        self.assertEqual(res["status"], 1)

if __name__ == "__main__":
    unittest.main()