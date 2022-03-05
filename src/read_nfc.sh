#!/bin/bash

OUTPUT=nfc_fifo
DUMP_FILE=card.mfd

while :
do
    nfc-mfultralight r "$DUMP_FILE"
    if [ $? -eq 0 ]
    then
        content=$(cat "$DUMP_FILE")
        echo "$content" > "$OUTPUT"
    fi
    sleep 0.1
done