"""
Use what we have learned from image correlation to try to automatically find
all of the reticle markings in a Ranger image.
"""
import re
from collections.abc import Iterable
from glob import glob
from os import mkdir, unlink, remove

import numpy as np
from PIL import Image
from matplotlib import image as mpimg, pyplot as plt
from matplotlib.backend_bases import MouseButton
from scipy.interpolate import RegularGridInterpolator
from scipy.optimize import minimize
# Give this function a weird alias so that we aren't tempted to use it.
# Use transform_image() below instead, and only use affine_pull_transform()
# inside transform_image().
from scipy.ndimage import affine_transform as affine_pull_transform

from kwanmath.vector import vdot, vcomp, vdecomp
from correlate import img_offset, cross_image

# Series 7A has the "top" row of reticle marks chopped off by the top of the frame. We will rectify using
# the rest of the marks, numbering them from left to right along the top row full row starting at 0, then
# the next row starting at 5, etc. Since there are 4 complete rows, this will give us 20 marks, numbered
# 0 to 19. Note that these are *NOT* the same numbering as in the photo parameter reports, but are 1-to-1
# convertible to that numbering.


def transform_image(img:np.ndarray,M_to_from:np.ndarray,*,output_shape:tuple[int,int]=None)->np.ndarray:
    """
    Perform an affine transform on an image. Original image is in the *from* frame,
    and the new coordinate for each pixel is found by multiplying the from coordinate
    by the given vector.

    :param img: Image to transform
    :param M_to_from: Matrix which transforms a coordinate in the *from* frame to the
                      corresponding image in the *to* frame. For each coordinate x_from,
                      the pixel in the new image at x_to=M_to_from@x_from will be the
                      same color as the pixel in the old image at x_from.
    :param args:      Extra un-named arguments passed along to scipy.ndimage.affine_transform()
    :param kwargs:    Extra named arguments passed along to scipy.ndimage.affine_transform()
    :return: Transformed image

    The *sole* reason we are doing this is that scipy.ndimage.affine_transform() uses the matrix
    backwards. From it's point of view, it takes each coordinate in the *to* image, calculates
    what the matching point is in the *from* image, and samples the *from* image there. It makes
    sense to calculate things this way, but it is inconvenient to use. Quoting the
    [documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.affine_transform.html):

    > This does ‘pull’ (or ‘backward’) resampling, transforming the output space to the input to locate data.
    > Affine transformations are often described in the ‘push’ (or ‘forward’) direction, transforming input
    > to output. If you have a matrix for the ‘push’ transformation, use its inverse (numpy.linalg.inv) in
    > this function.
    """
    #naming convention: in* is a point originally in input space.
    #                   out* is a point originally in output space
    #                   - No matter how you transform it, it remains an in* or out* quantity.
    #                   *from is a point now in input (from) space
    #                   *to is a point now in output (to) space
    #                   - Must follow the frame of the space that the quantity currently is in.
    #                   *x* is a 1D array of x (horizontal, IE column) coordinates
    #                   *y* is a 1D array of y (vertical, IE row) coordinates
    # so, in or out won't change during a transformation, but from or to must.
    iny1dfrom=np.arange(img.shape[0])
    inx1dfrom=np.arange(img.shape[1])
    rgi=RegularGridInterpolator((iny1dfrom,inx1dfrom),img,bounds_error=False,fill_value=0)
    inxfrom=np.broadcast_to(inx1dfrom,img.shape)
    inyfrom=np.broadcast_to(iny1dfrom.reshape(-1,1),img.shape)
    if output_shape is None:
        output_shape=img.shape
    outy1dto=np.arange(output_shape[0])
    outx1dto=np.arange(output_shape[1])
    outxto=np.broadcast_to(outx1dto,output_shape)
    outyto=np.broadcast_to(outy1dto.reshape(-1,1),output_shape)

    # Will be a 2D stack of column vectors, so [inrows,3,incols]
    invfrom=vcomp((inxfrom,inyfrom,np.broadcast_to(1,img.shape)))
    # Will be a 2D stack of column vectors, so [outrows,3,outcols]
    outvto=vcomp((outxto,outyto,np.broadcast_to(1,output_shape)))
    invto=M_to_from @ invfrom
    # Coordinates of each output pixel in input space. We will sample the input image at each point.
    M_from_to=np.linalg.inv(M_to_from)
    outvfrom=M_from_to @ outvto
    outxfrom,outyfrom,_=vdecomp(outvfrom)
    outimg=rgi((outyfrom,outxfrom))
    return outimg


