
"""
Simple decoder, accepts vector+text chunks input, applies entity
relationship analysis to get entity relationship edges which are output as
graph edges.
"""

import pulsar
from pulsar.schema import JsonSchema
from langchain_community.document_loaders import PyPDFLoader
import tempfile
import base64
import os
import argparse
import rdflib
import json
import urllib.parse
import time

from ... schema import VectorsChunk, Triple, VectorsAssociation, Source, Value
from ... log_level import LogLevel
from ... llm_client import LlmClient
from ... prompts import to_relationships
from ... rdf import RDF_LABEL, TRUSTGRAPH_ENTITIES

RDF_LABEL_VALUE = Value(value=RDF_LABEL, is_uri=True)

default_pulsar_host = os.getenv("PULSAR_HOST", 'pulsar://pulsar:6650')
default_input_queue = 'vectors-chunk-load'
default_output_queue = 'graph-load'
default_subscriber = 'kg-extract-relationships'
default_vector_queue='vectors-load'

class Processor:

    def __init__(
            self,
            pulsar_host=default_pulsar_host,
            input_queue=default_input_queue,
            vector_queue=default_vector_queue,
            output_queue=default_output_queue,
            subscriber=default_subscriber,
            log_level=LogLevel.INFO,
    ):

        self.client = pulsar.Client(
            pulsar_host,
            logger=pulsar.ConsoleLogger(log_level.to_pulsar())
        )

        self.consumer = self.client.subscribe(
            input_queue, subscriber,
            schema=JsonSchema(VectorsChunk),
        )

        self.producer = self.client.create_producer(
            topic=output_queue,
            schema=JsonSchema(Triple),
        )

        self.vec_prod = self.client.create_producer(
            topic=vector_queue,
            schema=JsonSchema(VectorsAssociation),
        )

        self.llm = LlmClient(pulsar_host=pulsar_host)

    def to_uri(self, text):

        part = text.replace(" ", "-").lower().encode("utf-8")
        quoted = urllib.parse.quote(part)
        uri = TRUSTGRAPH_ENTITIES + quoted

        return uri

    def get_relationships(self, chunk):

        prompt = to_relationships(chunk)
        resp = self.llm.request(prompt)

        rels = json.loads(resp)

        return rels

    def emit_edge(self, s, p, o):

        t = Triple(s=s, p=p, o=o)
        self.producer.send(t)

    def emit_vec(self, ent, vec):

        r = VectorsAssociation(entity=ent, vectors=vec)
        self.vec_prod.send(r)

    def run(self):

        while True:

            msg = self.consumer.receive()

            try:

                v = msg.value()
                print(f"Indexing {v.source.id}...", flush=True)

                chunk = v.chunk.decode("utf-8")

                g = rdflib.Graph()

                try:

                    rels = self.get_relationships(chunk)
                    print(json.dumps(rels, indent=4), flush=True)

                    for rel in rels:

                        s = rel["subject"]
                        p = rel["predicate"]
                        o = rel["object"]

                        s_uri = self.to_uri(s)
                        s_value = Value(value=str(s_uri), is_uri=True)

                        p_uri = self.to_uri(p)
                        p_value = Value(value=str(p_uri), is_uri=True)

                        if rel["object-entity"]: 
                            o_uri = self.to_uri(o)
                            o_value = Value(value=str(o_uri), is_uri=True)
                        else:
                            o_value = Value(value=str(o), is_uri=False)

                        self.emit_edge(
                            s_value,
                            p_value,
                            o_value
                        )

                        # Label for s
                        self.emit_edge(
                            s_value,
                            RDF_LABEL_VALUE,
                            Value(value=str(s), is_uri=False)
                        )

                        # Label for p
                        self.emit_edge(
                            p_value,
                            RDF_LABEL_VALUE,
                            Value(value=str(p), is_uri=False)
                        )

                        if rel["object-entity"]: 
                            # Label for o
                            self.emit_edge(
                                o_value,
                                RDF_LABEL_VALUE,
                                Value(value=str(o), is_uri=False)
                            )

                        self.emit_vec(s_value, v.vectors)
                        self.emit_vec(p_value, v.vectors)
                        if rel["object-entity"]: 
                            self.emit_vec(o_value, v.vectors)

                except Exception as e:
                    print("Exception: ", e, flush=True)

                print("Done.", flush=True)

                # Acknowledge successful processing of the message
                self.consumer.acknowledge(msg)

            except Exception as e:

                print("Exception: ", e, flush=True)

                # Message failed to be processed
                self.consumer.negative_acknowledge(msg)

    def __del__(self):
        self.client.close()

def run():

    parser = argparse.ArgumentParser(
        prog='kg-extract-relationships',
        description=__doc__,
    )

    parser.add_argument(
        '-p', '--pulsar-host',
        default=default_pulsar_host,
        help=f'Pulsar host (default: {default_pulsar_host})',
    )

    parser.add_argument(
        '-i', '--input-queue',
        default=default_input_queue,
        help=f'Input queue (default: {default_input_queue})'
    )

    parser.add_argument(
        '-s', '--subscriber',
        default=default_subscriber,
        help=f'Queue subscriber name (default: {default_subscriber})'
    )

    parser.add_argument(
        '-o', '--output-queue',
        default=default_output_queue,
        help=f'Output queue (default: {default_output_queue})'
    )

    parser.add_argument(
        '-l', '--log-level',
        type=LogLevel,
        default=LogLevel.INFO,
        choices=list(LogLevel),
        help=f'Output queue (default: info)'
    )

    parser.add_argument(
        '-c', '--vector-queue',
        default=default_vector_queue,
        help=f'Vector output queue (default: {default_vector_queue})'
    )

    args = parser.parse_args()

    while True:

        try:

            p = Processor(
                pulsar_host=args.pulsar_host,
                input_queue=args.input_queue,
                output_queue=args.output_queue,
                vector_queue=args.vector_queue,
                subscriber=args.subscriber,
                log_level=args.log_level,
            )

            p.run()

        except Exception as e:

            print("Exception:", e, flush=True)
            print("Will retry...", flush=True)

        time.sleep(10)


