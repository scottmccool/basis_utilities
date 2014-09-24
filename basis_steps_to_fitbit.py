#!/usr/bin/env python

import traceback
import json
import os
import datetime
import fitbit
import time
import sys
import pprint
hr_metrics = []  # Store (time,value) tuples parsed from json
step_data = []

# Must take at least 10 steps to count as a walk period
MIN_STEPS_MINUTE_TO_COUNT = 10
MAX_LOW_INTERVALS_TO_END_PERIOD = 3  # Must not stop for more then 3 minutes
MIN_STEPS_TO_COUNT = 100

try:
    config = json.loads(open('.basis_retriever.cfg', 'r').read())
    FB_CONSUMER_KEY = config['fitbit']['consumer_key']
    FB_CONSUMER_SECRET = config['fitbit']['consumer_secret']
    FB_RESOURCE_OWNER_KEY = config['fitbit']['resource_owner_key']
    FB_RESOURCE_OWNER_SECRET = config['fitbit']['resource_owner_secret']
except:
    print "Could not open config file, please create .basis_retriever.cfg"
    print "and include at least the \"fitbit\" section."
    print "Format: "
    print """
    {
      "basis": {
        "username": "<your mybasis.com username>",
        "password": "<your mybasis.com password>"
      },
      "fitbit": {
        "consumer_key": "<your fitbit consumer key>",
        "consumer_secret": <your fitbit consumer secret>",
        "resource_owner_key": <fitbit resource owner key>",
        "resource_owner_secret": <fitbit resource owner secret>""
      }
    }
    """
    traceback.print_exc()
    sys.exit(1)

FB_TOKEN_REQ_URL = 'https://api.fitbit.com/oauth/request_token'
FB_TOKEN_ACCESS_URL = 'https://api.fitbit.com/oauth/access_token'
FB_AUTHORIZE_URL = 'https://www.fitbit.com/oauth/authorize'
 # from ./gather_keys_cli.py
# FB_WALKING_ACTIVITY=90013
FB_WALKING_ACTIVITY = 17200

today = time.strftime('%Y-%m-%d')
if len(sys.argv) > 1:
    d = sys.argv[1]
else:
    d = today
f = "data/basis-data-%s.json" % (d)

try:
    jd = json.load(open(f, 'r'))
except:
    print "Exception loading data file (%s)" % (f)
    traceback.print_exc()
    sys.exit(1)

activity_data = []
# steps_str=jd['metrics']['steps']['sum']
data_start = int(jd['starttime'])
data_end = int(jd['endtime'])
data_interval = (1 + (data_end - data_start)) / \
    len(jd['metrics']['steps']['values'])
step_data = []
    # Split into walks
in_current_walk = False
walk_steps = 0
walk_start = 0
walk_end = 0
strikes = 0
for counter, s in enumerate(jd['metrics']['steps']['values']):
    try:
        steps = int(s)
    except:
        steps = 0
    if steps < MIN_STEPS_MINUTE_TO_COUNT:
        strikes += 1
        # end this walk
        if in_current_walk and strikes >= MAX_LOW_INTERVALS_TO_END_PERIOD:
            walk_end = data_start + (counter * data_interval)
            in_current_walk = False
            if walk_steps > MIN_STEPS_TO_COUNT:
                step_data.append((walk_start, walk_end, walk_steps))
            walk_start = 0
            walk_end = 0
            walk_steps = 0
    else:
        strikes = 0  # Reset strike counter if we had steps this minute
        in_current_walk = True
        if walk_start == 0:
            walk_start = data_start + (counter * data_interval)
        walk_steps += steps

print "Here are your walks for %s:" % (d)
for start, end, steps in step_data:
    d = datetime.datetime.fromtimestamp(start)
    s = d.strftime("%H:%M")
    d = datetime.datetime.fromtimestamp(end)
    e = d.strftime("%H:%M")
    print "%s - %s: %d" % (s, e, steps)
try:
    authd_client = fitbit.Fitbit(FB_CONSUMER_KEY, FB_CONSUMER_SECRET,
                                 resource_owner_key=FB_RESOURCE_OWNER_KEY, resource_owner_secret=FB_RESOURCE_OWNER_SECRET)
except:
    print "Exception connecting to fitbit"
    traceback.print_exc()

# print "Browsing acts"
# a=authd_client.activities_list()
# pprint.pprint(a)

for start, end, steps in step_data:
    start_date = time.strftime('%Y-%m-%d', time.localtime(start))
    start_time = time.strftime('%H:%M', time.localtime(start))
    duration_millis = 1000 * (end - start)
    try:
        activity_data = dict(
            activityId=FB_WALKING_ACTIVITY, distance=steps, distanceUnit='Steps',
            date=start_date,  startTime=start_time, durationMillis=duration_millis)
        authd_client.log_activity(activity_data)
        print "Posted walking data to fitbit for %s (%s)" % (start_date, start_time)
    except:
        print "Exception posting data to fitbit, sleeping for 1 hour and retrying once" % (activity_data)
        print activity_data
        traceback.print_exc()
        time.sleep(60 * 60)
        activity_data = dict(
            activityId=FB_WALKING_ACTIVITY, distance=steps, distanceUnit='Steps',
            date=start_date,  startTime=start_time, durationMillis=duration_millis)
        try:
            authd_client.log_activity(activity_data)
            print "Posted walking data to fitbit for %s (%s)" % (start_date, start_time)
        except:
            print "Another exception, bombing out, sorry (today was %s)" % (today)
            traceback.print_exc()
            sys.exit(1)

# x=0
# for activity in activity_data:
#    x+=1
#    if x > 10:
#        print "Pausing after %d runs" % x
#        time.sleep(1)
#        x=0
#    d=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(activity[0]))
#    s=activity[2]
#    print "Date: %s, Steps: %d" % (d,s)
#    start_date = time.strftime('%Y-%m-%d', time.localtime(activity[0]))
#    start_time = time.strftime('%H:%M', time.localtime(activity[0]))
#    duration_millis = 1000 * ( activity[1] - activity[0])
# Post to fitbit: activityId=90013, d
##    unauth_client = fitbit.Fitbit(FB_CONSUMER_KEY,FB_CONSUMER_SECRET)
#    try:
#        activity_data = dict(activityId=FB_WALKING_ACTIVITY, distance=s, distanceUnit='Steps', date=start_date,  startTime=start_time, durationMillis=duration_millis)
#        authd_client.log_activity(activity_data)
#        print "Posted walking data to fitbit for %s" % (d)
##        cont=raw_input("Enter to continue")
#    except:
#        print "Exception posting data"
#        traceback.print_exc()
