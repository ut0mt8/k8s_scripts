#!/usr/bin/python
# check if all service have at least one endpoint

import os
from kubernetes import client, config

config.load_kube_config( os.path.join(os.environ["HOME"], '.kube/config'))
v1 = client.CoreV1Api()

endpoints = v1.list_endpoints_for_all_namespaces()
for e in endpoints.items:
  if e.metadata.namespace == 'kube-system':
    continue
  endpt = 0
  for s in e.subsets:
    if s.addresses == None:
      continue
    for a in s.addresses:
      if a.ip != None:
        endpt += 1
  if endpt:
    print("OK: %d endpoints found %s:%s service" % (endpt, e.metadata.namespace, e.metadata.name))
  else:
    print("FAILED: no endpoints for %s:%s service" % (e.metadata.namespace, e.metadata.name))
