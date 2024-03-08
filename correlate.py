import numpy as np
import scipy

def cross_image(im:np.array, im_ref:np.array)->np.array:
    """
    Cross-correlation of image using 2D FFT, from https://stackoverflow.com/a/24769222

    :param im: Input image to check for cross-correlation.
    :param im_ref:  reference image, must be same size and shape as im1
    :return: Image of cross-correlation, will be same size as im and im_ref.

    The cross-correlation is how much the two images "correlate". Conceptually
    it can be calculated by generating a result image, then for each pixel in the result:
    * Roll one of the images by the distance from the center to this result pixel.
      The center pixel represents a null roll. Pixels to the left of center roll one image left,
      etc.
    * Multiply the rolled image by the other image
    * The pixel value in the result is the sum of this product.

    The second image is called the "reference" image because if the first image is created from
    the second using something like np.roll(), then the bright spot in the correlation will be
    shifted from center in the same direction by the same amount.

    example:

      img_move=np.roll(img_ref,(60,0),axis=(0,1)) #Make a copy of the reference image and roll it up 60 pixels
      cross_image(img_move,img_ref) # will have a bright spot 60 pixels above and on-center left to right

    """

    # calculate the correlation image; note the flipping of one of the images. Subtract the
    # mean from each image so that the DC component doesn't interfere with things.
    return scipy.signal.fftconvolve(im-np.mean(im), im_ref[::-1,::-1]-np.mean(im_ref), mode='same')


def img_offset(im:np.array=None,im_ref:np.array=None,cross:np.array=None,bbox_r:int=None)->np.array:
    """
    Calculate the image offset between two images. If a rolled copy of a reference image
    is compared to the reference, the offset should exactly equal the roll. This is calculated
    using image correlation so should produce somewhat-valid answers if the images are
    somewhat-similar.

    :param im:
    :param im_ref:
    :param cross: Optional pre-calculated cross-correlation, should equal cross_image(im,im_ref)
    :return: 2D vector offset -- first element is vertical offset, where positive means that
             the rolled image is above the reference. Second element is horizontal offset, where
             positive means that the rolled image is to the right of the reference. If you use
             the result as the argument of np.roll(), it will roll the reference image onto the
             rolled image.

    example:
    img=...
    img_roll=np.roll(img,(y_roll,x_roll),axes=(0,1))
    offset=img_offset(img_roll,img) #should be near (y_roll,x_roll)
    assert np.allclose(img_roll,np.roll(img,offset,axes=(0,1)) #Roll the reference to see if it matches up
    """
    if cross is None:
        cross=cross_image(im,im_ref)
    if bbox_r is not None:
        cross_rx=cross.shape[1]//2
        cross_ry=cross.shape[0]//2
        cross=cross[cross_ry-bbox_r:cross_ry+bbox_r,cross_rx-bbox_r:cross_rx+bbox_r]
    offset = np.array(np.unravel_index(cross.argmax(), cross.shape)) - np.array(cross.shape) // 2
    return offset


