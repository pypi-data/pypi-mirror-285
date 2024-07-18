from enum import IntEnum
from typing import Union

import imagingcontrol4
import imagingcontrol4.native
from .helper import make_repr


class PixelFormat(IntEnum):
    """Defines the possible representations of pixels in an image.

    The pixel format is part of the :py:class:`.ImageType`.
    """

    Unspecified = imagingcontrol4.native.IC4_PIXEL_FORMAT.IC4_PIXEL_FORMAT_Unspecified
    """Unspecified pixel format, used to partially define a image type."""
    Mono8 = imagingcontrol4.native.IC4_PIXEL_FORMAT.IC4_PIXEL_FORMAT_Mono8
    """Monochrome 8-bit"""
    Mono10p = imagingcontrol4.native.IC4_PIXEL_FORMAT.IC4_PIXEL_FORMAT_Mono10p
    """Monochrome 10-bit packed"""
    Mono12p = imagingcontrol4.native.IC4_PIXEL_FORMAT.IC4_PIXEL_FORMAT_Mono12p
    """Monochrome 12-bit packed"""
    Mono16 = imagingcontrol4.native.IC4_PIXEL_FORMAT.IC4_PIXEL_FORMAT_Mono16
    """Monochrome 16-bit"""
    BayerBG8 = imagingcontrol4.native.IC4_PIXEL_FORMAT.IC4_PIXEL_FORMAT_BayerBG8
    """Bayer Blue-Green 8-bit"""
    BayerBG10p = imagingcontrol4.native.IC4_PIXEL_FORMAT.IC4_PIXEL_FORMAT_BayerBG10p
    """Bayer Blue-Green 10-bit packed"""
    BayerBG12p = imagingcontrol4.native.IC4_PIXEL_FORMAT.IC4_PIXEL_FORMAT_BayerBG12p
    """Bayer Blue-Green 12-bit packed"""
    BayerBG16 = imagingcontrol4.native.IC4_PIXEL_FORMAT.IC4_PIXEL_FORMAT_BayerBG16
    """Bayer Blue-Green 16-bit"""
    BayerGB8 = imagingcontrol4.native.IC4_PIXEL_FORMAT.IC4_PIXEL_FORMAT_BayerGB8
    """Bayer Green-Blue 8-bit"""
    BayerGB10p = imagingcontrol4.native.IC4_PIXEL_FORMAT.IC4_PIXEL_FORMAT_BayerGB10p
    """Bayer Green-Blue 10-bit packed"""
    BayerGB12p = imagingcontrol4.native.IC4_PIXEL_FORMAT.IC4_PIXEL_FORMAT_BayerGB12p
    """Bayer Green-Blue 12-bit packed"""
    BayerGB16 = imagingcontrol4.native.IC4_PIXEL_FORMAT.IC4_PIXEL_FORMAT_BayerGB16
    """Bayer Green-Blue 16-bit"""
    BayerGR8 = imagingcontrol4.native.IC4_PIXEL_FORMAT.IC4_PIXEL_FORMAT_BayerGR8
    """Bayer Green-Red 8-bit"""
    BayerGR10p = imagingcontrol4.native.IC4_PIXEL_FORMAT.IC4_PIXEL_FORMAT_BayerGR10p
    """Bayer Green-Red 10-bit packed"""
    BayerGR12p = imagingcontrol4.native.IC4_PIXEL_FORMAT.IC4_PIXEL_FORMAT_BayerGR12p
    """Bayer Green-Red 12-bit packed"""
    BayerGR16 = imagingcontrol4.native.IC4_PIXEL_FORMAT.IC4_PIXEL_FORMAT_BayerGR16
    """Bayer Green-Red 16-bit"""
    BayerRG8 = imagingcontrol4.native.IC4_PIXEL_FORMAT.IC4_PIXEL_FORMAT_BayerRG8
    """Bayer Red-Green 8-bit"""
    BayerRG10p = imagingcontrol4.native.IC4_PIXEL_FORMAT.IC4_PIXEL_FORMAT_BayerRG10p
    """Bayer Red-Green 10-bit packed"""
    BayerRG12p = imagingcontrol4.native.IC4_PIXEL_FORMAT.IC4_PIXEL_FORMAT_BayerRG12p
    """Bayer Red-Green 12-bit packed"""
    BayerRG16 = imagingcontrol4.native.IC4_PIXEL_FORMAT.IC4_PIXEL_FORMAT_BayerRG16
    """Bayer Red-Green 16-bit"""
    BGRa8 = imagingcontrol4.native.IC4_PIXEL_FORMAT.IC4_PIXEL_FORMAT_BGRa8
    """Blue-Green-Red-alpha 8-bit"""
    BGRa16 = imagingcontrol4.native.IC4_PIXEL_FORMAT.IC4_PIXEL_FORMAT_BGRa16
    """Blue-Green-Red-alpha 16-bit"""
    BGR8 = imagingcontrol4.native.IC4_PIXEL_FORMAT.IC4_PIXEL_FORMAT_BGR8
    """Blue-Green-Red 8-bit"""
    Mono12Packed = imagingcontrol4.native.IC4_PIXEL_FORMAT.IC4_PIXEL_FORMAT_Mono12Packed
    """GigE Vision specific format, Monochrome 12-bit packed"""
    BayerBG12Packed = imagingcontrol4.native.IC4_PIXEL_FORMAT.IC4_PIXEL_FORMAT_BayerBG12Packed
    """GigE Vision specific format, Bayer Blue-Green 12-bit packed"""
    BayerGB12Packed = imagingcontrol4.native.IC4_PIXEL_FORMAT.IC4_PIXEL_FORMAT_BayerGB12Packed
    """GigE Vision specific format, Bayer Green-Blue 12-bit packed"""
    BayerGR12Packed = imagingcontrol4.native.IC4_PIXEL_FORMAT.IC4_PIXEL_FORMAT_BayerGR12Packed
    """GigE Vision specific format, Bayer Green-Red 12-bit packed"""
    BayerRG12Packed = imagingcontrol4.native.IC4_PIXEL_FORMAT.IC4_PIXEL_FORMAT_BayerRG12Packed
    """GigE Vision specific format, Bayer Red-Green 12-bit packed"""
    YUV422_8 = imagingcontrol4.native.IC4_PIXEL_FORMAT.IC4_PIXEL_FORMAT_YUV422_8
    """YUV 4:2:2 8-bit"""
    YCbCr422_8 = imagingcontrol4.native.IC4_PIXEL_FORMAT.IC4_PIXEL_FORMAT_YCbCr422_8
    """YCbCr 4:2:2 8-bit"""
    YCbCr411_8 = imagingcontrol4.native.IC4_PIXEL_FORMAT.IC4_PIXEL_FORMAT_YCbCr411_8
    """YCbCr 4:1:1 8-bit (CbYYCrYY)"""
    YCbCr411_8_CbYYCrYY = imagingcontrol4.native.IC4_PIXEL_FORMAT.IC4_PIXEL_FORMAT_YCbCr411_8_CbYYCrYY
    """YCbCr 4:1:1 8-bit (YYCbYYCr)"""

    AnyBayer8 = imagingcontrol4.native.IC4_PIXEL_FORMAT.IC4_PIXEL_FORMAT_AnyBayer8
    """Virtual pixel format value to select any 8-bit bayer format

    Remarks:
        When setting the camera's :attr:`.PropId.PIXEL_FORMAT` to this value, automatically selects one of the 8-bit bayer pixel formats
        :attr:`.BayerBG8`, :attr:`.BayerGB8`, :attr:`.BayerRG8` or :attr:`.BayerGR8`.
    """

    AnyBayer10p = imagingcontrol4.native.IC4_PIXEL_FORMAT.IC4_PIXEL_FORMAT_AnyBayer10p
    """Virtual pixel format value to select any 10-bit packed bayer format
    
    Remarks:
        When setting the camera's :attr:`.PropId.PIXEL_FORMAT` to this value, automatically selects one of the 10-bit packed bayer pixel formats
        :attr:`.BayerBG10p`, :attr:`.BayerGB10p`, :attr:`.BayerRG10p` or :attr:`.BayerGR10p`.
    """
    AnyBayer12p = imagingcontrol4.native.IC4_PIXEL_FORMAT.IC4_PIXEL_FORMAT_AnyBayer12p
    """Virtual pixel format value to select any 12-bit packed bayer format
    
    Remarks:
        When setting the camera's :attr:`.PropId.PIXEL_FORMAT` to this value, automatically selects one of the 12-bit packed bayer pixel formats
        :attr:`.BayerBG12p`, :attr:`.BayerGB12p`, :attr:`.BayerRG12p`, :attr:`.BayerGR12p`,
        :attr:`.BayerBG12Packed`, :attr:`.BayerGB12Packed`, :attr:`.BayerRG12Packed` or :attr:`.BayerGR12Packed`.
    """
    AnyBayer16 = imagingcontrol4.native.IC4_PIXEL_FORMAT.IC4_PIXEL_FORMAT_AnyBayer16
    """Virtual pixel format value to select any 16-bit bayer format

    Remarks:
        When setting the camera's :attr:`.PropId.PIXEL_FORMAT` to this value, automatically selects one of the 16-bit bayer pixel formats
        :attr:`.BayerBG16`, :attr:`.BayerGB16`, :attr:`.BayerRG16` or :attr:`.BayerGR16`.
    """

    Invalid = imagingcontrol4.native.IC4_PIXEL_FORMAT.IC4_PIXEL_FORMAT_Invalid
    """Invalid pixel format"""


