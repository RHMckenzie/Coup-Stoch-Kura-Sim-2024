#!/bin/bash
tail -n 2 -q `ls ~/jobresults/* | grep -E ".o[0-9]*$"`| head -n 1 
