#!/usr/bin/python

import os
from kubernetes import client, config

config.load_kube_config( os.path.join(os.environ["HOME"], '.kube/config'))

v1 = client.CoreV1Api()

pods = v1.list_pod_for_all_namespaces()
for p in pods.items:
    print("Pod: %s:%s\t%s, %s\t%s" % (p.metadata.namespace, p.metadata.name, p.status.pod_ip, p.status.host_ip, p.status.phase))
    for c in p.spec.containers:
      ready = "notready"
      for cstatus in p.status.container_statuses:
        if cstatus.name == c.name:
          if cstatus.ready == True:
            ready = "ready"
      print("\tContainer: %s %s" % (c.name, ready))
