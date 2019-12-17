#!/usr/bin/python3
# Copyright eBrevia.com 2019
"""Document splitting server."""

import logging
import socket
import sys
import resource

import doc_config
import doc_split

result_map = {}
dict_mode = False

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# pylint: disable=invalid-name
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def tabular(tab_map):
    """Convert Python dict into sorted output lines "unsplit\tsplit\n"."""
    result = []
    for orig in sorted(tab_map.keys()):
        split = tab_map[orig]
        result.append(orig + '\t' + split)
    return '\n'.join(result) + '\n'

def run(client_socket, client_address, dict):
    """Reads, splits, writes."""
    input_bytes = bytearray(b'')
    blockno = 0
    while True:
        block = client_socket.recv(2048)
        #print ("Read block %d" % blockno, file=sys.stderr)
        blockno += 1
        if not block:
            break
        input_bytes += block
    logger.info("Read %d bytes", len(input_bytes))
    input_str = input_bytes.decode()
    result_map.clear()
    output_str = doc_split.doc_split(input_str, dict, result_map)
    if dict_mode:
        output_str = tabular(result_map)
    output_bytes = output_str.encode()
    logger.info("Split the text")
    client_socket.sendall(output_bytes)
    logger.info("Written %d bytes", len(output_bytes))
    client_socket.shutdown(socket.SHUT_WR)
    #print("Client at ", client_address, " disconnecting", file=sys.stderr)

def main():
    """Main server program.
       Reads the whole of standard input, splits it all,
       sends the result to standard output.
       Usage: doc_server [-p][-d] port dict
    """
    if len(sys.argv) > 3:
        dict = sys.argv[3]
    else:
        dict = doc_config.DEFAULT_DICT

    if len(sys.argv) > 2:
        port = int(sys.argv[2])
    else:
        port = doc_config.DEFAULT_PORT

    global dict_mode
    if len(sys.argv) > 1:
        dict_mode = (sys.argv[1] == '-d')

    # Load dictionaries and report memory usage while quiescent
    doc_split.load_known_words(dict)
    mem_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024
    logger.info("Memory usage: %d MB", mem_mb)

    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('localhost', port))
        logger.info("Server started")
        while True:
            server.listen(1)
            client, client_address = server.accept()
            run(client, client_address, dict)
    except:
        pass  # trap all errors so the server doesn't die

if __name__ == "__main__":
    main()
