KPL/FK


Ranger 7 Frames Kernel
===============================================================================

   This frame kernel contains complete set of frame definitions for the
   Ranger 7 spacecraft, its structures and science instruments. This frame
   kernel also contains name - to - NAIF ID mappings for Ranger 7 science
   instruments and s/c structures (see the last section of the file.)


Version and Date
-------------------------------------------------------------------------------

   Version 0.0 -- May 22, 2009 -- Chris Jeppesen

      Initial Release with spacecraft ID -1007.


   Version 0.1 -- 2024-03-08 -- Chris Jeppesen

      Improved comments (removed more of the MAVEN boilerplate)


References
-------------------------------------------------------------------------------

   1. ``Frames Required Reading''

   2. ``Kernel Pool Required Reading''

   3. ``C-Kernel Required Reading''

   4. Ranger 7 - Part 1. Mission Description and Performance
       https://ntrs.nasa.gov/citations/19650003679

   5. Ranger 7 Photographs of the Moon Part I: Camera A series
       https://www.lpi.usra.edu/resources/ranger/book/1/


Implementation Notes
-------------------------------------------------------------------------------

   This file is used by the SPICE system as follows: programs that make
   use of this frame kernel must ``load'' the kernel, normally during
   program initialization using the SPICELIB routine FURNSH. This file
   was created and may be updated with a text editor or word processor.


Ranger 7 Frames
-------------------------------------------------------------------------------

   The following Ranger 7 frames are defined in this kernel file:

           Name                  Relative to           Type       NAIF ID
      ======================  ===================  ============   =======

   Spacecraft frame:
   -----------------
      RANGER7_SPACECRAFT        rel.to ECI_TOD      CK             -1007000

   Camera frames:
   -----------------
      RANGER7_CAMREF            RANGER7_SPACECRAFT  FIXED          -1007100
      RANGER7_A                 RANGER7_CAMREF      FIXED          -1007101
      RANGER7_B                 RANGER7_CAMREF      FIXED          -1007102
      RANGER7_P1                RANGER7_CAMREF      FIXED          -1007201
      RANGER7_P2                RANGER7_CAMREF      FIXED          -1007202
      RANGER7_P3                RANGER7_CAMREF      FIXED          -1007203
      RANGER7_P4                RANGER7_CAMREF      FIXED          -1007204

   Articulated devices:
   ------------------
      RANGER7_HGA               RANGER7_SPACECRAFT  CK             -1007301
      RANGER7_SOLAR_PX          RANGER7_SPACECRAFT  CK             -1007401
      RANGER7_SOLAR_PY          RANGER7_SPACECRAFT  CK             -1007402




