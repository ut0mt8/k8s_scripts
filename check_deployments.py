#!/usr/bin/python
# check all deployment checking available pods = desired

import os
from kubernetes import client, config

config.load_kube_config( os.path.join(os.environ["HOME"], '.kube/config'))
v1 = client.ExtensionsV1beta1Api()
depls = v1.list_deployment_for_all_namespaces()

for d in depls.items:
  ns = d.metadata.namespace
  name = d.metadata.name
  available_repl = d.status.available_replicas
  desired_repl = d.status.replicas
  if available_repl != desired_repl:
    print("FAILED: %s:%s, %s desired/%s available" % (ns, name, desired_repl, available_repl))
  else:
    print("OK: %s:%s, %s desired/%s available" % (ns, name, desired_repl, available_repl))
