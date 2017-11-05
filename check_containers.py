#!/usr/bin/python
# check state of all pods/containers

import os
from kubernetes import client, config

config.load_kube_config( os.path.join(os.environ["HOME"], '.kube/config'))
v1 = client.CoreV1Api()
pods = v1.list_pod_for_all_namespaces()

for p in pods.items:
  ns = p.metadata.namespace
  pod_name = p.metadata.name
  status = p.status
  container_statuses = p.status.container_statuses
  if type(container_statuses) is list:
    for cs in container_statuses:
      cname = cs.name
      state = cs.state
      if state.terminated is not None and state.terminated is not 'ContainerCreating':
        terminated_reason = state.terminated.reason
        print("FAILED: %s:%s:%s, status %s" % (ns, pod_name, cname, terminated_reason))
      elif state.waiting is not None and state.terminated is not 'ContainerCreating':
        waiting_reason = state.waiting.reason
        print("FAILED: %s:%s:%s, status %s" % (ns, pod_name, cname, waiting_reason))
      else:
        print("OK: %s:%s:%s, status running" % (ns, pod_name, cname))
