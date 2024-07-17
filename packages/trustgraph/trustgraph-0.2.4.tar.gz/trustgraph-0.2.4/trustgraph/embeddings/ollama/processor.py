
"""
Embeddings service, applies an embeddings model selected from HuggingFace.
Input is text, output is embeddings vector.
"""

import pulsar
from pulsar.schema import JsonSchema
import tempfile
import base64
import os
import argparse
from langchain_community.embeddings import OllamaEmbeddings
import time

from ... schema import EmbeddingsRequest, EmbeddingsResponse
from ... log_level import LogLevel

default_pulsar_host = os.getenv("PULSAR_HOST", 'pulsar://pulsar:6650')
default_input_queue = 'embeddings'
default_output_queue = 'embeddings-response'
default_subscriber = 'embeddings-ollama'
default_model="mxbai-embed-large"
default_ollama = 'http://localhost:11434'

class Processor:

    def __init__(
            self,
            pulsar_host=default_pulsar_host,
            input_queue=default_input_queue,
            output_queue=default_output_queue,
            subscriber=default_subscriber,
            log_level=LogLevel.INFO,
            model=default_model,
            ollama=default_ollama,
    ):

        self.client = None

        self.client = pulsar.Client(
            pulsar_host,
            logger=pulsar.ConsoleLogger(log_level.to_pulsar())
        )

        self.consumer = self.client.subscribe(
            input_queue, subscriber,
            schema=JsonSchema(EmbeddingsRequest),
        )

        self.producer = self.client.create_producer(
            topic=output_queue,
            schema=JsonSchema(EmbeddingsResponse),
        )

        self.embeddings = OllamaEmbeddings(base_url=ollama, model=model)

    def run(self):

        while True:

            msg = self.consumer.receive()

            try:

                v = msg.value()

	        # Sender-produced ID

                id = msg.properties()["id"]

                print(f"Handling input {id}...", flush=True)

                text = v.text
                embeds = self.embeddings.embed_query([text])

                print("Send response...", flush=True)
                r = EmbeddingsResponse(vectors=[embeds])

                self.producer.send(r, properties={"id": id})

                print("Done.", flush=True)

                # Acknowledge successful processing of the message
                self.consumer.acknowledge(msg)

            except Exception as e:

                print("Exception:", e, flush=True)

                # Message failed to be processed
                self.consumer.negative_acknowledge(msg)

    def __del__(self):

        if self.client:
            self.client.close()

def run():

    parser = argparse.ArgumentParser(
        prog='embeddings-ollama',
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
        '-m', '--model',
        default=default_model,
        help=f'Embeddings model (default: {default_model})'
    )

    parser.add_argument(
        '-r', '--ollama',
        default=default_ollama,
        help=f'ollama (default: {default_ollama})'
    )

    args = parser.parse_args()

    
    while True:

        try:

            p = Processor(
                pulsar_host=args.pulsar_host,
                input_queue=args.input_queue,
                output_queue=args.output_queue,
                subscriber=args.subscriber,
                log_level=args.log_level,
                model=args.model,
                ollama=args.ollama,
            )

            p.run()

        except Exception as e:

            print("Exception:", e, flush=True)
            print("Will retry...", flush=True)

        time.sleep(10)

