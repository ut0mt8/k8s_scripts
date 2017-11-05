#!/usr/bin/python
# drain the whole cluster aka
# 1) cordon node
# 2) delete all pod on it (except critical one)
# 3) uncordon node

import os
import time
from kubernetes import client, config
from kubernetes.client.rest import ApiException

v1node = client.V1Node()
v1node_spec = client.V1NodeSpec()
v1node.spec = v1node_spec


def list_pod_node(nodename):
  pod_list = []
  pods = v1.list_pod_for_all_namespaces()
  for p in pods.items:
    if p.metadata.namespace == "kube-system":
      continue
    if p.spec.node_name != nodename:
      continue
    pod_list.append(p.metadata.namespace+":"+p.metadata.name)
  return pod_list

def delete_pod_node(node, pod_list):
  for pod in pod_list:
    print "Deleting pod %s in node %s" % (pod, node)
    (pns, pname) = pod.split(':')
    delete_pod(pns, pname)

def delete_pod(pns, pname):
  try:
    rep = v1.delete_namespaced_pod(pname, pns, client.V1DeleteOptions(), grace_period_seconds=0)
    print ("Pod %s:%s Deleted." % (pns, pname))
  except ApiException as e:
    print("Job %s:%s deletion failed: %s" % (pns, pname, e))

def drain_node(nodename):
  cordon_node(nodename)
  pod_list = list_pod_node(nodename)
  delete_pod_node(nodename, pod_list)
  while pod_list:
    pod_list = list_pod_node(nodename)
    print "Waiting for pods termination in node %s" % (nodename)
    print pod_list
    time.sleep(3)
  uncordon_node(nodename)

def cordon_node(nodename):
  try: 
    v1node.spec.unschedulable = True
    res = v1.patch_node(nodename, v1node)
  except ApiException as e:
    print("Error cordon node %s : %s\n" % (node, e))
    return False
  print("Cordon node %s succeed" % nodename)
  return True

def uncordon_node(nodename):
  try: 
    v1node.spec.unschedulable = False
    res = v1.patch_node(nodename, v1node)
  except ApiException as e:
    print("Error uncordon node %s : %s\n" % (node, e))
    return False
  print("Uncordon node %s succeed" % nodename)
  return True


if __name__ == '__main__':

  config.load_kube_config( os.path.join(os.environ["HOME"], '.kube/config'))
  v1 = client.CoreV1Api()

  nodes = v1.list_node()
  for node in nodes.items:
    sched = "OK"
    if node.spec.unschedulable:
      sched = "No"
    if sched != "No":
      print("Draining node: %s" % node.metadata.name)
      drain_node(node.metadata.name)
      time.sleep(5)
    else:
      print("Not draining node: %s, as it was already unschedulable" % node.metadata.name)
    
