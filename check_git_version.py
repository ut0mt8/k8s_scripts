#!/usr/bin/python
# script to compare version running in production and commited
# deployments end with -depl.yaml

import os
import collections
import requests
import yaml
from addict import Dict
from kubernetes import client, config

# list of project to watch
projects = ['project']

# github api url
gh_url = 'http://github.corp/api/v3/'

# github information 
token = 'xxxxxxxxxxxx'
user = 'user'
repo = 'kubernetes'
path = '/production/'


def gh_get_all_files(repo, project):
  files = []
  headers = {'Authorization': 'token %s' % token}
  url = gh_url + 'repos/' + user + '/' + repo + '/git/trees/master?recursive=1'
  r = requests.get(url, headers=headers)
  j = Dict(r.json())
  for tree in j.tree:
    if project+path in tree.path:
      files.append(tree.path)
  return files

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

def gh_get_image_version(ymlfile):
  img_containers = {}
  yml = gh_get_raw_file(ymlfile)
  if yml:
    pod_def = Dict(yaml.load(yml))
    if pod_def.kind in ['Deployment', 'PetSet', 'DaemonSet']:
      for c in pod_def.spec.template.spec.containers:
        img_containers[c.name] = c.image
  return img_containers

def compare_version(project, k8s_containers, gh_containers):
  k8s_containers_sorted = collections.OrderedDict(sorted(k8s_containers.items()))
  for cname, imgver in k8s_containers_sorted.items():
    if cname not in gh_containers:
      print "%s:%s %s, version not found in git : Failed" % (project, cname, imgver)
    elif imgver != gh_containers[cname]:
      print "%s:%s %s, %s, version differ : Failed" % (project, cname, imgver, gh_containers[cname])
    else:
      print "%s:%s %s, same version : OK" % (project, cname, imgver)


config.load_kube_config( os.path.join(os.environ["HOME"], '.kube/config'))
v1 = client.CoreV1Api()

for project in projects:
  gh_containers = Dict()
  k8s_containers = Dict()

  # get containers/images version from github
  for f in gh_get_all_files(repo, project):
    if f.endswith('-depl.yaml'):
      for cname, imgver in gh_get_image_version(f).iteritems():
        if cname not in gh_containers:
          gh_containers[cname] = imgver

  # get containers/images version from k8s cluster
  pods = v1.list_namespaced_pod(project)
  for p in pods.items:
    created_by = p.metadata.annotations['kubernetes.io/created-by']
    # try to exclude job
    if "ReplicaSet" not in created_by and "PetSet" not in created_by:
      continue
    if "-job" in p.metadata.name:
      continue
    for c in p.spec.containers:
      if c.name not in k8s_containers:
        k8s_containers[c.name] = c.image

  compare_version(project, k8s_containers, gh_containers)


