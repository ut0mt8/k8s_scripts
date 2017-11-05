#!/usr/bin/python
# check if a pod is in ContainerCreating state for too long

import os
import datetime
import time
from kubernetes import client, config

config.load_kube_config( os.path.join(os.environ["HOME"], '.kube/config'))
v1 = client.CoreV1Api()
pods = v1.list_pod_for_all_namespaces()

for p in pods.items:
  status = p.status.phase
  if status == "ContainerCreating":
    start_time = p.status.start_time
    date_now_format = (time.strftime("%Y-%m-%d %H:%M:%S"))
    start_time_format = (start_time.strftime("%Y-%m-%d %H:%M:%S"))
    date_now_stamp = time.mktime(datetime.datetime.strptime(date_now_format, "%Y-%m-%d %H:%M:%S").timetuple())
    start_time_stamp = time.mktime(datetime.datetime.strptime(start_time_format, "%Y-%m-%d %H:%M:%S").timetuple())
    since_created_stamp = date_now_stamp-start_time_stamp
    if since_created_stamp > 600:
      print("FAILED: %s:%s in ContainerCreating since %s second" % (p.metadata.namespace, p.metadata.name, since_created_min))
