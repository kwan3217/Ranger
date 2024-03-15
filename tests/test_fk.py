import numpy as np
import pytest
from matplotlib import pyplot as plt

from spiceypy import furnsh, pxform

from kwanmath.vector import vcomp



def test_fk():
    """
    Test that the FK kernels produce vectors in the expected direction
    :return:
    """
    furnsh("kernels/Ranger7.tf")
    z_ref=vcomp((0.0,0.0,1.0))
    M_sc_ref=pxform("RANGER7_CAMREF","RANGER7_SPACECRAFT",0)
    z_sc=M_sc_ref @ z_ref
    # The expected camera reference axis has:
    #  * 0 on x axis, since camera is exactly on yz plane
    #  * Positive (= cos(-38deg)) z axis, since camera reference axis is close to spacecraft z axis
    #  * Positive (=-sin(-38deg)) y axis, since reference axis is on the +y side of the vehicle
    print(M_sc_ref,z_sc)
    plt.axis('equal')
    cam_size={
            # left  right up    down
        "A" :(12.78,10.75,12.18,12.48),
        "B" :( 4.31, 3.34, 4.40, 4.30),
        "P1":( 1.14, 0.64, 1.10, 1.30),
        "P2":( 1.14, 0.70, 1.07, 1.07),
        "P3":( 2.91, 2.42, 2.93, 2.83),
        "P4":( 2.88, 2.60, 2.86, 2.76),

    }
    for cam,(l,r,u,d) in cam_size.items():
        z_cam=vcomp((0.0,0.0,1.0))
        u_cam=vcomp((0.0, np.sin(np.radians( u)),np.cos(np.radians( u))))
        d_cam=vcomp((0.0, np.sin(np.radians(-d)),np.cos(np.radians( d))))
        l_cam=vcomp((np.sin(np.radians(-l)),0.0,np.cos(np.radians(-l))))
        r_cam=vcomp((np.sin(np.radians( r)),0.0,np.cos(np.radians( r))))
        M_ref_cam=pxform(f"RANGER7_{cam}","RANGER7_CAMREF",0)
        for vec_cam,color in zip((z_cam,u_cam,d_cam,l_cam,r_cam),("k+","g+","m+","c+","r+")):
            vec_ref=M_ref_cam @ vec_cam
            xplt=np.degrees(np.arcsin(vec_ref[0,0]))
            yplt=np.degrees(np.arcsin(vec_ref[1,0]))
            plt.plot(xplt,yplt,color)
            plt.text(xplt,yplt,cam)
            print(M_ref_cam)
            print(vec_ref)
    plt.show()