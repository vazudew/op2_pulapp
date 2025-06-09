"""This script does basic system testing of the app, against given success criteria"""

import unittest
import urllib.request
import subprocess
import requests
import json

TESTABLES = {}

def get_pulumi_values():
    """global scoped method to retrieve testable items for Pulumi project"""

    TESTABLES["op2_plapp_url"] = subprocess.run(
        ['pulumi', 'stack', 'output', 'op2_plapp_url'],
        stdout=subprocess.PIPE,  check = True).stdout.decode('utf-8').rstrip()

    TESTABLES["config_val"] =   subprocess.run(
        ['pulumi', 'config', 'get', 'config_val'],
        stdout=subprocess.PIPE,  check = True).stdout.decode('utf-8').rstrip()

    TESTABLES["image_digest"] = subprocess.run(
        ['pulumi', 'stack', 'output', 'image_digest'],
        stdout=subprocess.PIPE,  check = True).stdout.decode('utf-8').rstrip()
    print ("Testable Parameters" + json.dumps(TESTABLES, indent=4))

class AppTester(unittest.TestCase):
    """Test Script Class, containing Test cases"""

    def test_web_app_exists(self):
        """test case to check if given web page for the app exists (or not)"""

        print("URL:" + TESTABLES["op2_plapp_url"])
        link = f'http://{TESTABLES["op2_plapp_url"]}'
        try:
            urllib.request.urlopen(link)
            print("website reacahble, PASS!")
        except Exception as exception:
            self.fail(f"Exception occured {exception}, website not reachable")

    def test_config_val_exists(self):
        """test case to check if configured value in web page for the app exists (or not)"""

        print("CONFIGURED_VALUE:" + TESTABLES["config_val"])
        print("URL:" + TESTABLES["op2_plapp_url"])
        link = f'http://{TESTABLES["op2_plapp_url"]}'
        pattern = TESTABLES["config_val"]
        try:
            content = requests.get(link)
            if pattern in content.text:
                print("configured value is displayed, PASS!")
                print(content.text)
            else:
                self.fail("configured value is not displayed, FAIL!")
        except Exception as exception:
            self.fail(f"Exception occured {exception}, website not reachable")

if __name__ == '__main__':
    get_pulumi_values()
    unittest.main(verbosity=2)
    print("Hello")
    