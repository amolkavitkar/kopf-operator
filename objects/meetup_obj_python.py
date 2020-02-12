# ----------------------------------------------------------------------------
# Copyright (c) 2020 amol kavitkar
# ----------------------------------------------------------------------------
import json
import logging
import time
import sys

from kubernetes import client, config

formatter = " %(asctime)s | %(levelname)-6s | %(process)d | %(threadName)-12s |" \
            " %(thread)-15d | %(name)-30s | %(filename)s:%(lineno)d | %(message)s |"

handler = logging.StreamHandler(sys.stdout)
# logging.basicConfig(format=formatter)
logger = logging.getLogger("CRDApi")
logger.setLevel(level=logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


K8S_NAMESPACE = "meetup"
K8S_GROUP = "meetup.com"
K8S_OPERATOR_VERSION = "v1"
K8S_MAX_API_RETRY_COUNT = 5
K8S_API_RETRY_DELAY = 5
K8S_CHECK_RETRY_COUNT = 5


def _get_crd_client():
    #config.load_incluster_config()
    config.load_kube_config()
    return client.CustomObjectsApi()


class CRDCustomApi(object):

    def __init__(self):
        self.crd_client = _get_crd_client()

    def create_custom_object(self, namespace, crd_name_plural, object_json, group=K8S_GROUP,
                             version=K8S_OPERATOR_VERSION):
        logger.info("Custom object creation triggered for {}".format(crd_name_plural))
        self.crd_client.create_namespaced_custom_object(group, version, namespace, crd_name_plural, object_json)
        logger.info("Custom object creation completed for {}".format(crd_name_plural))

    def delete_custom_object(self, namespace, crd_name_plural, name, object_json=None, group=K8S_GROUP,
                             version=K8S_OPERATOR_VERSION, wait=False):
        if not object_json:
            object_json = client.V1DeleteOptions()
            object_json.grace_period_seconds = 0
            object_json.propagation_policy = 'Foreground'
        logger.info("Delete object params are %s %s %s", namespace, crd_name_plural, name)
        self.crd_client.delete_namespaced_custom_object(group, version, namespace, crd_name_plural, name, object_json)
        if not wait:
            return

        for _ in range(K8S_MAX_API_RETRY_COUNT):
            try:
                self.get_custom_object(namespace, crd_name_plural, name)
            except Exception as ec:
                logger.info("custom object %s is deleted", name)
                return
            logger.info("Custom object is not deleted, retrying check in %s seconds", K8S_API_RETRY_DELAY)
            time.sleep(K8S_API_RETRY_DELAY)
        else:
            logger.error("The object %s is not deleted", name)
            raise Exception("The object {} is not deleted".format(name))

    def get_custom_object(self, namespace, crd_name_plural, object_name, group=K8S_GROUP,
                          version=K8S_OPERATOR_VERSION):
        logger.info("Custom object deletion triggered for {}".format(crd_name_plural))
        return self.crd_client.get_namespaced_custom_object(group=group, version=version, namespace=namespace,
                                                            plural=crd_name_plural, name=object_name)

        logger.info("Custom object deletion completed for {}".format(crd_name_plural))


def main():
    crd_obj = CRDCustomApi()
    crd_meetup_template = {
                            "apiVersion": "meetup.com/v1",
                            "kind": "MeetUpOp",
                            "metadata": {
                                "name": "my-meetup-api",
                                "namespace": "meetup"
                                },
                            }
    # logger.info("Creating custom object with {}".format(crd_meetup_template))
    # crd_obj.create_custom_object("meetup", "meetupops", crd_meetup_template)

    logger.info("Deleting custom object with {}".format(crd_meetup_template))
    crd_obj.delete_custom_object("meetup", "meetupops", "my-meetup-api", wait=True)


if __name__ in ["__main__", "main"]:
    main()

