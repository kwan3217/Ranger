#!/bin/bash -x
#Script to get, resize, and convert all Ranger 7 camera images from the Lunar and Planetary Institute

# Local folder to store data
LOCAL_ROOT=./

#Ranger 7
MISSION=7
# Camera A
CAMERA=A
IMAGES=199
rm -rfv $LOCAL_ROOT/$MISSION$CAMERA
mkdir -pv $LOCAL_ROOT/$MISSION$CAMERA
for i in `seq -w 1 $IMAGES`
do
    wget -v https://www.lpi.usra.edu/resources/ranger/images/print/$MISSION/$CAMERA/$i.jpg -O $LOCAL_ROOT/$MISSION$CAMERA/Ranger$MISSION$CAMERA$i.jpg
done

# Camera B
CAMERA=B
IMAGES=200
rm -rfv $LOCAL_ROOT/$MISSION$CAMERA
mkdir -pv $LOCAL_ROOT/$MISSION$CAMERA
for i in `seq -w 1 $IMAGES`
do
    wget -v https://www.lpi.usra.edu/resources/ranger/images/print/$MISSION/$CAMERA/$i.jpg -O $LOCAL_ROOT/$MISSION$CAMERA/Ranger$MISSION$CAMERA$i.jpg
done

# Camera P. There are 200 file, but only 190 are unique.
# TABs 191-200 duplicate 181-190, with a different margin.
CAMERA=P
IMAGES=190
rm -rfv $LOCAL_ROOT/$MISSION$CAMERA
mkdir -pv $LOCAL_ROOT/$MISSION$CAMERA
for i in `seq -w 1 $IMAGES`
do
    wget -v https://www.lpi.usra.edu/resources/ranger/images/print/$MISSION/$CAMERA/$i.jpg -O $LOCAL_ROOT/$MISSION$CAMERA/Ranger$MISSION$CAMERA$i.jpg
done


#Ranger 8
MISSION=8
# Camera A
CAMERA=A
IMAGES=60
rm -rfv $LOCAL_ROOT/$MISSION$CAMERA
mkdir -pv $LOCAL_ROOT/$MISSION$CAMERA
for i in `seq -f "%03.0f" $IMAGES`
do
    wget -v https://www.lpi.usra.edu/resources/ranger/images/print/$MISSION/$CAMERA/$i.jpg -O $LOCAL_ROOT/$MISSION$CAMERA/Ranger$MISSION$CAMERA$i.jpg
done

# Camera B
CAMERA=B
IMAGES=90
rm -rfv $LOCAL_ROOT/$MISSION$CAMERA
mkdir -pv $LOCAL_ROOT/$MISSION$CAMERA
for i in `seq -f "%03.0f" $IMAGES`
do
    wget -v https://www.lpi.usra.edu/resources/ranger/images/print/$MISSION/$CAMERA/$i.jpg -O $LOCAL_ROOT/$MISSION$CAMERA/Ranger$MISSION$CAMERA$i.jpg
done

# Camera P
CAMERA=P
IMAGES=20
rm -rfv $LOCAL_ROOT/$MISSION$CAMERA
mkdir -pv $LOCAL_ROOT/$MISSION$CAMERA
for i in `seq -f "%03.0f" $IMAGES`
do
    wget -v https://www.lpi.usra.edu/resources/ranger/images/print/$MISSION/$CAMERA/$i.jpg -O $LOCAL_ROOT/$MISSION$CAMERA/Ranger$MISSION$CAMERA$i.jpg
done


#Ranger 9
MISSION=9
# Camera A
CAMERA=A
IMAGES=70
rm -rfv $LOCAL_ROOT/$MISSION$CAMERA
mkdir -pv $LOCAL_ROOT/$MISSION$CAMERA
for i in `seq -f "%03.0f" $IMAGES`
do
    wget -v https://www.lpi.usra.edu/resources/ranger/images/print/$MISSION/$CAMERA/$i.jpg -O $LOCAL_ROOT/$MISSION$CAMERA/Ranger$MISSION$CAMERA$i.jpg
done

# Camera B
CAMERA=B
IMAGES=88
rm -rfv $LOCAL_ROOT/$MISSION$CAMERA
mkdir -pv $LOCAL_ROOT/$MISSION$CAMERA
for i in `seq -f "%03.0f" $IMAGES`
do
    wget -v https://www.lpi.usra.edu/resources/ranger/images/print/$MISSION/$CAMERA/$i.jpg -O $LOCAL_ROOT/$MISSION$CAMERA/Ranger$MISSION$CAMERA$i.jpg
done

# Camera P
CAMERA=P
IMAGES=12
rm -rfv $LOCAL_ROOT/$MISSION$CAMERA
mkdir -pv $LOCAL_ROOT/$MISSION$CAMERA
for i in `seq -f "%03.0f" $IMAGES`
do
    wget -v https://www.lpi.usra.edu/resources/ranger/images/print/$MISSION/$CAMERA/$i.jpg -O $LOCAL_ROOT/$MISSION$CAMERA/Ranger$MISSION$CAMERA$i.jpg
done


