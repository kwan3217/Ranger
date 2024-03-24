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
  
## Camera Hardware

Rangers 7, 8, and 9 were all completely successful. They were the Ranger Block
III spacecraft (as was Ranger 6), which deleted all science except for the
cameras. These missions carried a fix for the problem which doomed the Ranger 6
camera, and all of them worked. 

All cameras use the same basic design philosophy, and much of the same
hardware design. Each camera has a slow-scan vidicon tube. The camera
is exposed for a short (few millisecond) time, then scanned and transmitted
over a much longer time. The readout and transmission is fully analog --
the readout of each line is used to modulate an FM signal which is then
transmitted back to Earth over the high-gain antenna.

The block III spacecraft carried six cameras
that transmitted back on two channels. Each channel has its own
60W FM transmitter on its own frequency, but both channels
share the high-gain antenna. 

The analog television technology of the 1960s can easily transmit
full-motion (480i30) video. So, why didn't Ranger transmit at
30fps? Any signal using any modulation has a maximum signal rate,
determined largely by the signal-to-noise ratio. Since Ranger
uses a watt-level rather than kilowatt-level transmitter, and
since it is *much* farther away than the range of any normal 
television broadcast, it has a lower signal and therefore lower
signal-to-noise ratio than normal television. The system compensates
by transmitting the signal *much* slower. 

### Channel F
Channel F (for Full scan) carried cameras A and B, which fired alternately on a 2.56s cadence
(each camera therefore was on a 5.12s cadence). Camera A used a 25mm focal length
wide-field lens, and had a field of view of about 22x24deg. Camera B used a 75mm
focal length telephoto lens, and had a field of view of 9x8deg. 

Each camera was scanned with 1150 scan lines. Each camera scanned the full design area (about 11x11mm) of the vidicon tube face
with those 1150 lines. It takes 2.56s to scan and transmit each image, so while one camera is
being scanned and transmitted, the other is being erased and exposed for the next image.

No attempt was made to synchronize the camera cycle with impact, so the impact effectively
was at a uniformly-distributed random time during the last camera cycle. One of the cameras
will have taken an image between 5.12s and 2.56s before impact and completely transmitted it,
while the other will have taken an image between 2.56s and 0.00s and be interrupted by impact
during transmission. Since the vertical speed of impact is about 2km/s, the last complete image
will be taken between 5 and 10km altitude, and the last partial at less than 5km 
altitude.

### Channel P
* Channel P (for Partial scan) carried cameras P1, P2, P3, and P4. These had a narrow field
  of view, but were not designed for higher resolution. Instead, they were designed to fire
  and readout as frequently as possible, so that the last image is as close as possible to the
  surface. The P cameras had the same vidicon tube
  and electronics, but only scanned about 3x3mm of the vidicon tube face. Because of
  this partial scan, the cameras had a narrower field of view even with the same camera
  optics. It's similar to the old "digital zoom" on older digital 
  cameras, that just saved the middle part of the image at the same
  pixel angular resolution but fewer pixels. Cameras P1 and P2 shared the 75mm optics design
  of camera B and therefore had nearly identical angular resolution to B.
  Similarly, P3 and P4 shared the 25mm optics design with camera A, and
  therefore had nearely identical angular resolution.
  Each of these fired in turn on a 0.20s cadence, with an additional 0.04s pause at the end of
  each cycle, so each camera individually was on a 0.84s cadence. Since a camera fires about
  every 0.2s, and the spacecraft has a vertical speed of about 2km/s, we expect the last image taken to be from an altitude of 
  less than 400m, and for the last complete image to be from between 800 and 400m. 
  Cameras P1 and P2 used the same optics as B (75mm lens) and resulted in the narrowest
  fields of view at about 2x2deg, while P3 and P4 used the same optics
  as A and had medium-fields at about 6x6deg. 

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
POD numbers. Each F-channel POD contains a single image. Cameras A and B alternated PODs
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

## Image Orientation

* All A images are oriented such that the original scan lines were
  vertical.
* All B images are oriented such that the original scan lines are
  vertical. The last scan was cut off by impact, and it interrupted
  the *right* edge of the image, indicating that the lines
  were scanned from left to right. A images are probably scanned
  the same, but there is no image interruption to prove it.
* In A TAB 79, there is a lava-filled crater (Guericke F)
  just to the right of reticle point 18, the 
  right-most reticle in the center row. To the
  right of that, there is a large crater (Guericke)
  with two small sharp craters (Guericke D and H) inside it.
  These craters are also visible in B TAB 79,
  much more zoomed in and much closer to
  the center, between reticle points 2 and 3,7. This establishes
  that the axis of camera B is to the right of camera A in the 
  published image series. This in turn
  means that the diagram of camera field overlaps should be
  rotated 90deg counterclockwise to match the published images.
* Comparison with a [modern map of Mare Cognitum](https://asc-planetarynames-data.s3.us-west-2.amazonaws.com/Lunar/lac_76_wac.pdf)
  shows that the published image series has North generally
  towards the top of the images.
* Each of the A and B cameras have a mask on the bottom edge
  of the image. This means that the mask is on the *left* edge
  of the field-of-view diagrams. The masks mask part of each scan line
  to give a black reference. Similarly all P cameras have a simplified
  reticle and mask.
* The top two (wider-field) images in the P TAB 1 include
  Guericke and Guericke F. They also include a noticeable mountain range
  to the left of center. The map shows this as being just north
  of the line between Guericke B and Darney J. B is visible in
  the images but J is not.
* In a P image, P1 is lower left, P2 is lower right, P3 is
  upper left, and P4 is upper right [figure 8 of Ranger VII Photographs of the Moon Part III - P Series](https://www.lpi.usra.edu/resources/ranger/book/3/)

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
