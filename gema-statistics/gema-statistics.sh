#!/bin/bash

OPT="add"
DATAFILE="~/datafile"
NUM=500
WAIT=0

for i in `seq 1 $NUM`; do

    echo "Sending $OPT command to GEMA..."
    /usr/bin/time --quiet -o /tmp/datafile.tmp ./gema-run.sh $OPT ~/datafile
    cat /tmp/datafile.tmp | grep "elapsed" | awk '{ print $3 }' | sed 's/elapsed//g' >> ~/datafile

    echo "Waiting $WAIT seconds..."
    sleep $WAIT

    if [ "$OPT" == "add" ]; then
        OPT="remove"
    else
        OPT="add"
    fi

done

echo "Finished $NUM iteractions."