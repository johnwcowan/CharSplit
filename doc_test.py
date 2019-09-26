#!/usr/bin/env python3

import os
import socket
import subprocess
import time
import unittest

from doc_split import *
from char_split import *

TEST_WORD = 'Autobahnraststätte'
RESULT_WORD1 = 'Autobahn'
RESULT_WORD2 = 'Raststätte'

TEST_SENTENCE = \
    """Die Technik setzt sich aus dem europaweiten Mobilfunk·standard Gsm, 
       der in Deutschland über das D1-Netz angeboten wird,
       und dem weltweit verfügbaren System
       von Navigationssatelliten (Gps) zusammen.
    """

RESULT_SENTENCE = \
    """Die Technik setzt sich aus dem europaweiten Mobil·funk·standard Gsm, 
       der in Deutschland über das D1-Netz angeboten wird,
       und dem weltweit verfügbaren System
       von Navigations·satelliten (Gps) zusammen.
    """

RESULT_DICTIONARY = \
"""Mobilfunk\tMobil·funk
Navigationssatelliten\tNavigations·satelliten
"""

PPORT = 30302   # Don't use production port
DPORT = 30303   # Don't use production port


class TestDeDecompound(unittest.TestCase):
    """Test German decompounder.
       WARNING: If these tests fail, that does NOT necessarily mean
       that the algorithm is broken.  It may in fact have been improved,
       in which case RESULT_SENTENCE should be changed to the new result.
    """

    def test_char_split(self):
        result = split_compound(TEST_WORD)[0]
        self.assertEqual(result[1], RESULT_WORD1)
        self.assertEqual(result[2], RESULT_WORD2)

    def test_maximal_split(self):
        self.assertEqual(maximal_split('Mobilfunkstandard'),
                         ['Mobil', 'Funk', 'Standard'])
        self.assertEqual(maximal_split('europaweiten'),
                         ['europaweiten'])

    def test_maximal_split_str(self):
        self.assertEqual(maximal_split_str('Mobilfunkstandard'),
                         'Mobil·funk·standard')
        self.assertEqual(maximal_split_str('europaweiten'),
                         'europaweiten')

    def test_doc_split(self):

        self.assertEqual(doc_split(TEST_SENTENCE), RESULT_SENTENCE);

    def test_doc_server_plaintext(self):
        # Start server
        pid = subprocess.Popen([sys.executable,    # this Python
                                '-m',
                                'doc_server',
                                '-p',
                                str(PPORT)])
        time.sleep(5)
        # Modified version of doc_client
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect(('localhost', PPORT))
            #print("connected to server", file=sys.stderr)
            input_bytes = TEST_SENTENCE.encode()
            client.sendall(input_bytes)
            #print("input sent", file=sys.stderr)
            client.shutdown(socket.SHUT_WR)
            #print("shut down write side", file=sys.stderr)
            data = client.recv(2048)   # one block is enough
            output_str = data.decode()
            #print("finished reading", file=sys.stderr)

            # Compare
            self.assertEqual(output_str, RESULT_SENTENCE)

            # Kill server
            pid.kill()

    def test_doc_server_dict(self):
        # Start server
        pid = subprocess.Popen([sys.executable,    # this Python
                                '-m',
                                'doc_server',
                                '-d',
                                str(DPORT)])
        time.sleep(5)
        # Modified version of doc_client
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect(('localhost', DPORT))
            #print("connected to server", file=sys.stderr)
            input_bytes = TEST_SENTENCE.encode()
            client.sendall(input_bytes)
            #print("input sent", file=sys.stderr)
            client.shutdown(socket.SHUT_WR)
            #print("shut down write side", file=sys.stderr)
            data = client.recv(2048)   # one block is enough
            output_str = data.decode()
            #print("finished reading", file=sys.stderr)

            # Compare
            self.assertEqual(output_str, RESULT_DICTIONARY)

            # Kill server
            pid.kill()

if __name__ == "__main__":
    unittest.main()
