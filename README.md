Basis data liberator & Fitbit hack
==

Credit
==
Inspired by https://github.com/btroia/basis-data-export
Basically, I already had a fitbit-poster and didn’t feel like changing PHP code

Overview
==
This is a set of scripts for working with data from the Basis smartwatch (http://www.mybasis.com/).  The core script is basis_retriever.py, which retrieves minute-by-minute data from the Basis website after you have synced your device.  It does not read from the watch directly.

In addition, helper scripts are provided to display your raw step count, to graph your heart rate over time, and to write step data to Fitbit since they integrate well with other services (the impetus for this was my desire to post walking data to MyFitnessPal, who don’t seem to issue new API keys)

Details
==
Basis doesn’t provide an API, but quantified bob was kind enough to reverse engineer their javascript.  This script “scrapes” the data by logging into the website and retrieving it in .json format.  It exports that data to a single file per day containing all of the metrics available from the basis.

In addition, the companion basis_steps_to_fitbit.py parses a days data, looks for “walk events” (minutes where you took more then X steps for more then Y consecutive minutes) and posts that to fitbit as an activity.  This is solely because MyFitnessPal won’t issue API keys from what I can see, and I wanted to get calorie burned data into MFP.  You can connect your Fitbit and MFP accounts and using this rube-goldberg-esque contraption get data from your basis into fitbit.
i
scatterplot_hr_metrics.py Will generate a graph from each of your days data showing your heartrate throughout the day.  This could be extneded for any metric.

If anyone has a contact at MFP, please let me know and I’ll post directly there.

Configuration
==
  * Install the “Requests” module (pip install requests)
  * See .basis_retriever.cfg.example; the “basis” section is required for basis_retriever.py
  * Create a “data” directory (I recommend symlinking to dropbox)
  * <for fitbit integration>
    ** Install the “fitbit” module (pip install fitbit)
    ** Configure fitbit API keys according to their docs, add to fitbit section of config

Usage
==
python basis_retriever.py [YYYY-MM-DD]
python basis_steps_to_fitbit.py [YYYY-MM-DD]

Caveats
==
basis_retriever:  This is not an official API; Basis may change it at any time.
basis_steps_to_fitbit: Hard coded to “walking” activity, it does not post total calories burned or all walks.  I’m only interested in transferring my walking commute automatically; I enter other exercise into MFP directly.
