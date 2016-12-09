# ** testcontroller.py **
# maintainer: Leif Taylor
# Purpose: This program will execute a series of robot tests, move the logs into a folder structure, and
# route console input into an output file.
#
# +--------------------------+
# | How to use this program: |
# +--------------------------+
# 1) You must already have your own folder, with inventory files, on a robot controller vm
# 2) Required files: 'rbc', 'aliases', 'testcontroller.py (this file)'
# 3) Edit your 'aliases' file (must be called aliases) like this:
#   [<alias name>]
#   <some command>
#   [<another alias>]
#   <another command>
#   [<another alias>]
#   [another command]
#
# Here is an example aliases file (comments are okay on the tag line, not the invdrobot command line:
#   [aix] # this will run the database test on my aix inventory file
#   invdrobot -V inv/host/oraclehost.py:host -V inv/appliance/mycds.py suites/orarac1+2/databasetest.robot
#   [linux] # this will run the database test on my linux inventory file and a sky
#   invdrobot -V inv/host/linuxoracle.py:host -V inv/appliance/mysky.py suites/orarac1+2/databasetest.robot
#
# 4) To execute all of the tests in the 'aliases' file, simply run: './rbc' (or 'python testcontroller.py')
# 5) To execute a single test from the 'aliases' file, simply run: './rbc <aliasname>' (e.g. ./rbc aix)
# 6) If you want to execute some but not all, simply list the ones you want: './rbc alias1 alias3 alias5
# 7) For additional help and examples, use ./rbc -h
#
# Happy Testing!
