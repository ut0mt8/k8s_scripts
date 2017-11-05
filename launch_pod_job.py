#!/usr/bin/python
# utility script to launch "job" pod directly from yaml def stored in git

import os
import sys
import time
import requests
import yaml
from addict import Dict
from kubernetes import client, config, watch
from kubernetes.client.rest import ApiException

# github url
gh_url = 'http://github.corp/api/v3/'

# github informations
token = 'xxxxx'
user = 'user'
repo = 'kubernetes'

def gh_get_raw_file(yaml):
  headers = {'Authorization': 'token %s' % token}
  url = gh_url + 'repos/' + user + '/' + repo + '/contents/' + yaml
  r = requests.get(url, headers=headers)
  if r.status_code == requests.codes.ok:
    j = Dict(r.json())
    r = requests.get(j.download_url, headers=headers)
    return r.text
  else:
    return None

def wait_end_pod():
  rcode = 0
  w = watch.Watch()
  for event in w.stream(api.list_namespaced_pod, pns):
    etype = event['type']
    ename = event['object'].metadata.name 
    if ename == pname:
      status = event['object'].status
      if etype == 'ADDED':
        print ("Pod %s:%s Created." % (pns, pname))
      elif etype == 'MODIFIED' and status.phase == 'Succeeded':
        print ("Pod %s:%s %s." % (pns, pname, status.phase))
        rcode = status.container_statuses[0].state.terminated.exit_code
        w.stop()
      elif etype == 'MODIFIED' and status.phase == 'Failed':
        print ("Pod %s:%s %s." % (pns, pname, status.phase))
        rcode = status.container_statuses[0].state.terminated.exit_code
        w.stop()
      elif etype == 'MODIFIED' and status.phase:
        print ("Pod %s:%s %s." % (pns, pname, status.phase))
  return rcode

def delete_pod(pname, pns):
  try:
    rep = api.delete_namespaced_pod(pname, pns, client.V1DeleteOptions(), grace_period_seconds=0)
    print ("Pod %s:%s Deleted." % (pns, pname))
  except ApiException as e:
    print("Pod %s:%s Deletion failed: %s." % (pns, pname, e))
    sys.exit(2)

def end_pod(pname, pns):
    pods = api.list_namespaced_pod(pns)
    for p in pods.items:
      if pname in p.metadata.name:
        rlog = api.read_namespaced_pod_log(p.metadata.name, pns)
        print("Log:\n%s" % rlog)
        delete_pod(p.metadata.name, pns)

def delete_old_pod(pname, pns):
    pods = api.list_namespaced_pod(pns)
    for p in pods.items:
      if pname in p.metadata.name:
        print("Pod %s:%s %s. already there. Cleaning it." % (pns, p.metadata.name, p.status.phase))
        delete_pod(p.metadata.name, pns)
        time.sleep(3)

if __name__ == '__main__':
  if len(sys.argv) != 2:
    print("Usage %s <github_path>" % sys.argv[0])
    sys.exit(2)

  ymlfile = sys.argv[1]
  yml = gh_get_raw_file(sys.argv[1])
  if not yml:
    print("yaml file %s not found in github" % ymlfile)
    sys.exit(2)

  config.load_kube_config(os.path.join(os.environ["HOME"], '.kube/config'))

  pod_def = Dict(yaml.load(yml)) 
  pname = pod_def.metadata.name
  pns = pod_def.metadata.namespace
  pbody = pod_def.to_dict()

  try:
    api = client.CoreV1Api()
    delete_old_pod(pname, pns)
    rep = api.create_namespaced_pod(pns, body=pbody)
    rcode = wait_end_pod()
    end_pod(pname, pns)
    sys.exit(rcode)
  except ApiException as e:
    print("Pod %s:%s creation failed: %s" % (pns, pname, e))
    sys.exit(2)

