#!/bin/bash

BATCH=11
sh launch2.sh $((BATCH + 1))
sh launch_central.sh $((BATCH + 2))
sh launch_us_central.sh $((BATCH + 3))
sh launch_useast4.sh $((BATCH + 4))