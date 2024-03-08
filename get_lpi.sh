#!/bin/bash -x
#Script to get, resize, and convert all Ranger 7 camera images from the Lunar and Planetary Institute

# Local folder to store data
LOCAL_ROOT=/mnt/big/workspace/Data/Ranger

# Camera A
rm -rfv $LOCAL_ROOT/7A
mkdir -pv $LOCAL_ROOT/7A
for i in `seq -w 1 199`
do
    wget -v https://www.lpi.usra.edu/resources/ranger/images/print/7/A/$i.jpg -O $LOCAL_ROOT/7A/Ranger7A$i.jpg
done

# Camera B
rm -rfv $LOCAL_ROOT/7B
mkdir -pv $LOCAL_ROOT/7B
for i in `seq -w 1 200`
do
    wget -v https://www.lpi.usra.edu/resources/ranger/images/print/7/B/$i.jpg -O $LOCAL_ROOT/7B/Ranger7B$i.jpg
done

# Camera P. There are 200 file, but only 190 are unique.
# TABs 191-200 duplicate 181-190, with a different margin.
rm -rfv $LOCAL_ROOT/7P
mkdir -pv $LOCAL_ROOT/7P
for i in `seq -w 1 190`
do
    wget -v https://www.lpi.usra.edu/resources/ranger/images/print/7/P/$i.jpg -O $LOCAL_ROOT/7P/Ranger7P$i.jpg
done


