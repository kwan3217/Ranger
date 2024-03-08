# Ranger
Programs and data to plot the impact of Ranger on the Moon. I am focusing on
Ranger 7, the first fully-successful mission.

## Mission
Ranger was a series of impactor spacecraft. The first six missions did not
result in successful imagery:

* Rangers 1 and 2 were tests of the spacecraft and launch vehicle. Neither one
  was aimed at the moon, but instead aimed at a point in space at lunar distance
  referred to as a "paper moon". Neither mission left Earth parking orbit due
  to failures in the upper stage.
* Rangers 3, 4, and 5 carried cameras and a rough-landing seismometer package
  with its own solid-fuel braking rocket. Ranger 3 missed the moon due to launch
  vehicle and ground systems failures, but did reach lunar distance. Ranger 4
  had a near-flawless launch and injection onto a translunar trajectory, but
  the spacecraft failed. Its translunar trajectory resulted in a lunar impact
  over the limb on the far side, and due to the failure, the midcourse maneuver
  was not executed. Ranger 5 also had a successful launch and injection, with
  a translunar trajectory that passed only a few hundred kilometers over the
  lunar surface, but the spacecraft failed and again no midcourse maneuver
  could be executed.
* Ranger 6 might have been the most painful of all. The spacecraft was pared
  down and totally focused on one science instrument, the camera suite. The 
  mission worked perfectly with one glaring exception -- during launch, the 
  staging event increased the local atmosphere around the launch vehicle and
  spacecraft, causing a transient in the camera power supply which burned it
  out. The spacecraft successfully executed its midcourse maneuver, and was
  perfectly targeted towards a lunar impact. However, when the camera was
  commanded to activate 15 minutes before impact, it never activated and
  transmitted no pictures. Since this was the sole science instrument, the
  whole mission was a failure.
  
Rangers 7, 8, and 9 were all completely successful. They were the Ranger Block
III spacecraft (as was Ranger 6), which deleted all science except for the
cameras. These missions carried a fix for the problem which doomed the Ranger 6
camera, and all of them worked. The block III spacecraft carried six cameras
that transmitted back on two channels:

* Channel F carried cameras A and B, which fired alternately on a 2.56s cadence
  (each camera therefore was on a 5.12s cadence). Camera A was the widest field,
  22x24deg. Camera B was medium-field, 9x8deg. Each camera was scanned with 1150
  scan lines.
* Channel P carried cameras P1, P2, P3, and P4. Each of these fired in turn on
  a 0.84s cadence, so each camera individually was on a 3.36s cadence. Cameras
  P1 and P2 were the narrowest fields of view at about 2x2deg, while P3 and P4
  had medium-fields at about 6x6deg. Each of these cameras was scanned with only
  300 scan lines, meaning that P1 had slightly worse resolution than camera B.
  
Each camera had a short (5 or 2 ms) exposure time, followed by a much longer
scanning readout time. The last image of each channel is interrupted by impact.
The last image was completely exposed, but the scanning and transmission was
cut off when the spacecraft hit the ground.

The data archive is in the form of a JPEG image for each A exposure, a separate
image for each B exposure, and a composite image of all 4 P expousres in a
cycle.

* Ranger 7 took 199 A images, 200 B images, and 200 images with each P camera.

## Sources
* The Lunar and Planetary Institute (LPI) is the official NASA archive for
  Ranger data. Their web site is at https://www.lpi.usra.edu/resources/ranger/
  * [Ranger VII Photographs of the Moon Part I: Camera "A" Series](https://www.lpi.usra.edu/resources/ranger/book/1/)
    This report includes fields of view of the cameras, orientation relative
    to the spacecraft axes, and a table of exposure times for camera A.
  * [Ranger VII Photographs of the Moon Part II: Camera "B" Series](https://www.lpi.usra.edu/resources/ranger/book/2/)
    Same thing for camera B
  * [Ranger VII Photographs of the Moon Part II: Camera "P" Series](https://www.lpi.usra.edu/resources/ranger/book/3/)
    Same thing for cameras on the P channel.

### Unevaluated
* I have a file marked "Flight Evaluation and Performance Analysis Report for 
  Ranger 7 Mission (45-day report)", signed by J L Shoenhair. This is actually
  a report on the Agena upper stage used to launch the mission. I haven't been
  able to find a reference to it on NTRS

## get_lpi.sh
Script to get Ranger images from the Lunar and Planetary Institute (LPI), 
University of Arizona. 