def calc_M_img_big(shape:np.ndarray,n_scanlines:int)->np.ndarray:
    # Return a matrix that scales coordinates in the full-resolution image down
    # to the corresponding coordinate in the 1150-sample image.
    M = np.array([[n_scanlines/shape[1], 0,0],
                  [0, n_scanlines/shape[1] ,0],
                  [0,0,1]])
    return M


def scaledown(img:np.ndarray,n_scanlines:int)->np.ndarray:
    """
    # Scale image to 1150 pixels wide (to roughly match scan resolution)

    :param img:
    :param n_scanlines:
    :return:
    """
    M_img_big=calc_M_img_big(img.shape,n_scanlines)
    outshape=(int(n_scanlines / img.shape[1] * img.shape[0]), n_scanlines)
    outimg = transform_image(img, M_img_big, output_shape=outshape).astype(np.uint8)
    return outimg


def get_synthetic_masks(mission:int,channel:str)->list[np.ndarray]:
    def synthetic_mark(*,
                       r: int = 50, l: int = 30, w2: int = 2,
                       n: bool, s: bool, e: bool, w: bool,
                       bg: int = 0, fg: int = 255) -> np.ndarray:
        result = np.zeros((r * 2, r * 2), dtype=np.uint8) + bg
        if n:
            result[r - l:r + w2, r - w2:r + w2] = fg
        if s:
            result[r - w2:r + l, r - w2:r + w2] = fg
        if e:
            result[r - w2:r + w2, r - w2:r + l] = fg
        if w:
            result[r - w2:r + w2, r - l:r + w2] = fg
        return result

    synthetic_masks=[
        synthetic_mark(n=True , s=True , e=True , w=False),
        synthetic_mark(n=False, s=True , e=True , w=False),
        synthetic_mark(n=False, s=True , e=True , w=True ),
        synthetic_mark(n=False, s=True , e=False, w=True ),
        synthetic_mark(n=True , s=True , e=False, w=True ),

        synthetic_mark(n=True , s=True , e=True , w=False),
        synthetic_mark(n=True , s=True , e=True , w=False),
        synthetic_mark(n=True , s=True , e=True , w=True ),
        synthetic_mark(n=True , s=True , e=False, w=True ),
        synthetic_mark(n=True , s=True , e=False, w=True ),

        synthetic_mark(n=True , s=True , e=True , w=False),
        synthetic_mark(n=True , s=False, e=True , w=False),
        synthetic_mark(n=True , s=False, e=True , w=True ),
        synthetic_mark(n=True , s=False, e=False, w=True ),
        synthetic_mark(n=True , s=True , e=False, w=True ),

        synthetic_mark(n=True , s=False, e=True , w=False, l=50),
        synthetic_mark(n=True , s=False, e=True , w=True ),
        synthetic_mark(n=True , s=False, e=True , w=True ),
        synthetic_mark(n=True , s=False, e=True , w=True ),
        synthetic_mark(n=True , s=False, e=False, w=True , l=50),
    ]
    return synthetic_masks

lattice_config={7:{"A":((-2,-1,0,1,2),(-1,0,1,2)),
                   "B":((-2,-1,0,1,2),(-1,0,1,2))},
                8:{"A":((-2,-1,0,1,2),(-1,0,1,2)),
                   "B":((-2,-1,0,1,2),(-1,0,1,2))}}


def get_lattice(mission:int,channel:str)->list[tuple[int,int]]:
    """

    :param mission:
    :param channel:
    :return:
    """
    xlattice,ylattice=lattice_config[mission][channel]
    n_lattice=len(xlattice)*len(ylattice)
    lattice=[None]*n_lattice
    for i_y, y in enumerate(ylattice):
        for i_x, x in enumerate(xlattice):
            i = i_y * 5 + i_x
            lattice[i]=(i_x,i_y)
    return lattice


