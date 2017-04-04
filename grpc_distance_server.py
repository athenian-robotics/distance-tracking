#!/usr/bin/env python

import argparse
import logging
import time

import grpc
from concurrent import futures
from grpc_support import GenericServer
from prometheus_client import Counter
from prometheus_client import start_http_server, Summary
from utils import current_time_millis
from utils import setup_logging

from proto.distance_service_pb2 import Distance
from proto.distance_service_pb2 import DistanceServiceServicer
from proto.distance_service_pb2 import ServerInfo
from proto.distance_service_pb2 import add_DistanceServiceServicer_to_server

logger = logging.getLogger(__name__)

summary = Summary('request_processing_seconds', 'Time spent processing request')
c = Counter('currvals_counter', 'Description of currvalls_counter', ['method', 'endpoint'])


class GrpcDistanceServer(DistanceServiceServicer, GenericServer):
    def __init__(self, port=None):
        super(GrpcDistanceServer, self).__init__(port=port, desc="distance server")
        self.grpc_server = None

    def registerClient(self, request, context):
        logger.info("Connected to {0} client {1} [{2}]".format(self.desc, context.peer(), request.info))
        return ServerInfo(info="Server invoke count {0}".format(self.increment_cnt()))

    def getDistance(self, request, context):
        return self.get_currval()

    @summary.time()
    def getDistances(self, request, context):
        client_info = request.info
        # Update metrics
        c.labels(method='get', endpoint='/').inc()
        c.labels(method='post', endpoint='/submit').inc(2)
        return self.currval_generator(context.peer())

    def _init_values_on_start(self):
        self.write_distance(-1)

    def _adjust_currval(self, currval, start_time):
        if currval:
            currval.elapsed = current_time_millis() - start_time
        return currval

    def _start_server(self):
        logger.info("Starting gRPC {0} listening on {1}".format(self.desc, self.hostname))
        self.grpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        add_DistanceServiceServicer_to_server(self, self.grpc_server)
        self.grpc_server.add_insecure_port(self.hostname)
        self.grpc_server.start()
        try:
            while not self.stopped:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()

    def write_distance(self, distance):
        if not self.stopped:
            self.id += 1
            self.set_currval(Distance(id=self.id,
                                      ts=current_time_millis(),
                                      elapsed=0,
                                      distance=distance))


stopped = False


def run_server(delay):
    with GrpcDistanceServer() as server:
        cnt = 0
        while not stopped:
            server.write_distance(cnt)
            cnt += 1
            time.sleep(delay)


def stop_server():
    global stopped
    stopped = True


if __name__ == "__main__":
    setup_logging()

    parser = argparse.ArgumentParser()
    parser.add_argument("--delay", type=float, default=1.0, help="Delay secs")
    parser.add_argument("--metrics", default=False, action="store_true", help="Enable metrics")
    args = vars(parser.parse_args())

    # Start up a server to expose the metrics.
    if args["metrics"]:
        start_http_server(8000)

    run_server(args["delay"])