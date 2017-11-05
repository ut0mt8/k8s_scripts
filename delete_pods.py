#!/usr/bin/python
# utility script to delete all matching pods

import argparse
import os
import time
from kubernetes import client, config
from kubernetes.client.rest import ApiException

def list_pod(podname):
  pod_list = []
  pods = v1.list_pod_for_all_namespaces()
  for p in pods.items:
    if p.metadata.name.startswith(podname):
      pod_list.append(p.metadata.namespace+":"+p.metadata.name)
  return pod_list

def delete_pod(pns, pname):
  try:
    rep = v1.delete_namespaced_pod(pname, pns, client.V1DeleteOptions(), grace_period_seconds=0)
    print ("Pod %s:%s Deleted." % (pns, pname))
  except ApiException as e:
    print("Job %s:%s deletion failed: %s" % (pns, pname, e))


if __name__ == '__main__':

  parser = argparse.ArgumentParser()
  parser.add_argument('pod_name')
  args = parser.parse_args()

  config.load_kube_config( os.path.join(os.environ["HOME"], '.kube/config'))
  v1 = client.CoreV1Api()

  for pod in list_pod(args.pod_name):
    (pns, pname) = pod.split(':')
    delete_pod(pns, pname)
    time.sleep(1)
    
