#!/usr/bin/env python

# Draw a scatterplot of a given metric from the Basis smartwatch
# Data must be in data/, written by basis_retriever.py
# Requires matplotlib

# @author: Scott McCool <scott@mccool.com>

import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
import datetime
import sys

if len(sys.argv) > 1:
    metric_name = sys.argv[1]
else:
    metric_name = 'heartrate'
    print "No metric passed, using heartrate"

metric_vals=[] # Store (time,value) tuples parsed from json
for f in os.listdir('./data/'):
    daygraph_metric_vals=[]
    if f.endswith('.json'):
        plt.close('all')
        today = f.split('.')[0][11:]
        print "Processing: %s" % f
        jd=json.load(open('./data/'+f,'r'))
        mtime=jd['starttime']
        endtime=jd['endtime']
        offset = (1 + (endtime - mtime)) / len(jd['metrics']['steps']['values'])
        if metric_name not in jd['metrics']:
            print "Could not find %s in data file (%s)" % (metric_name, f)
            continue
        for v in jd['metrics'][metric_name]['values']:
            if v != None:
                dto=datetime.datetime.fromtimestamp(mtime)
                metric_vals.append((dto,v))
                daygraph_metric_vals.append((dto,v))
            mtime += offset
        if len(daygraph_metric_vals) > 0:
            dp = plt.scatter(*zip(*daygraph_metric_vals), marker=',')
            plt.setp(plt.xticks()[1],rotation=30,ha='right')
            plt.xlim(datetime.datetime.fromtimestamp(jd['starttime']),datetime.datetime.fromtimestamp(jd['endtime']))
            plt.Axes.format_xdata = mdates.DateFormatter('%Y-%m-%d %H:%M')
            plt.title('%s for %s' % (metric_name, today))
            plt.xlabel('Time')
            plt.savefig('graphs/%s_%s.png' % ( metric_name, today))

plt.close('all')
if len(metric_vals) > 0:
    p = plt.scatter(*zip(*metric_vals), marker=',', vmin=40,vmax=180, s=100)
    plt.title('%s over time' % (metric_name))
    plt.xlabel('Timesetamp')
    plt.savefig('graphs/%s_all_time.png' % metric_name)