def get_manual_reticle(mission:int,channel:str,img1:np.ndarray)->list[tuple[float,float]]:
    """

    :param mission: Mission number, IE 7=Ranger 7, etc.
    :param channel: Either A, B, or P
    :param img1: image from tab1, scaled to its nominal size (IE 1150 wide for A and B)
    :return: A list of tuples, each of which is the x and y location of a manual click
             on the scaled images.
    """

    manual_tab1_reticles={7:{
        "A":[
            #  xdata     ydata
            (  74.571,   235.829),
            ( 314.931,   236.818),
            ( 558.917,   235.170),
            ( 808.148,   233.955),
            (1060.956,   231.900),
            (  76.603,   478.858),
            ( 317.079,   479.016),
            ( 561.931,   476.805),
            ( 809.468,   475.069),
            (1060.635,   474.595),
            (  77.909,   722.763),
            ( 318.815,   721.816),
            ( 563.352,   720.711),
            ( 811.046,   719.922),
            (1060.793,   720.553),
            (  77.120,   968.879),
            ( 318.973,   969.668),
            ( 564.142,   969.826),
            ( 811.836,   970.615),
            (1060.793,   972.668),
        ],
        "B":[
            (  91.531,   219.808), #  0
            ( 330.130,   223.859), #  1
            ( 572.052,   225.833), #  2
            ( 818.025,   227.391), #  3
            (1066.802,   229.676), #  4
            (  90.077,   459.653), #  5
            ( 329.195,   462.249), #  6
            ( 570.493,   463.496), #  7
            ( 815.532,   465.158), #  8
            (1063.167,   467.755), #  9
            (  87.273,   702.717), # 10
            ( 327.325,   703.340), # 11
            ( 569.143,   704.275), # 12
            ( 813.974,   705.937), # 13
            (1060.466,   710.508), # 14
            (  81.560,   950.664), # 15
            ( 323.378,   950.872), # 16
            ( 566.858,   951.910), # 17
            ( 812.104,   954.092), # 18
            (1058.389,   959.285), # 19
        ]},
        8:{"A":[
            (  80.959,   243.018), #  0
            ( 325.298,   246.223), #  1
            ( 573.123,   245.945), #  2
            ( 825.547,   243.296), #  3
            (1080.201,   239.951), #  4
            (  83.468,   484.848), #  5
            ( 327.807,   487.079), #  6
            ( 575.074,   485.685), #  7
            ( 826.244,   483.455), #  8
            (1080.062,   482.339), #  9
            (  83.468,   728.491), # 10
            ( 328.922,   729.606), # 11
            ( 576.607,   728.909), # 12
            ( 827.916,   727.516), # 13
            (1081.455,   729.328), # 14
            (  81.377,   976.594), # 15
            ( 328.086,   977.291), # 16
            ( 576.747,   978.267), # 17
            ( 828.753,   978.685), # 18
            (1083.407,   983.703), # 19
            ],
        "B":[
            #(  79.275,    32.796), #  0
            #( 325.680,    34.996), #  1
            #( 577.271,    35.782), #  2
            #( 833.734,    33.582), #  3
            #(1094.597,    32.010), #  4
            (  80.532,   265.844), #  5
            ( 326.780,   266.787), #  6
            ( 577.114,   265.687), #  7
            ( 832.162,   263.330), #  8
            (1091.296,   261.287), #  9
            (  81.789,   497.006), # 10
            ( 328.509,   496.063), # 11
            ( 578.528,   493.549), # 12
            ( 833.419,   492.292), # 13
            (1090.668,   491.349), # 14
            (  83.046,   730.525), # 15
            ( 330.237,   728.168), # 16
            ( 580.571,   726.125), # 17
            ( 835.148,   725.654), # 18
            (1091.768,   726.911), # 19
            (  81.003,   966.088), # 20
            ( 330.237,   964.673), # 21
            ( 581.514,   963.573), # 22
            ( 836.720,   964.830), # 23
            (1092.554,   969.231), # 24
            ]}
        }

    if mission in manual_tab1_reticles and channel in manual_tab1_reticles[mission]:
        # Clicks have already been collected. The clicks below are from
        # TAB 1, scaled to have a horizontal size of 1150 pixels.
        manual_tab1_reticle=manual_tab1_reticles[mission][channel]
    else:
        # Collect the clicks
        xlattice, ylattice = lattice_config[mission][channel]
        n_lattice = len(xlattice) * len(ylattice)
        manual_tab1_reticle = [None] * n_lattice
        current_click = 0

        def on_click(event):
            if event.button==MouseButton.RIGHT:
                nonlocal current_click
                manual_tab1_reticle[current_click]=(event.xdata, event.ydata)
                print(f"    ({event.xdata:8.3f},  {event.ydata:8.3f}), # {current_click:2d}")
                plt.plot(event.xdata,event.ydata,'b+')
                plt.pause(0.001)
                current_click+=1
        plt.close('all')
        plt.figure(1)
        plt.clf()
        plt.imshow(img1)
        plt.title(f"Ranger {mission:1d} channel {channel}")
        plt.connect('button_press_event', on_click)
        plt.show()
    return manual_tab1_reticle


