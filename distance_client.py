#!/usr/bin/env python3

import argparse
import logging
import socket
import time

import cli_args as cli
from constants import LOG_LEVEL
from grpc_support import CannotConnectException, SingleValueClient
from utils import setup_logging

from grpc_distance_client import GrcpDistanceClient

logger = logging.getLogger(__name__)


class DistanceClient(SingleValueClient):
    def __init__(self, hostname):
        super(DistanceClient, self).__init__(hostname, desc="{0} client".format(socket.gethostname()))
        self.__grpc_client = GrcpDistanceClient(self.hostname)

    def _get_values(self, pause_secs=2.0):
        while not self.stopped:
            try:
                self.__grpc_client.connect()
            except CannotConnectException:
                time.sleep(pause_secs)
                continue

            try:
                for val in self.__grpc_client.values():
                    with self.value_lock:
                        self.currval = val
                    self._mark_ready()
                    if self.stopped:
                        break
            except BaseException as e:
                logger.info("Error reading values from gRPC server at %s [%s]", self.hostname, e)
                time.sleep(pause_secs)
            logger.info("Disconnected from gRPC server at %s", self.hostname)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", dest="host", default="localhost", help="Distance server hostname")
    cli.verbose(parser)
    args = vars(parser.parse_args())

    setup_logging(level=args[LOG_LEVEL])

    cnt = 0

    for i in range(5):
        print("Iteration {0}".format(i))
        with DistanceClient(args["host"]) as client:
            for d, j in zip(client.values(), range(10)):
                print(d)
                cnt += 1

            for j in range(10):
                print(client.value())
                cnt += 1

    assert cnt == 5 * 10 * 2

    print("Exiting...")
