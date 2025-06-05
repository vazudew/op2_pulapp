import unittest
import json
import urllib.request
import requests

## Pulumi outputs are not stringable, so storing the testable params in a file
test_params_file ="test_params.json"
with open(test_params_file) as f:
    testables = json.load(f)

class AppTester(unittest.TestCase):    
    def test_web_app_exists(self):
        print(testables["op2_plapp_url"])
        link = f'http://{testables["op2_plapp_url"]}'
        try:
            content = urllib.request.urlopen(link)
            print("website reacahble, PASS!")
        except Exception as e:
            self.fail(f"Exception occured {e}, website not reachable")

    def test_config_val_exists(self):
        print(testables["config_val"])
        print(testables["op2_plapp_url"])
        link = f'http://{testables["op2_plapp_url"]}'
        pattern = testables["config_val"]
        try:
            content = requests.get(link)
            if pattern in content.text:
                print("configured value is displayed, PASS!")
                print(content.text)
            else:
                self.fail("configured value is not displayed, FAIL!")
        except Exception as e:
            self.fail(f"Exception occured {e}, website not reachable")
        pass

if __name__ == '__main__':
    unittest.main()
    print("Hello")