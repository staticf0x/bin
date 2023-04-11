#!/bin/bash

# Add -s us for measuring in us instead of ms

TIMESTAMP=$(date +"%s")
python3 -m cProfile -s time -o profile_$TIMESTAMP.prof "$@"

if [ -e profile_$TIMESTAMP.prof ]
then
    pyprof2calltree -i profile_$TIMESTAMP.prof -o cachegrind.out.$TIMESTAMP -s us
    echo "Output written to: cachegrind.out.$TIMESTAMP"
    echo "Run kcachegrind cachegrind.out.$TIMESTAMP to open"
fi
