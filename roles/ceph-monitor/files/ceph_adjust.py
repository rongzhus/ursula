#!/usr/bin/python
# coding: utf-8 -*-

# ceph wants pg number be power of 2(good for cursh).
# So if we increase pg number from 1024, the next number will be 2048.
# Increasing so many pg numbers will cause much data rebalancing.
# This script is to increase pg number in small step,
# we run this cript as cron job every 5 minutes.

import subprocess
import pickle
import logging
import json
import os
import time
import re
import glob

LOGFILE = '/var/log/ceph/ceph_adjust.log'

handler = logging.FileHandler(LOGFILE)
FORMAT = "%(asctime)-15s %(levelname)s %(message)s"
handler.setFormatter(logging.Formatter(FORMAT))
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

def run_cmd(command):
    '''
    run the command and return stdout
    exit the script if the rc is not zero
    
    '''
    cmdpipe = subprocess.Popen(command, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    stdout, stderr = cmdpipe.communicate()
    if cmdpipe.returncode != 0:
        logger.error('%(cmd)s: %(err)s' % {'cmd': ' '.join(command),
                                           'err': stderr})
        os._exit(1)
    return stdout

def reweight_by_pg(existing_pools):
    '''
    if any osd node pg_num exceed avg*1.05, then will 
    do pg redistribution
    '''
    #get each pool's pg_num 
    for pool in existing_pools:
        pg = int(run_cmd(['ceph','osd','pool','get',pool,'pg_num']).split(':')[1])
        #if any pg_num is not 2's power, exit
        if(pg&(pg-1) != 0):
            logger.info('The current pg num %d is not 2\' power,pool is %s' % (pg,pool))
            os._exit(1)

    #reweight
    logstr = run_cmd(['ceph','osd','reweight-by-pg','105'])
    str1 = ''
    for i in range(len(logstr.splitlines())):
        str1 += logstr.splitlines()[i] + ' '
    logger.info(str1)        

if __name__ == '__main__':

    existing_pools = run_cmd(['ceph', 'osd', 'pool', 'ls'])
    existing_pools = existing_pools.splitlines()

    reweight_by_pg(existing_pools)
