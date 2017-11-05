#!/usr/bin/python
# check various part of a pod definition

import os
import datetime
import time
from kubernetes import client, config

config.load_kube_config( os.path.join(os.environ["HOME"], '.kube/config'))
v1 = client.CoreV1Api()
pod = v1.list_pod_for_all_namespaces()

def exist(e_name, e_value, image,limits_mem,requests_mem):
  if e_value is None and e_name == 'compare_mem':
    print("FAILED : %s in %s limits(%s)/requests(%s) memory is not the same" % (image,pod_name,limits_mem,requests_mem))
  elif e_value is None:
    print("FAILED : %s in %s no %s value" % (image,pod_name, e_name))

def has_tag(image):
  if ':' in image:
    tag = image.rsplit(':', 1)
    if tag[1] == 'latest':
      return None
    return tag[1]
  else:
    return None

def has_localhost(image):
  if 'localhost' in image:
    return image
  return None

def has_limits_cpu(image):
  if c.resources.limits is not None:
    for k_limits_cpu,v_limits_cpu in c.resources.limits.iteritems():
      if k_limits_cpu == 'cpu':
        return v_limits_cpu
  return None

def has_limits_mem(image):
  if c.resources.limits is not None:
    for k_limits_mem,v_limits_mem in c.resources.limits.iteritems():
      if k_limits_mem == 'memory':
        return v_limits_mem
  return None

def has_requests_cpu():
  if c.resources.limits is not None:
    for k_requests_cpu,v_requests_cpu in c.resources.requests.iteritems():
      if k_requests_cpu == 'cpu':
        return v_requests_cpu
  return None

def has_requests_mem():
  if c.resources.limits is not None:
    for k_requests_mem,v_requests_mem in c.resources.requests.iteritems():
      if k_requests_mem == 'memory':
        return v_requests_mem
  return None

def compare_limits_requests_mem(limits_mem,requests_mem):
  if limits_mem != requests_mem:
    return None
  return limits_mem,requests_mem

for p in pod.items:
  namespace = p.metadata.namespace
  pod_name = p.metadata.name
  node_selector = p.spec.node_selector
  for c in p.spec.containers:
    liveness = c.liveness_probe
    readiness = c.readiness_probe
    image = c.image
    limits_cpu = has_limits_cpu(image)
    limits_mem = has_limits_mem(image)
    requests_cpu = has_requests_cpu()
    requests_mem = has_requests_mem()
    compare_mem = compare_limits_requests_mem(limits_mem,requests_mem)
    version = has_tag(image)
    localhost = has_localhost(image)
    element_name = []
    element_value = []
    element_name = ['pod_name', 'namespace', 'node_selector','version','readiness', 'liveness', 'localhost', 'limits_cpu', 'limits_mem', 'requests_cpu','requests_mem','compare_mem']
    element_value = [pod_name, namespace, node_selector, version, liveness, localhost,limits_mem,requests_cpu,requests_mem]
    for e_name, e_value in zip(element_name, element_value):
      exist(e_name, e_value,image,limits_mem,requests_mem)