def calc_M_im_lat(reticle_points:np.ndarray, img:np.ndarray=None)->np.ndarray:
    """
    # Find the best fit matrix which reproduces the grid.

    :param reticle_points: Image coordinates of integer lattice points
    :return: Matrix which transforms integer lattice coordinates to image coordinates

    We are going to use a nonlinear minimizer even though the problem is linear,
    because it is easier to express the problem as a nonlinear cost.

    If the data were perfect, we would be able to scale each vector
    on the integer lattice with -2<=x<=2 and -2<=y<=1. We would have
    [a b c][x] [xd]
    [d e f][y]=[yd]
    [0 0 1][1] [1 ]
    where xd is the image coordinates of the reticle points. We will call that
    matrix [A], the left-side vector [x], and the right side data [B]. The cost
    for one point is vdot([A][x]-[B],[A][x]-[B]) and the cost for all points is
    therefore the sum of that dot product over all points.

    The cost function is in the form:
     J(x,*args)->float
    In our case, x is the parameters we are trying to minimize (a,b,c,d,e,f),
    and *args isn't needed.
    """
    def J(abcdef:np.ndarray)->float:
        cost=0.0
        a,b,c,d,e,f=abcdef
        A=np.array([[a,b,c],
                    [d,e,f],
                    [0,0,1]])

        for i_y,y in enumerate((-1,0,1,2)):
            for i_x,x in enumerate((-2,-1,0,1,2)):
                i=i_y*5+i_x
                x=np.array([[x],
                            [y],
                            [1]])
                Ax=A@x
                B=np.array([[reticle_points[i][0]],
                            [reticle_points[i][1]],
                            [1]])
                cost+=vdot(Ax-B,Ax-B)
        return cost

    result=minimize(J,(1,0,0,0,1,0))
    a,b,c,d,e,f=result.x
    A = np.array([[a, b, c],
                  [d, e, f],
                  [0, 0, 1]])
    if img is not None:
        print(A)
        plt.imshow(img)
        for i_y, y in enumerate((-1, 0, 1, 2)):
            for i_x, x in enumerate((-2, -1, 0, 1, 2)):
                i = i_y * 5 + i_x
                x = np.array([[x],
                              [y],
                              [1]])
                Ax = A @ x
                plt.plot(Ax[0,0],Ax[1,0],'b+')
        plt.show()
    return A


def sample_img_boxes(img:np.ndarray,
                     reticle_points:Iterable[tuple[float,float]],
                     box_r:int=50)->Iterable[np.ndarray]:
    """
    Sample the region around each reticle point

    :param img: Image to sample
    :param reticle_points: List of reticle points to sample around. Should
                           be a list of tuples, each tuple being the x and y
                           coordinates of the expected center of a reticle mark
    :param box_r: Square radius to sample around each reticle point
    :return: List of images
    """
    img_boxes=[None]*len(reticle_points)
    for i_reticle, (click_x,click_y) in enumerate(reticle_points):
        click_x = int(click_x)
        click_y = int(click_y)
        img_boxes[i_reticle] = img[click_y - box_r:click_y + box_r,
                                   click_x - box_r:click_x + box_r]
        if False:
            plt.clf()
            plt.subplot(2, 2, 1)
            plt.imshow(this_box)
            plt.title(f"{i_x=},{i_y=},{i=},{mask_level[i]=}")
            plt.subplot(2, 2, 2)
            plt.imshow(this_box > mask_level[i])
            plt.subplot(2, 2, 3)
            plt.imshow(synthetic_masks[i % len(synthetic_masks)])
            plt.subplot(2, 2, 4)
            hist, xs = np.histogram(this_box, bins=range(257))
            plt.plot(xs[:-1], hist)
            plt.show()
    return img_boxes


