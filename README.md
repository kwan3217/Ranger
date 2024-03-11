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

* Channel F (for Full scan) carried cameras A and B, which fired alternately on a 2.56s cadence
  (each camera therefore was on a 5.12s cadence). Camera A used a 25mm focal length
  wide-field lens, and had a field of view of about 22x24deg. Camera B used a 75mm
  focal length telephoto lens, and had a field of view of 9x8deg. Each camera was scanned with 1150
  scan lines. Each camera scanned the full design area (about 11x11mm) of the vidicon tube face
  with those 1150 lines. 
* Channel P (for Partial scan) carried cameras P1, P2, P3, and P4. Each of these fired in turn on
  a 0.21s cadence, so each camera individually was on a 0.84s cadence. Cameras
  P1 and P2 used the same optics as B (75mm lens) and resulted in the narrowest
  fields of view at about 2x2deg, while P3 and P4 used the same optics
  as A and had medium-fields at about 6x6deg. The P cameras had the same vidicon tube and electronics, but only scanned
  about 3x3mm of the vidicon tube face. Because of this partial scan,
  the cameras had a narrower field of view even with the same camera
  optics. It's similar to the old "digital zoom" on older digital 
  cameras, that just saved the middle part of the image at the same
  pixel angular resolution but fewer pixels. Each of these cameras was scanned with only
  300 scan lines, meaning that P1 had slightly worse resolution than camera B.

The partial scan cameras could be fired much quicker than the full-scan
cameras. The F cameras had a mechanical shutter with a 5ms exposure
time, and the P cameras had a similar shutter but with a 2ms exposure
time (probably due to a narrower slit). The shutter is effectively a
"rolling" shutter, where each point on the focal plane is exposed for
2 or 5 ms, but the entire exposure takes quite a bit longer (looks like
about 80ms, but I still haven't found good documentation).
  
Each camera had a short (5 or 2 ms) exposure time, followed by a much longer
scanning readout time. The last image of each channel is interrupted by impact.
The last image was completely exposed, but the scanning and transmission was
cut off when the spacecraft hit the ground.

Each camera has a [Réseau plate](https://en.wikipedia.org/wiki/R%C3%A9seau_plate)
which is especially important for vidicon cameras. The scan pattern of a vidicon
tube is affected by the very charge image it is scanning, resulting in a
distortion which is dependent on image brightness. The Réseau plate allows the
distortion to be reversed, but leaves permanent fiducial marks in the data. For
Ranger, this isn't that big of a deal since the fiducial marks could in
principle be patched with data from the neighboring images.

Not all images are available on the archive. The original record was kept in
PODs (Primary Original mission Data record). Channels F and P had independent
POD numbers. Each POD contains a single image. Cameras A and B alternated PODs
on channel F, with A being the even numbers and B the odd numbers. There
appear to be 404 channel F PODs on Ranger 7, with the first A image being
POD 8, the last being POD 404, and the first B image being POD 5 with the
last at POD 403. The only loss appears to be the initial cycles, perhaps
images which were transmitted before the camera had fully warmed up. This
gives 199 A images and 200 B images.

All data from a single cycle of cameras P1-P4 are in the same POD, with the 
first set of images all being in POD 17 and the last being POD 979. Published
data goes from every 25th POD near the beginning of the record to every POD
near the end (after 57s to impact). This gives 190 published P PODs. The archive
includes 200 images, but images 191-200 are duplicates of 181-190 respectively
(with a slightly different margin).

In the Ranger 7 photographic parameters table, each published image has one
table of parameters. Each table is identified with a TAB number,
and atlas photo number, and a POD number. For Ranger 7, the TAB
and atlas numbers are the same.

The data archive is in the form of a JPEG image for each A exposure, a separate
image for each B exposure, and a composite image of all 4 P expousres in a
P POD.

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
  * [Ranger VII Photographic Parameters](https://ntrs.nasa.gov/citations/19670002488)
    The bulk of this document is a set of tables, with one entry for each
    photograph.

### Unevaluated
* I have a file marked "Flight Evaluation and Performance Analysis Report for 
  Ranger 7 Mission (45-day report)", signed by J L Shoenhair. This is actually
  a report on the Agena upper stage used to launch the mission. I haven't been
  able to find a reference to it on NTRS

# Getting data
Source code is obviously appropriate to check in. Also, we will be
(but haven't yet) check in tables which have been entered from
the source PDF documents above into spreadsheets.

The PDF files themselves, along with the images from the LPI archive
will not be downloaded. Instead, we provide a bash script which downloads
the images, as well as URLs in this file for the PDF documents.

## get_lpi.sh
Script to get Ranger images from the Lunar and Planetary Institute (LPI), 
University of Arizona. 

# Rectification
The images are of an unknown provenance, and almost certainly scanned
out of a printed atlas. Because of this, and also due to the nature
of vidicon tubes,
