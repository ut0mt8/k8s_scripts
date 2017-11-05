#!/usr/bin/python

import os
from kubernetes import client, config

config.load_kube_config( os.path.join(os.environ["HOME"], '.kube/config'))
v1 = client.CoreV1Api()

node_pods = {}
pods = v1.list_pod_for_all_namespaces()
for p in pods.items:
    node_pods.setdefault(p.spec.node_name, []).append(p.metadata.namespace+":"+p.metadata.name)

nodes = v1.list_node()
for node in nodes.items:
  print("%s:" % node.metadata.name)
  if node.metadata.name in node_pods:
    for pod in node_pods[node.metadata.name]:
      print("  - %s" % pod)
