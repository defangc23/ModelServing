import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import requests, json, unittest


'''Change by user'''
REQUEST_URL = "http://127.0.0.1:666/extract"
PARAM_DICT = {"token": 123, "discord_ID": 330421170186879007}
# form = json.dumps(PARAM_DICT)

class TestServer(unittest.TestCase):
    def test_REST(self):
        response = requests.post(REQUEST_URL, json=PARAM_DICT)
        res = response.json()
        print(res)
        self.assertEqual(res["status"], 1)

if __name__ == "__main__":
    unittest.main()