Spacecraft Bus Frame
-------------------------------------------------------------------------------
 
   The spacecraft frame is a right-handed system defined by the s/c design and
   matches [1, p79].

      - origin is the intersection of the roll axis and the separation plane

      -  Z axis is parallel to the roll axis, with +Z towards the separation plane
         and -Z towards the television system. Positive roll is a right-handed rotation
         around the Z axis.
 
      -  X axis is parallel to the pitch axis, and runs along the solar panels (when they
         are deployed). Positive pitch is a right-handed rotation around the X axis.

      -  Y axis completes the right hand frame. The high-gain antenna is on the -Y side
         of the spacecraft. Positive yaw is a right-handed rotation around the Y axis.


   Since the S/C bus attitude is provided by a C kernel (see [3] for
   more information), this frame is defined as a CK-based frame.


   \begindata

      FRAME_RANGER7_SPACECRAFT       = -1007000
      FRAME_-1007000_NAME            = 'RANGER7_SPACECRAFT'
      FRAME_-1007000_CLASS           = 3
      FRAME_-1007000_CLASS_ID        = -1007000
      FRAME_-1007000_CENTER          = -1007
      CK_-1007000_SCLK               = -1007
      CK_-1007000_SPK                = -1007

   \begintext

   The spacecraft camera reference axis is rotated
   38deg away from the +Z axis towards the +y axis.
   This is a right-handed rotation of -38deg about
   the x axis. The camera reference +Z is along
   the general direction of the camera fields of view,
   while its +x matches the spacecraft +x and the +y
   completes a right-handed system and is therefore
   38deg away from the spacecraft +y.

   The TK below is what is necessary to rotate *from* the
   camera reference frame *to* the spacecraft frame, so
   it's a *positive* 38deg rotation around the
   *camera reference* +x axis.

   All camera axes are specified relative to this axis.

   \begindata

      FRAME_RANGER7_CAMREF           = -1007100
      FRAME_-1007100_NAME            = 'RANGER7_CAMREF'
      FRAME_-1007100_CLASS           = 4
      FRAME_-1007100_CLASS_ID        = -1007100
      FRAME_-1007100_CENTER          = -1007
      TKFRAME_-1007100_RELATIVE      = 'RANGER7_SPACECRAFT'
      TKFRAME_-1007100_SPEC          = 'ANGLES'
      TKFRAME_-1007100_UNITS         = 'DEGREES'
      TKFRAME_-1007100_ANGLES        = (0.00, 0.00,+38.0)
      TKFRAME_-1007100_AXES          = ( 3  ,  2  ,   1 )

   \begintext

   Ranger 7 Camera A. All cameras have their axes defined
   relative to the "camera reference axis" above. See [5, pp5-6]
   In that diagram, "up" is farther away from the spacecraft
   +z axis, so negative rotation around the x axis. "Right"
   is a rotation around the y axis towards the -x axis,
   which turns out to be a positive rotation. From the
   reference:

   Camera         left(-)/right(+)    up(-)/down(+)
      A           +0.05               -8.75
      B           +0.07               +4.65
     P1           -0.44               -0.76
     P2           +0.60               -0.43
     P3           -0.28               +0.25
     P4           +0.78               +0.54

     Since all left/right angles are small, rotate around
     that axis *first*, then the other axis. None of the
     cameras have any clock/barrel-twist recorded. If they
     did, it would be a rotation around the camera reference
     Z axis first. We reverse all the signs since we are
     transforming *from* the camera *to* the reference axis

   \begindata

      FRAME_RANGER7_A                = -1007101
      FRAME_-1007101_NAME            = 'RANGER7_A'
      FRAME_-1007101_CLASS           = 4
      FRAME_-1007101_CLASS_ID        = -1007101
      FRAME_-1007101_CENTER          = -1007
      TKFRAME_-1007101_RELATIVE      = 'RANGER7_CAMREF'
      TKFRAME_-1007101_SPEC          = 'ANGLES'
      TKFRAME_-1007101_UNITS         = 'DEGREES'
      TKFRAME_-1007101_ANGLES        = (0.00,-0.05,+8.75)
      TKFRAME_-1007101_AXES          = ( 3  ,  2  ,  1  )

      FRAME_RANGER7_B                = -1007102
      FRAME_-1007102_NAME            = 'RANGER7_B'
      FRAME_-1007102_CLASS           = 4
      FRAME_-1007102_CLASS_ID        = -1007102
      FRAME_-1007102_CENTER          = -1007
      TKFRAME_-1007102_RELATIVE      = 'RANGER7_CAMREF'
      TKFRAME_-1007102_SPEC          = 'ANGLES'
      TKFRAME_-1007102_UNITS         = 'DEGREES'
      TKFRAME_-1007102_ANGLES        = (0.00,-0.07,-4.65)
      TKFRAME_-1007102_AXES          = ( 3  ,  2  ,  1  )

      FRAME_RANGER7_P1                = -1007201
      FRAME_-1007201_NAME            = 'RANGER7_P1'
      FRAME_-1007201_CLASS           = 4
      FRAME_-1007201_CLASS_ID        = -1007201
      FRAME_-1007201_CENTER          = -1007
      TKFRAME_-1007201_RELATIVE      = 'RANGER7_CAMREF'
      TKFRAME_-1007201_SPEC          = 'ANGLES'
      TKFRAME_-1007201_UNITS         = 'DEGREES'
      TKFRAME_-1007201_ANGLES        = (0.00,+0.44,+0.76)
      TKFRAME_-1007201_AXES          = ( 3  ,  2  ,  1  )

      FRAME_RANGER7_P2                = -1007202
      FRAME_-1007202_NAME            = 'RANGER7_P2'
      FRAME_-1007202_CLASS           = 4
      FRAME_-1007202_CLASS_ID        = -1007202
      FRAME_-1007202_CENTER          = -1007
      TKFRAME_-1007202_RELATIVE      = 'RANGER7_CAMREF'
      TKFRAME_-1007202_SPEC          = 'ANGLES'
      TKFRAME_-1007202_UNITS         = 'DEGREES'
      TKFRAME_-1007202_ANGLES        = (0.00,-0.60,+0.43)
      TKFRAME_-1007202_AXES          = ( 3  ,  2  ,  1  )

      FRAME_RANGER7_P3                = -1007203
      FRAME_-1007203_NAME            = 'RANGER7_P3'
      FRAME_-1007203_CLASS           = 4
      FRAME_-1007203_CLASS_ID        = -1007203
      FRAME_-1007203_CENTER          = -1007
      TKFRAME_-1007203_RELATIVE      = 'RANGER7_CAMREF'
      TKFRAME_-1007203_SPEC          = 'ANGLES'
      TKFRAME_-1007203_UNITS         = 'DEGREES'
      TKFRAME_-1007203_ANGLES        = (0.00,+0.28,-0.25)
      TKFRAME_-1007203_AXES          = ( 3  ,  2  ,  1  )

      FRAME_RANGER7_P4                = -1007204
      FRAME_-1007204_NAME            = 'RANGER7_P4'
      FRAME_-1007204_CLASS           = 4
      FRAME_-1007204_CLASS_ID        = -1007204
      FRAME_-1007204_CENTER          = -1007
      TKFRAME_-1007204_RELATIVE      = 'RANGER7_CAMREF'
      TKFRAME_-1007204_SPEC          = 'ANGLES'
      TKFRAME_-1007204_UNITS         = 'DEGREES'
      TKFRAME_-1007204_ANGLES        = (0.00,-0.78,-0.54)
      TKFRAME_-1007204_AXES          = ( 3  ,  2  ,  1  )

