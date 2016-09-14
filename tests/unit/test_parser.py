# Copyright 2016 Eitan Geiger
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from os import remove
import unittest

from DHCPConfParser.DHCPConfParser import DHCPConfParser
from DHCPConfParser.DHCPConfParser import ParseError

SAMPLE_FILE = "/tmp/dhcpd.conf"


class TestParser(unittest.TestCase):

    def setUp(self):

        valid = """#this is line comment
                subnet 10.0.0.0 netmask 255.255.0.0 { #this is another comment
                    \toption routers 10.0.0.1;
               }"""
#        invalid = "#shity shit" \
#                  "subnet 10.0.0.0 netmask {" \
#                  "\t\t\t option routers 10.0.0.1"

        with open(SAMPLE_FILE, 'w') as f:
            f.write(valid)

    def tearDown(self):
        remove(SAMPLE_FILE)

    def test_preformat(self):
        parser = DHCPConfParser(SAMPLE_FILE)
        confs = parser._preformat()
        self.assertEqual(confs, ['subnet 10.0.0.0 netmask 255.255.0.0',
                                 '{', 'option routers 10.0.0.1', ';', '}'])

    def test_parse_option(self):
        key, value = DHCPConfParser._parse_option(['option shit 1 2 3', ';'])
        self.assertEqual(key, "option shit")
        self.assertEqual(value, ["1", "2", "3"])

        key, value = DHCPConfParser._parse_option(['shit 1 2 3', ';'])
        self.assertEqual(key, "shit")
        self.assertEqual(value, ["1", "2", "3"])

        key, value = DHCPConfParser._parse_option(['shit 1', ';'])
        self.assertEqual(key, "shit")
        self.assertEqual(value, "1")

        self.assertRaises(ParseError, DHCPConfParser._parse_option,
                          ['shit 1'])


if __name__ == '__main__':
    unittest.main()
