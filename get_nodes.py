#!/usr/bin/python

import os
from kubernetes import client, config

config.load_kube_config( os.path.join(os.environ["HOME"], '.kube/config'))
v1 = client.CoreV1Api()

nodes = v1.list_node()
for node in nodes.items:
  project = "All"
  sched = "OK"
  status = "NotReady"
  if 'project' in node.metadata.labels:
    project =  node.metadata.labels['project']
  if node.spec.unschedulable:
    sched = "No"
  for cond in node.status.conditions:
    if cond.type == "Ready" and cond.status == "True":
      status = "Ready"
      last_seen = cond.last_heartbeat_time
  print("%s \t sched: %s, status: %s, lastseen: %s, project: %s" % (node.metadata.name, sched, status, last_seen, project))
