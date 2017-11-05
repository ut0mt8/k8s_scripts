#!/usr/bin/python
# check number of restart of pods
# add option to delete it to clear the counter

import argparse
import collections
import os
import requests
from kubernetes import client, config

parser = argparse.ArgumentParser()
parser.add_argument('-v', action='store_true')
parser.add_argument('-delete', action='store_true')
args = parser.parse_args()

epods = {}
config.load_kube_config( os.path.join(os.environ["HOME"], '.kube/config'))
v1 = client.CoreV1Api()

pods = v1.list_pod_for_all_namespaces()
for p in pods.items:
  for c in p.spec.containers:
    if not p.status.container_statuses:
      continue
    for cs in p.status.container_statuses:
      if cs.restart_count > 0:
        if cs.name == c.name:
          epods[p.metadata.name] = p.metadata.namespace
          print '#', p.metadata.namespace, p.metadata.name, c.name, cs.restart_count, p.spec.node_name
          if not cs.last_state.terminated :
            print "=> Unknown reason"
          else:
            print "=>", cs.last_state.terminated.reason, cs.last_state.terminated.finished_at
            if args.v and cs.last_state.terminated.reason in ["Completed", "Error"]:
              print "Output log:"
              log = v1.read_namespaced_pod_log(p.metadata.name, p.metadata.namespace, container=c.name, previous=True, tail_lines=30)
              print '--\n',log,'--'
 
if args.delete:
  spods = collections.OrderedDict(sorted(epods.items()))
  for i, (pname, pns) in enumerate(spods.iteritems()):
    try:
      rep = v1.delete_namespaced_pod(pname, pns, client.V1DeleteOptions(), grace_period_seconds=0)
      print ("Pod %s:%s Deleted." % (pns, pname))
    except ApiException as e:
      print("Pod %s:%s deletion failed: %s" % (pns, pname, e))
