#!/usr/bin/env python

# @author: Scott McCool <scott@mccool.com>

import datetime
import requests
import json
import sys
import traceback
import os

try:
    config = json.loads(open('.basis_retriever.cfg', 'r').read())
    BASIS_USERNAME = config['basis']['username']
    BASIS_PASSWORD = config['basis']['password']
    try:
        ACCESS_TOKEN = config['basis']['access_token']
#        print "__debug: Using access token from config (%s)" % (ACCESS_TOKEN)
    except:
        ACCESS_TOKEN = None
    try:
        REFRESH_TOKEN = config['basis']['refresh_token']
    except:
        REFRESH_TOKEN = None
except:
    print "Could not open config file, please create .basis_retriever.cfg"
    print "and include at least the \"basis\" section."
    print "Format (it's json): "
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

# Request everything; get_basis_data() provides the start time and offset
LOGIN_URL = "https://app.mybasis.com/login"
BASE_DATA_URL = """https://app.mybasis.com/api/v1/metricsday/me?
              &heartrate=true&steps=true&calories=true&gsr=true
              &skin_temp=true&air_temp=true&bodystates=true"""
LOGOUT_URL = "https://app.mybasis.com/#logout"
ME_URL = "https://app.mybasis.com/api/v1/user/me.json"
REFRESH_URL = "https://app.mybasis.com/refresh.json"


def basis_login():
    global ACCESS_TOKEN
    global REFRESH_TOKEN
    validLogin = False
    # If we have an access token, see if it's still valid
    if ACCESS_TOKEN != None or REFRESH_TOKEN != None:
        if ACCESS_TOKEN != None:
            r = requests.get(
                url=ME_URL, cookies=dict(access_token=ACCESS_TOKEN))
            if r.status_code == 200:
                validLogin = True
            else:
                print "__Debug:  Got %d from %s, access token %s is probably invalid" % (r.status_code, ME_URL, ACCESS_TOKEN)
                # Do we have a refresh token to try?
        if REFRESH_TOKEN != None and not validLogin:
            print "  __Debug: Trying refresh token"
            r = requests.post(
                url=REFRESH_URL, data={
                    'username': BASIS_USERNAME, 'password': BASIS_PASSWORD,
                    'refresh_token': REFRESH_TOKEN, 'scope': 'login'})
            if r.status_code == 200:
                validLogin = True
                ACCESS_TOKEN = r.cookies['access_token']
                print "  __Debug: Got new access token (%s)" % (ACCESS_TOKEN)
    # We had neither an access nor a refresh token saved, or our attempt at
    # refresh failed.  Just log in.
    if not validLogin:
        print "__Debug: Trying a fresh login"
        r = requests.post(
            url=LOGIN_URL, data={'username': BASIS_USERNAME, 'password': BASIS_PASSWORD})
        if r.status_code == 200:
            validLogin = True
            try:
                REFRESH_TOKEN = r.cookies['refresh_token']
                ACCESS_TOKEN = r.cookies['access_token']
            except:
                print "__Debug:  Confusing, I got a 200 back from the login post but don't seem to have a refresh/access token"
                for c in r.cookies:
                    print "Cookie: %s" % (c)
    # Save access token for future use
    if validLogin:
        global config
        config['basis']['access_token'] = ACCESS_TOKEN
        config['basis']['refresh_token'] = REFRESH_TOKEN
        with open('.basis_retriever.cfg', 'w') as outfile:
            json.dump(config, outfile)


def basis_logout():
    try:
        requests.get(url=LOGOUT_URL, cookies=dict(access_token=ACCESS_TOKEN))
    except:
        print "Exception logging out, you can probably ignore this (used ACCESS_TOKEN=%s)" % (ACCESS_TOKEN)


def get_basis_data(start_date):
    basis_login()
    url = BASE_DATA_URL + "&day=%s" % (start_date)
    r = requests.get(url, cookies=dict(access_token=ACCESS_TOKEN))
    if r.status_code == 200:
        basis_data = json.loads(r.text)
        return basis_data
    else:
        print "__Error from %s (Code: %d) (Response:\n%s\n)" % (url, r.status_code, r.text)


def main():
    d = None
    if len(sys.argv) > 1:
        try:
            d = sys.argv[1]
            datetime.datetime.strptime(d, '%Y-%m-%d')
        except ValueError:
            d = None
    if d == None:
        d = (datetime.date.today() -
             datetime.timedelta(1)).strftime('%Y-%m-%d')
        print "No date passed, using %s" % (d)
    if not os.path.exists('./data/'):
        os.makedirs('data')
    basis_data = get_basis_data(d)
    outfilename = "data/basis-data-%s.json" % (d)
    with open(outfilename, 'w') as outfile:
        json.dump(basis_data, outfile)
    print "Wrote data for %s to %s" % (d, outfilename)
    basis_logout()

if __name__ == "__main__":
    main()
