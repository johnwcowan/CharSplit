#!/usr/bin/env python3

import os
import socket
import subprocess
import time
import unittest

from doc_split import *


class TestDeDecompound(unittest.TestCase):
    """Test German decompounder.
       WARNING: If these tests fail, that does NOT necessarily mean
       that the algorithm is broken.  It may in fact have been improved,
       in which case RESULT_SENTENCE should be changed to the new result.
    """

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

    PORT = 30302   # Don't use production port

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

        self.assertEqual(doc_split(TestDeDecompound.TEST_SENTENCE),
                         TestDeDecompound.RESULT_SENTENCE);

    def test_doc_server_plaintext(self):
        # Start server
        pid = subprocess.Popen([sys.executable,    # this Python
                                '-m',
                                'doc_server',
                                '-p',
                                'de_dicts/de-mixed.dic',
                                str(self.PORT)])
        time.sleep(5)
        # Modified version of doc_client
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect(('localhost', self.PORT))
            print("connected to server", file=sys.stderr)
            input_bytes = TestDeDecompound.TEST_SENTENCE.encode()
            client.sendall(input_bytes)
            print("input sent", file=sys.stderr)
            client.shutdown(socket.SHUT_WR)
            print("shut down write side", file=sys.stderr)
            data = client.recv(2048)   # one block is enough
            output_str = data.decode()
            print("finished reading", file=sys.stderr)

            # Compare
            self.assertEquals(output_str, TestDeDecompound.RESULT_SENTENCE)

            # Kill server
            pid.kill()

    def test_doc_server_dict(self):
        # Start server
        pid = subprocess.Popen([sys.executable,    # this Python
                                '-m',
                                'doc_server',
                                '-d',
                                'de_dicts/de-mixed.dic',
                                str(self.PORT)])
        time.sleep(5)
        # Modified version of doc_client
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect(('localhost', self.PORT))
            print("connected to server", file=sys.stderr)
            input_bytes = TestDeDecompound.TEST_SENTENCE.encode()
            client.sendall(input_bytes)
            print("input sent", file=sys.stderr)
            client.shutdown(socket.SHUT_WR)
            print("shut down write side", file=sys.stderr)
            data = client.recv(2048)   # one block is enough
            output_str = data.decode()
            print("finished reading", file=sys.stderr)

            # Compare
            self.assertEquals(output_str, TestDeDecompound.RESULT_SENTENCE)

            # Kill server
            pid.kill()

if __name__ == "__main__":
    unittest.main()
