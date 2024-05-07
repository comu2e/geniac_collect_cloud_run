#!/bin/bash

BATCH=20
sh launch.sh $((BATCH + 1)) "us-east1" "crawler2"
sh launch.sh $((BATCH + 2)) "us-central1" "crawler-uscentral"
sh launch.sh $((BATCH + 3)) "us-west1" "crawler-uswest"
sh launch.sh $((BATCH +4)) "us-east4" "crawler-useast4"