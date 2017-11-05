#!/usr/bin/python

import os
from kubernetes import client, config

ns = "oneinfo"

def print_endpoint_member(endpoint, ns):
  print endpoint
  endp = v1.read_namespaced_endpoints(endpoint, ns)
  for s in endp.subsets:
    if s.addresses == None:
      continue
    for addr in s.addresses:
      print " ", addr.ip
    for port in s.ports:
      print " ", port.port, port.protocol


config.load_kube_config( os.path.join(os.environ["HOME"], '.kube/config'))
v1 = client.CoreV1Api()

endpts = v1.list_endpoints_for_all_namespaces()
for endpt in endpts.items:
  print_endpoint_member(endpt.metadata.name, endpt.metadata.namespace)
