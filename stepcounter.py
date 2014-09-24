#!/usr/bin/env python

import traceback
import json
import os

stepdata = []
for i in os.listdir(os.getcwd() + '/data/'):
    if not (i.startswith('basis-data') and i.endswith('.json')):
        continue
    try:
        jd = json.load(open('data/' + i, 'r'))
        try:
            steps = jd['metrics']['steps']['sum']
        except:
            steps = 0
            for s in jd['metrics']['steps']['values']:
                steps += int(s)
        d = i.lstrip('basis-data-').rstrip('.json')
        stepdata.append((d, steps))
    except:
        print "          * Skipping %s" % (i)
        traceback.print_exc()

print "Date    | Steps"
print "---------------"
maxsteps = (None, 0)
for d, s in stepdata:
    if s > maxsteps[1]:
        maxsteps = (d, s)
    print "%s: %s" % (d, s)
print "Your maximum number of steps was %s on %s" % (maxsteps[1], maxsteps[0])