def auto_rectify(mission:int,channel:str):
    """

    :param mission:
    :param channel:
    :return:
    """
    # A is now the matrix which best converts integer lattice points to reticle coordinates
    # on an 1150-column image. Name it according to our convention M_to_from -- Matrix which
    # transforms the lattice onto image1
    tab = 1
    infn = f"raw_images/{mission:1d}{channel}/Ranger{mission:1d}{channel}{tab:03d}.jpg"
    bigimg1 = mpimg.imread(infn)
    image_sizes={7:{"A":1150,"B":1150},8:{"A":1150,"B":1150},9:{"A":1150,"B":1150}}
    try:
        mkdir(f"rect_images/{mission:1d}{channel}")
    except FileExistsError:
        oufns=glob("rect_images/{mission:1d}{channel}/*.png")
        for oufn in oufns:
            remove(oufn)
    image_size=image_sizes[mission][channel]
    img1 = scaledown(bigimg1,image_size)

    print(f"{infn},{img1.shape},{img1.dtype}")

    manual_tab1_reticle=get_manual_reticle(mission,channel,img1)
    M_im1_lat = calc_M_im_lat(manual_tab1_reticle)

    img1_boxes = sample_img_boxes(img1, manual_tab1_reticle)

    synthetic_masks=get_synthetic_masks(mission,channel)

    # For each subsequent image:
    infns=sorted(glob(f"raw_images/{mission:1d}{channel}/Ranger{mission:1d}{channel}*.jpg"))
    box_r=50
    xbox=np.array([-1,1,1,-1,-1])*box_r
    ybox=np.array([-1,-1,1,1,-1])*box_r

    for infn in infns:
        if match:=re.match(f".*/Ranger{mission:1d}{channel}(?P<tab>[0-9][0-9][0-9]).jpg",infn):
            tab=int(match.group("tab"))
        else:
            raise ValueError("Couldn't get TAB number out of filename")
        oufn = f"rect_images/{mission:1d}{channel}/Rect{mission:1d}{channel}{tab:03d}.png"
        # Scale down to 1150 lines
        bigimgn=mpimg.imread(infn)
        M_imn_big=calc_M_img_big(bigimgn.shape,image_size)
        imgn = scaledown(bigimgn,image_size)
        plt.figure(2)
        plt.clf()
        plt.imshow(imgn)
        plt.title(f"TAB {tab}")

        for x,y in manual_tab1_reticle:
            plt.plot(x+xbox,y+ybox,'r-')
        auto_tabn_reticle = [None]*20

        # Dig out the region around each reticle mark using click centers from TAB 1
        imgn_boxes=sample_img_boxes(imgn,manual_tab1_reticle,box_r=box_r)
        for i_reticle,(this_box,this_mark,(x_img1,y_img1)) in enumerate(zip(imgn_boxes,synthetic_masks,manual_tab1_reticle)):
            # Use image correlation to match the reticle mask from TAB 1 to each reticle mark
            cross=cross_image(im=255-this_box,im_ref=this_mark)
            yofs,xofs=img_offset(cross=cross,bbox_r=20)
            auto_tabn_reticle[i_reticle]=(x_img1+xofs,y_img1+yofs)
            if tab==3 and False:
                plt.figure(4)
                plt.clf()
                plt.subplot(2,2,1)
                plt.imshow(255-this_box)
                plt.title(f"This box")
                plt.plot(box_r+xofs,box_r+yofs,'r+')
                plt.subplot(2,2,2)
                plt.title(f"img1 box")
                plt.imshow(255-img1_boxes[i_reticle])
                plt.subplot(2,2,3)
                plt.title(f"synthetic mask")
                plt.imshow(synthetic_masks[i_reticle])
                plt.subplot(2,2,4)
                plt.title(f"cross")
                plt.imshow(cross)
                plt.figure(5)
                plt.plot(x_img1+xofs,y_img1+yofs,'r+')
                plt.pause(0.001)
        if tab==3 and False:
            plt.show()
        plt.figure(2)
        plt.plot([x for x,y in auto_tabn_reticle],[y for x,y in auto_tabn_reticle],'w+')
        plt.pause(0.1)

        # * Do a nonlinear minimization to find the best-fit matrix M_imn_lat which maps the lattice
        #   to this image
        M_imn_lat=calc_M_im_lat(auto_tabn_reticle)
        # * Get the matrix which transforms from imn to im1:
        M_lat_imn=np.linalg.inv(M_imn_lat)
        M_im1_imn=M_im1_lat@M_lat_imn
        M_im1_big=M_im1_imn@M_imn_big
        # Now if we transform auto_tabn_reticle with M_im1_imn, it *should* approximately
        # hit the reticle marks on img1. So, plot this and find out.
        plt.figure(1)
        plt.clf()
        plt.imshow(img1)
        plt.title(f"TAB 1 with transformed TAB {tab} reticle points")
        for x,y in auto_tabn_reticle:
            v_imn=np.array([[x],[y],[1]])
            v_im1=M_im1_imn @ v_imn
            plt.plot(v_im1[0,0],v_im1[1,0],'w+')
        print(M_im1_imn)
        # * Use the affine transform to map this image into the same space as image1
        rectified = transform_image(bigimgn, M_im1_big, output_shape=(1150,1150))
        plt.figure(3)
        plt.clf()
        plt.imshow(rectified)
        plt.title(f"rectified TAB {tab}")
        plt.plot([x for x,y in manual_tab1_reticle],[y for x,y in manual_tab1_reticle],'r+')
        plt.pause(0.1)
        Image.fromarray(rectified.astype(np.uint8), mode='L').save(oufn)


def main():
    # auto_rectify(7,"A")
    auto_rectify(8,"B")


if __name__=="__main__":
    main()