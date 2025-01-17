#!/usr/bin/env python

"""Generates a stream to Kafka from a time series csv file.
"""

import argparse
import csv
import json
import sys
import time
from datetime import datetime
from dateutil.parser import parse
from confluent_kafka import Producer
import socket

csv.field_size_limit(sys.maxsize)


def acked(err, msg):
    if err is not None:
        print("Failed to deliver message: %s: %s" % (str(msg.value()), str(err)))
    else:
        print("Message produced: %s" % (str(msg.value())))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('filename', type=str,
                        help='Time series csv file.')
    parser.add_argument('topic', type=str,
                        help='Name of the Kafka topic to stream.')
    parser.add_argument('--speed', type=float, default=1, required=False,
                        help='Speed up time series by a given multiplicative factor.')
    args = parser.parse_args()

    topic = args.topic
    p_key = args.filename

    conf = {'bootstrap.servers': "kafka:9092",
            'client.id': socket.gethostname()}
    producer = Producer(conf)

    rdr = csv.reader(open(args.filename))
    next(rdr)  # Skip header
    firstline = True

    while True:

        try:

            if firstline is True:
                line1 = next(rdr, None)
                timestamp, value = line1[0], line1[0]
                # Convert csv columns to key value pair
                result = {}
                result["ts"] = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f").isoformat(timespec='milliseconds') + 'Z'
                result["msg"] = value
                # Convert dict to json as message format
                jresult = json.dumps(result)
                firstline = False

                print("Msg len", len(value))
                producer.produce(topic, key=p_key, value=jresult, callback=acked)

            else:
                line = next(rdr, None)
                d1 = parse(timestamp)
                d2 = parse(line[0])
                diff = ((d2 - d1).total_seconds())/args.speed
                time.sleep(5.0)
                timestamp, value = line[0], line[1]
                result = {}
                result["ts"] = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f").isoformat(timespec='milliseconds') + 'Z'
                result["msg"] = value
                jresult = json.dumps(result)

                print("Msg len", len(value))
                producer.produce(topic, key=p_key, value=jresult, callback=acked)

            producer.flush()

        except TypeError:
            sys.exit()


if __name__ == "__main__":
    main()
