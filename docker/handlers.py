# ----------------------------------------------------------------------------
# Copyright (c) 2020 amol kavitkar
# ----------------------------------------------------------------------------
import logging

import kopf
from kubernetes import client, config

formatter = " %(asctime)s | %(levelname)-6s | %(process)d | %(threadName)-12s |" \
            " %(thread)-15d | %(name)-30s | %(filename)s:%(lineno)d | %(message)s |"
logging.basicConfig(format=formatter)
logger = logging.getLogger("Meetup-Operator")
logger.setLevel(level=logging.DEBUG)


def _get_kube_v1_client():
    config.load_incluster_config()
    return client.CoreV1Api()


@kopf.on.create("meetup.com", "v1", "meetupops")
def create_fn(body, spec, **kwargs):
    name = body['metadata']['name']
    namespace = body['metadata']['namespace']

    v1_client = _get_kube_v1_client()

    NGNIX_JSON_TEMPLATE = {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {
            "name": name,
            "nameapce": namespace
        },
        "spec": {
            "containers": [
                {
                    "name": "nginx",
                    "image": "nginx",
                    "ports": [
                        {
                            "containerPort": 80
                        }
                    ]
                }
            ]
        }
    }

    # Make the Pod children of opearator
    kopf.adopt(NGNIX_JSON_TEMPLATE, owner=body)

    # Create Pod
    obj = v1_client.create_namespaced_pod(namespace, NGNIX_JSON_TEMPLATE)
    logger.info("%s pod created", obj.metadata.name)

    return {'message': "NGNIX pod created"}


@kopf.on.create("meetup.com", "v1", "meetupops")
def delete(body, **kwargs):
    msg = "operator {} and its children deleted".format(body['metadata']['name'])
    return {'message': msg}