class ImageType:
    """Represents an image type, including pixel format and image dimensions."""

    def __init__(
        self, pixel_format: Union[PixelFormat, int] = PixelFormat.Unspecified, width: int = 0, height: int = 0
    ):
        fmt_value: int

        if isinstance(pixel_format, PixelFormat):
            fmt_value = pixel_format.value
        else:
            fmt_value = pixel_format

        self._image_type = imagingcontrol4.native.IC4_IMAGE_TYPE(fmt_value, width, height)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ImageType):
            raise NotImplementedError()

        if self.pixel_format != other.pixel_format:
            return False
        if self.width != other.width:
            return False
        if self.height != other.height:
            return False
        return True

    def __repr__(self) -> str:
        return make_repr(self, ImageType.pixel_format, ImageType.width, ImageType.height)

    @classmethod
    def _from_native(cls, native: imagingcontrol4.native.IC4_IMAGE_TYPE):
        return cls(native.pixel_format, native.width, native.height)

    @property
    def pixel_format(self) -> Union[PixelFormat, int]:
        """The pixel format of the image

        Returns:
            Union[PixelFormat, int]: The pixel format of an image. This may be of type `int`, if the actual pixel
            format is not a member of the :py:class:`.PixelFormat` enumeration.
        """
        try:
            return PixelFormat(self._image_type.pixel_format)
        except ValueError:
            return int(self._image_type.pixel_format)

    @property
    def width(self) -> int:
        """The width of the image

        Returns:
            int: The width of the image
        """
        return self._image_type.width

    @property
    def height(self) -> int:
        """The height of the image

        Returns:
            int: The height of the image
        """
        return self._image_type.height

    def _to_native(self):
        return self._image_type
