#!/usr/bin/python
# check liveness probe of each containers

import os
import requests
from kubernetes import client, config

config.load_kube_config( os.path.join(os.environ["HOME"], '.kube/config'))
v1 = client.CoreV1Api()

pods = v1.list_pod_for_all_namespaces()
for p in pods.items:
  # test ready state for pod
  if p.status.conditions[1].status != 'True':
    continue
  ready = True
  # test ready state for each container in pod
  for cs in p.status.container_statuses:
    pass
  if not ready:
    continue
  for c in p.spec.containers:
    if c.liveness_probe:
      restart_count = 0
      for cs in p.status.container_statuses:
        if cs.name == c.name:
          restart_count = cs.restart_count
      status = 'FAILED'
      url = 'http://'+p.status.pod_ip+':'+str(c.liveness_probe.http_get.port)+c.liveness_probe.http_get.path
      try:
        r = requests.get(url)
        if r.status_code == 200 or r.status_code == 204:
          status = 'OK'
      except:
        pass
      print("%s %s %s:%s:%s %s:%s" % (
        status, restart_count, p.metadata.namespace, p.metadata.name, c.name,
        c.liveness_probe.http_get.path, c.liveness_probe.http_get.port))
