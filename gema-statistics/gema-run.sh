#!/bin/bash

OPT=$1
DATAFILE=$2

echo -n `date | awk '{ print $4 }'` >> $DATAFILE
echo -n " " >> $DATAFILE
../gema.sh $OPT Dev Gema-Build