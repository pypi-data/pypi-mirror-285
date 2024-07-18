#
# postprocessor.py - DeGirum Python SDK: inference results postprocessing
# Copyright DeGirum Corp. 2022
#
# Implements InferenceResult classes to handle different types of specific inference results data.
#

import copy
import itertools
import math
import numpy
import yaml
from typing import Union
from collections.abc import Iterable
import base64

from .exceptions import DegirumException, validate_color_tuple
from ._draw_primitives import create_draw_primitives, _inv_conversion_calc
from .log import log_wrap


class _ListFlowTrue(list):
    """list subclass to specify custom yaml style"""


# add custom representer for list type with flow_style=True
yaml.add_representer(
    _ListFlowTrue,
    lambda dumper, data: dumper.represent_sequence(
        "tag:yaml.org,2002:seq", data, flow_style=True
    ),
)


def _format_num(number, precision=2):
    "Return formatted number based on type of numeric value"
    if isinstance(number, int):
        return str(number)
    else:
        return f"{number:.{precision}f}"


class InferenceResults:
    """Inference results container class.

    This class is a base class for a set of classes designed to handle
    inference results of particular model types such as classification, detection etc.

    !!! note

        You never construct model objects yourself. Objects of those classes are returned by various predict
        methods of [degirum.model.Model][] class.
    """

    @log_wrap
    def __init__(
        self,
        *,
        model_params,
        input_image=None,
        model_image=None,
        inference_results,
        draw_color=(255, 255, 128),
        line_width: int = 3,
        show_labels: bool = True,
        show_probabilities: bool = False,
        alpha: Union[float, str] = "auto",
        font_scale: float = 1.0,
        fill_color=(0, 0, 0),
        frame_info=None,
        conversion,
        label_dictionary={},
    ):
        """Constructor.

        !!! note

            You never construct `InferenceResults` objects yourself -- the ancestors of this class are returned
            as results of AI inferences from [degirum.model.Model.predict][], [degirum.model.Model.predict_batch][],
            and [degirum.model.Model.predict_dir][] methods.

        Args:
            model_params (ModelParams): Model parameters object as returned by [degirum.model.Model.model_info][].
            input_image (any): Original input data.
            model_image (any): Input data converted per AI model input specifications.
            inference_results (list): Inference results data.
            draw_color (tuple): Color for inference results drawing on overlay image.
            line_width: Line width in pixels for inference results drawing on overlay image.
            show_labels: True to draw class labels on overlay image.
            show_probabilities: True to draw class probabilities on overlay image.
            alpha: Alpha-blend weight for overlay details.
            font_scale: Font scale to use for overlay text.
            fill_color (tuple): RGB color tuple to use for filling if any form of padding is used.
            frame_info (any): Input data frame information object.
            conversion (Callable): Coordinate conversion function accepting two arguments `(x,y)` and returning two-element tuple.
                This function should convert model-based coordinates to input image coordinates.
            label_dictionary (dict[str, str]): Model label dictionary.

        """
        self._model_params = model_params
        self._input_image = input_image
        self._model_image = model_image
        self._inference_results = copy.deepcopy(inference_results)
        self._overlay_color = draw_color
        self._show_labels = show_labels
        self._show_labels_below = True
        self._show_probabilities = show_probabilities
        self._line_width = line_width
        self._alpha = 1.0 if alpha == "auto" else float(alpha)
        self._font_scale = font_scale
        self._fill_color = fill_color
        self._frame_info = frame_info
        self._conversion = conversion
        self._label_dictionary = label_dictionary

    def __str__(self):
        """Conversion to string"""
        return str(self._inference_results)

    def __repr__(self):
        return self.__str__()

    def __dir__(self):
        return [
            "generate_colors",
            "image",
            "image_model",
            "image_overlay",
            "info",
            "overlay_alpha",
            "overlay_fill_color",
            "overlay_font_scale",
            "overlay_line_width",
            "overlay_color",
            "overlay_show_labels",
            "overlay_show_probabilities",
            "results",
            "type",
        ]

    @property
    def image(self):
        """Original image.

        Returned image object type is defined by the selected graphical backend (see [degirum.model.Model.image_backend][]).
        """
        return self._input_image

    @property
    def image_overlay(self):
        """Image with AI inference results drawn on a top of original image.

        Drawing details depend on the inference result type:

        - For classification models the list of class labels with probabilities is printed below the original image.
        - For object detection models bounding boxes of detected object are drawn on the original image.
        - For pose detection models detected keypoints and keypoint connections are drawn on the original image.
        - For segmentation models detected segments are drawn on the original image.

        Returned image object type is defined by the selected graphical backend (see [degirum.model.Model.image_backend][]).
        """
        return copy.deepcopy(self._input_image)

    @property
    def image_model(self):
        """Model input image data: image converted to AI model input specifications.

        Image type is raw binary array."""
        return self._model_image

    @property
    def results(self) -> list:
        """Inference results list.

        Each element of the list is a dictionary containing information about one inference result.
        The dictionary contents depends on the AI model.


        **For classification models** each inference result dictionary contains the following keys:

        - `category_id`: class numeric ID.
        - `label`: class label string.
        - `score`: class probability.

        Example:
        ```
        [
            {'category_id': 0, 'label': 'cat', 'score': 0.99},
            {'category_id': 1, 'label': 'dog', 'score': 0.01}
        ]
        ```

        **For multi-label classification models** each inference result dictionary contains the following keys:

        - `classifier`: object class string.
        - `results`: list of class labels and its scores. Scores are optional.

        The `results` list element is a dictionary with the following keys:

        - `label`: class label string.
        - `score`: optional class label probability.

        Example:
        ```
        [
            {
                'classifier': 'vehicle color',
                'results': [
                                        {'label': 'red', 'score': 0.99},
                                        {'label': 'blue', 'score': 0.01}
                                ]
            },
            {
                'classifier': 'vehicle type',
                'results': [
                                        {'label': 'car', 'score': 0.99},
                    {'label': 'truck', 'score': 0.01}
                                ]
            }
        ]
        ```


        **For object detection models** each inference result dictionary may contain the following keys:

        - `category_id`: detected object class numeric ID.
        - `label`: detected object class label string.
        - `score`: detected object probability.
        - `bbox`: detected object bounding box list `[xtop, ytop, xbot, ybot]`.
        - `landmarks`: optional list of keypoints or landmarks. It is the list of dictionaries, one per each keypoint/landmark.
        - `mask`: optinal dictionary of run-length encoded (RLE) object segmentation mask array representation.

        The `landmarks` list is defined for special cases like pose detection of face points detection results.
        Each `landmarks` list element is a dictionary with the following keys:

        - `category_id`: keypoint numeric ID.
        - `label`: keypoint label string.
        - `score`: keypoint detection probability.
        - `landmark`: keypoint coordinate list `[x,y]`.
        - `connect`: optional list of IDs of connected keypoints.

        The `mask` dictionary is defined for the special case of object segmentation results, with the following keys:

        - `height`: height of segmentation mask array
        - `width`: width of segmentation mask array
        - `data`: string representation of a buffer of unsigned 32-bit integers carrying the RLE segmentation mask array.

        The object detection keys (`bbox`, `score`, `label`, and `category_id`) must be either all present or all absent.
        In the former case the result format is suitable to represent pure object detection results.
        In the later case, one of the following keys must be present:

        - the `landmarks` key
        - the `mask` key

        The following statements are then true:

        - If the `landmarks` key is present, the result format is suitable to represent pure landmark detection results, such as pose detection.
        - If the `mask` key is present, the result format is suitable to represent pure segmentation results. If, optionally,
            the `category_id` key is also present, the result format is suitable to represent semantic segmentation results.

        When both object detection keys and the `landmarks` key are present, the result format is suitable to represent mixed model results,
        when the model detects not only object bounding boxes, but also keypoints/landmarks within the bounding box.

        When both object detection keys and the `mask` key are present, the result format is suitable to represent mixed model results,
        when the model detects not only object bounding boxes, but also segmentation masks within the bounding box (i.e. instance segmentation).

        Example of pure object detection results:
        ```
        [
            {'category_id': 0, 'label': 'cat', 'score': 0.99, 'bbox': [10, 20, 100, 200]},
            {'category_id': 1, 'label': 'dog', 'score': 0.01, 'bbox': [200, 100, 300, 400]}
        ]
        ```

        Example of landmark object detection results:
        ```
        [
            {
                'landmarks': [
                    {'category_id': 0, 'label': 'Nose', 'score': 0.99, 'landmark': [10, 20]},
                    {'category_id': 1, 'label': 'LeftEye', 'score': 0.98, 'landmark': [15, 25]},
                    {'category_id': 2, 'label': 'RightEye', 'score': 0.97, 'landmark': [18, 28]}
                ]
            }
        ]
        ```

        Example of segmented object detection results:
        ```
        [
            {
                'mask': {'height': 2, 'width': 2, 'data': 'AAAAAAEAAAAAAAAAAQAAAAIAAAABAAAA'}
            }
        ]
        ```

        **For hand palm detection** models each inference result dictionary contains the following keys:

        - `score`: probability of detected hand.
        - `handedness`: probability of right hand.
        - `landmarks`: list of dictionaries, one per each hand keypoint.

        Each `landmarks` list element is a dictionary with the following keys:

        - `label`: classified object class label.
        - `category_id`: classified object class index.
        - `landmark`: landmark point coordinate list `[x, y, z]`.
        - `world_landmark`: metric world landmark point coordinate list `[x, y, z]`.
        - `connect`: list of adjacent landmarks indexes.

        Example:
        ```
        [
            {
                'score': 0.99,
                'handedness': 0.98,
                'landmarks': [
                    {
                        'label': 'Wrist',
                        'category_id': 0,
                        'landmark': [10, 20, 30],
                        'world_landmark': [10, 20, 30],
                        'connect': [1]
                    },
                    {
                        'label': 'Thumb',
                        'category_id': 1,
                        'landmark': [15, 25, 35],
                        'world_landmark': [15, 25, 35],
                        'connect': [0]
                    }
                ]
            }
        ]
        ```

        **For segmentation models** inference result is a single-element list. That single element is a dictionary,
        containing single key `data`. The value of this key is 2D numpy array of integers, where each integer value
        represents a class ID of the corresponding pixel. The class IDs are defined by the model label dictionary.

        Example:
        ```
        [
            {
                'data': numpy.array([
                    [0, 0, 0, 1, 1, 1],
                    [0, 0, 0, 1, 1, 1],
                    [0, 0, 0, 1, 1, 1],
                    [2, 2, 2, 3, 3, 3],
                    [2, 2, 2, 3, 3, 3],
                    [2, 2, 2, 3, 3, 3],
                ])
            }
        ]
        ```

        """
        return self._inference_results

    @property
    def type(self) -> str:
        """Inference result type: one of

        - `"classification"`
        - `"detection"`
        - `"pose detection"`
        - `"segmentation"`
        """
        known_types = dict(
            InferenceResults="base",
            ClassificationResults="classification",
            DetectionResults="detection",
            Pose_DetectionResults="pose detection",
            SegmentationResults="segmentation",
        )
        return known_types.get(type(self).__name__, "")

    @property
    def overlay_color(self):
        """Color for inference results drawing on overlay image.

        3-element RGB tuple or list of 3-element RGB tuples."""
        return copy.deepcopy(self._overlay_color)

    @overlay_color.setter
    def overlay_color(self, val):
        if isinstance(val, Iterable) and all(isinstance(e, Iterable) for e in val):
            # sequence of colors
            self._overlay_color = [validate_color_tuple(e) for e in val]
        else:
            # single color
            self._overlay_color = validate_color_tuple(val)

    @property
    def overlay_show_labels(self) -> bool:
        """Specifies if class labels should be drawn on overlay image."""
        return self._show_labels

    @overlay_show_labels.setter
    def overlay_show_labels(self, val):
        self._show_labels = val

    @property
    def overlay_show_probabilities(self) -> bool:
        """Specifies if class probabilities should be drawn on overlay image."""
        return self._show_probabilities

    @overlay_show_probabilities.setter
    def overlay_show_probabilities(self, val):
        self._show_probabilities = val

    @property
    def overlay_line_width(self) -> int:
        """Line width in pixels for inference results drawing on overlay image."""
        return self._line_width

    @overlay_line_width.setter
    def overlay_line_width(self, val):
        self._line_width = val

    @property
    def overlay_alpha(self) -> float:
        """Alpha-blend weight for overlay details."""
        return self._alpha

    @overlay_alpha.setter
    def overlay_alpha(self, val):
        self._alpha = val
        if hasattr(self, "_segm_alpha"):
            self._segm_alpha = val

    @property
    def overlay_font_scale(self) -> float:
        """Font scale to use for overlay text."""
        return self._font_scale

    @overlay_font_scale.setter
    def overlay_font_scale(self, val):
        self._font_scale = val

    @property
    def overlay_fill_color(self) -> tuple:
        """Image fill color in case of image padding.

        3-element RGB tuple."""
        return self._fill_color

    @overlay_fill_color.setter
    def overlay_fill_color(self, val: tuple):
        self._fill_color = validate_color_tuple(val)

    @property
    def info(self):
        """Input data frame information object."""
        return self._frame_info

    @staticmethod
    def generate_colors():
        """Generate a list of unique RGB color tuples."""
        bits = lambda n, f: numpy.array(
            list(numpy.binary_repr(n, 24)[f::-3]), numpy.uint8
        )
        return [
            (
                int(numpy.packbits(bits(x, -3)).item()),
                int(numpy.packbits(bits(x, -2)).item()),
                int(numpy.packbits(bits(x, -1)).item()),
            )
            for x in range(256)
        ]

    @staticmethod
    def generate_overlay_color(model_params, label_dict) -> Union[list, tuple]:
        """Overlay colors generator.

        Args:
            model_params (ModelParams): Model parameters.
            label_dict (dict): Model labels dictionary.

        Returns:
            Overlay color tuple or list of tuples.
        """
        return (255, 255, 0)


class ClassificationResults(InferenceResults):
    """InferenceResult class implementation for classification results type"""

    @log_wrap
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    __init__.__doc__ = InferenceResults.__init__.__doc__

    def __dir__(self):
        return super().__dir__() + ["overlay_show_labels_below"]

    @property
    def overlay_show_labels_below(self):
        """Specifies if overlay labels should be drawn below the image or on image itself"""
        return self._show_labels_below

    @overlay_show_labels_below.setter
    def overlay_show_labels_below(self, val):
        self._show_labels_below = val

    @property
    def image_overlay(self):
        """Image with AI inference results drawn. Image type is defined by the selected graphical backend.
        Each time this property is accessed, new overlay image object is created and all overlay details
        are redrawn according to the current settings of overlay_*** properties.
        """
        prev_bbox = (0, 0, 0, 0)
        spacer = 3

        def get_string():
            for res in self._inference_results:
                if "label" not in res or "score" not in res:
                    continue
                if self._show_labels and self._show_probabilities:
                    str = f"{res['label']}: {_format_num(res['score'])}"
                elif self._show_labels:
                    str = res["label"]
                elif self._show_probabilities:
                    str = _format_num(res["score"])
                else:
                    str = ""
                yield str

        draw = create_draw_primitives(
            self._input_image, self._alpha, self._alpha, self._font_scale
        )
        if self._show_labels_below and (self._show_labels or self._show_probabilities):
            w = 0
            h = 0
            for label in get_string():
                lw, lh, _ = draw.text_size(label)
                w = max(w, 2 * spacer + lw)
                h += spacer + lh
            if h > 0:
                h += spacer
            w, h = draw.image_overlay_extend(w, h, self._fill_color)
            prev_bbox = (0, 0, 0, h)

        current_color_set = itertools.cycle(
            self._overlay_color
            if isinstance(self._overlay_color, list)
            else [self._overlay_color]
        )
        if self._show_labels or self._show_probabilities:
            for label in get_string():
                overlay_color = next(current_color_set)
                prev_bbox = draw.draw_text(
                    spacer, prev_bbox[3] + spacer, overlay_color, label
                )

        return draw.image_overlay()

    def __str__(self):
        """
        Convert inference results to string
        """
        res_list = []
        for el in self._inference_results:
            d = {}
            if "label" in el:
                d["label"] = el["label"]
            if "score" in el:
                d["score"] = el["score"]
            if "category_id" in el:
                d["category_id"] = el["category_id"]
            res_list.append(d)
        return yaml.safe_dump(res_list, sort_keys=False)


class MultiLabelClassificationResults(InferenceResults):
    """InferenceResult class implementation for multi-label classification results type"""

    @log_wrap
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    __init__.__doc__ = InferenceResults.__init__.__doc__

    def __dir__(self):
        return super().__dir__() + ["overlay_show_labels_below"]

    @property
    def overlay_show_labels_below(self):
        """Specifies if overlay labels should be drawn below the image or on image itself"""
        return self._show_labels_below

    @overlay_show_labels_below.setter
    def overlay_show_labels_below(self, val):
        self._show_labels_below = val

    @property
    def image_overlay(self):
        """Image with AI inference results drawn. Image type is defined by the selected graphical backend.
        Each time this property is accessed, new overlay image object is created and all overlay details
        are redrawn according to the current settings of overlay_*** properties.
        """
        prev_bbox = (0, 0, 0, 0)
        spacer = 3
        indentation = 2

        def get_string():
            for result in self._inference_results:
                if "classifier" not in result or "results" not in result:
                    continue
                str = f"{result['classifier']}:"
                for labels in result["results"]:
                    if "label" not in labels:
                        continue
                    if (
                        "score" in labels
                        and self._show_probabilities
                        and self._show_labels
                    ):
                        str += f"\n{' ' * indentation}{labels['label']}: {_format_num(labels['score'])}"
                    elif self._show_labels:
                        str += f"\n{' ' * indentation}{labels['label']}"
                    elif self._show_probabilities:
                        str += f"\n{' ' * indentation}{_format_num(labels['score'])}"
                    else:
                        str = ""
                yield str

        draw = create_draw_primitives(
            self._input_image, self._alpha, self._alpha, self._font_scale
        )
        if self._show_labels_below and (self._show_labels or self._show_probabilities):
            w = 0
            h = 0
            for lbs in get_string():
                labels_list = lbs.split("\n")
                for res_string in labels_list:
                    lw, lh, _ = draw.text_size(res_string)
                    w = max(w, spacer + lw)
                    h += spacer + lh
            if h > 0:
                h += spacer
            w, h = draw.image_overlay_extend(w, h, self._fill_color)
            prev_bbox = (0, 0, 0, h)

        current_color_set = itertools.cycle(
            self._overlay_color
            if isinstance(self._overlay_color, list)
            else [self._overlay_color]
        )
        if self._show_labels or self._show_probabilities:
            for lbs in get_string():
                labels_list = lbs.split("\n")
                for res_string in labels_list:
                    overlay_color = next(current_color_set)
                    prev_bbox = draw.draw_text(
                        spacer, prev_bbox[3] + spacer, overlay_color, res_string
                    )
        return draw.image_overlay()

    def __str__(self):
        """
        Convert inference results to string
        """
        res_list = []
        for el in self._inference_results:
            d = {}
            if "classifier" in el:
                d["classifier"] = el["classifier"]
            if "results" in el:
                d["results"] = el["results"]
                for labels in el:
                    if "label" in labels:
                        d["label"] = labels["label"]
                    if "score" in labels:
                        d["score"] = labels["score"]
            res_list.append(d)
        return yaml.safe_dump(res_list, sort_keys=False)


class DetectionResults(InferenceResults):
    """InferenceResult class implementation for detection results type"""

    max_colors = 255

    @log_wrap
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mask_result = None
        self.masks_present = False
        if "alpha" in kwargs and kwargs["alpha"] == "auto":
            self._segm_alpha = 0.5
        else:
            self._segm_alpha = self._alpha
        for res in self._inference_results:
            if "bbox" in res:
                box = res["bbox"]
                res["bbox"] = [
                    *self._conversion(*box[:2]),
                    *self._conversion(*box[2:]),
                ]
            if "landmarks" in res:
                for m in res["landmarks"]:
                    m["landmark"] = [
                        *self._conversion(*m["landmark"]),
                    ]
            if "mask" in res:
                if not self.masks_present:
                    self.masks_present = True
                res["mask"] = numpy.array(self._run_length_decode(res["mask"])).astype(
                    numpy.float32
                )
                res["mask"] = self._resize_mask(res["mask"])

    __init__.__doc__ = InferenceResults.__init__.__doc__

    def _run_length_decode(self, rle):
        """
        Returns NumPy array for run length encoded string, reshaped to specified shape

        Args:
            rle (dict): RLE image segmentation mask dictionary

        Returns:
            results (NumPy array): NumPy array, representing an image segmentation mask.
        """
        rle_array = numpy.frombuffer(base64.b64decode(rle["data"]), dtype=numpy.uint32)
        N = len(rle_array) // 2
        return numpy.repeat(rle_array[:N], rle_array[N:]).reshape(
            (rle["height"], rle["width"])
        )

    def _resize_mask(self, mask):
        """Return image segmentation mask scaled with respect to the provided image transformation callback

        - `conversion`: coordinate conversion function accepting two arguments (x,y) and returning two-element tuple
        - `overlay_data`: overlay data to blend on top of input image
        - `original_width`: original image width
        - `original_height`: original image height
        """
        import cv2

        # map corners from original image to model output
        original_height, original_width = (
            self._input_image.shape[:2]
            if hasattr(self._input_image, "shape")
            else (self._input_image.height, self._input_image.width)
        )
        height, width = mask.shape
        inv_conversion = _inv_conversion_calc(self._conversion, width, height)
        p1 = [int(round(i)) for i in inv_conversion(0, 0)]
        p2 = [int(round(i)) for i in inv_conversion(original_width, original_height)]

        img = mask[
            max(p1[1], 0) : min(p2[1], height), max(p1[0], 0) : min(p2[0], width)
        ]

        # add padding to cropped image
        if p1[0] < 0 or p1[1] < 0 or p2[0] > width or p2[1] > height:
            background = numpy.zeros((p2[1] - p1[1], p2[0] - p1[0]), img.dtype)
            background[
                abs(p1[1]) : (abs(p1[1]) + img.shape[0]),
                abs(p1[0]) : (abs(p1[0]) + img.shape[1]),
            ] = img
            img = background

        mask = cv2.resize(
            img, (original_width, original_height), interpolation=cv2.INTER_LINEAR
        )
        return mask

    # deduce color based on category_id or label
    def _deduce_color(self, id, label, current_color_set):
        if label is None:
            if id is None:
                # both label and id are missing: simply use next color
                return next(current_color_set)
            else:
                # label is missing, but id is there: use id
                pass
        else:
            if id is None:
                # id is missing: use label hash
                id = hash(label)
            else:
                if (
                    self._label_dictionary is not None
                    and self._label_dictionary.get(id, "") != label
                ):
                    # label with this id is not in dictionary
                    id = self._label_dictionary.get(label, None)
                    if id is None:
                        # label is not in dictionary: add it in reverse lookup manner assigning new unique id
                        id = 1 + max(
                            (
                                k
                                if isinstance(k, int)
                                else (v if isinstance(v, int) else 0)
                            )
                            for k, v in self._label_dictionary.items()
                        )
                        self._label_dictionary[label] = id
                    else:
                        # id is in dictionary in reverse lookup manner: use it
                        pass
                else:
                    # both label and id are there, and label matches id: use id
                    pass

        return self._overlay_color[id % len(self._overlay_color)]

    @staticmethod
    def generate_overlay_color(model_params, label_dict) -> list:
        """Overlay colors generator.

        Returns:
            general overlay color data for segmentation results
        """
        colors = InferenceResults.generate_colors()
        if not label_dict:
            if model_params.OutputNumClasses <= 0:
                raise DegirumException(
                    "Detection Postprocessor: either non empty labels dictionary or OutputNumClasses greater than 0 must be specified for Detection postprocessor"
                )
            colors = colors[1 : model_params.OutputNumClasses + 1]

        else:
            if any(not isinstance(k, int) for k in label_dict.keys()):
                raise DegirumException(
                    "Detection Postprocessor: non integer keys in label dictionary are not supported"
                )
            if any(k < 0 for k in label_dict.keys()):
                raise DegirumException(
                    "Detection Postprocessor: label key values must be greater than 0"
                )
            colors = colors[1 : len(label_dict) + 1]
        colors[0] = (255, 255, 0)
        return colors

    @property
    def image_overlay(self):
        """Image with AI inference results drawn. Image type is defined by the selected graphical backend."""
        segm_alpha = self._segm_alpha if self.masks_present else None
        draw = create_draw_primitives(
            self._input_image, self._alpha, segm_alpha, self._font_scale
        )
        many_colors = isinstance(self._overlay_color, list)
        current_color_set = itertools.cycle(
            self._overlay_color if many_colors else [self._overlay_color]
        )

        line_width = self._line_width
        show_labels = self._show_labels
        show_probabilities = self._show_probabilities
        spacer = 3 * line_width

        for res in self._inference_results:
            label = res.get("label", None)
            id = res.get("category_id", None)
            overlay_color = (
                self._deduce_color(id, label, current_color_set)
                if many_colors
                else self._overlay_color
            )

            box = res.get("bbox", None)
            if box is not None:
                draw.draw_box(*box, line_width, overlay_color)

                show_labels_and_label_is_not_none = show_labels and label is not None
                str = label if show_labels_and_label_is_not_none else ""
                if show_probabilities:
                    score = res.get("score", None)
                    if score is not None:
                        str = (
                            f"{label}: {_format_num(score)}"
                            if show_labels_and_label_is_not_none
                            else _format_num(score)
                        )

                if str != "":
                    draw.draw_text_label(*box, overlay_color, str, line_width)

            landmarks = res.get("landmarks", None)
            if landmarks is not None:
                for landmark in landmarks:
                    point = landmark["landmark"]
                    draw.draw_circle(
                        point[0],
                        point[1],
                        2,
                        line_width,
                        overlay_color,
                        True,
                    )

                    lm_connect = landmark.get("connect", None)
                    if lm_connect is not None:
                        for neighbor in lm_connect:
                            point2 = landmarks[neighbor]["landmark"]
                            draw.draw_line(
                                point[0],
                                point[1],
                                point2[0],
                                point2[1],
                                line_width,
                                overlay_color,
                            )

                    lm_label = landmark.get("label", None)
                    show_lm_labels = show_labels and lm_label is not None
                    str = lm_label if show_lm_labels else ""
                    if show_probabilities:
                        score = landmark.get("score", None)
                        if score is not None:
                            str = (
                                f"{lm_label}: {_format_num(score)}"
                                if show_lm_labels
                                else _format_num(score)
                            )

                    if str != "":
                        draw.draw_text_label(
                            point[0] + spacer,
                            point[1] - spacer,
                            point[0] + spacer,
                            point[1] + spacer,
                            overlay_color,
                            str,
                            line_width,
                        )

            mask = res.get("mask", None)
            if mask is not None:
                if self.mask_result is None:
                    self.mask_result = numpy.zeros(mask.shape).astype(numpy.uint8)
                category_id = res.get("category_id", 0)
                render_mask = (mask > 0).astype(numpy.uint8) * (
                    category_id % DetectionResults.max_colors + 1
                )
                merge_condition = render_mask != 0
                self.mask_result = numpy.where(
                    merge_condition, render_mask, self.mask_result
                )

        if self.mask_result is not None:
            lut = numpy.empty((256, 1, 3), dtype=numpy.uint8)
            lut[:, :, :] = (0, 0, 0)  # default non-mask color
            for i in range(1, 256):
                lut[i, :, :] = next(current_color_set)

            draw.image_segmentation_overlay(
                self._conversion, self.mask_result, lut, convert=False
            )

        return draw.image_overlay()

    def __str__(self):
        """
        Convert inference results to string
        """
        results = copy.deepcopy(self._inference_results)
        for res in results:
            if "bbox" in res:
                res["bbox"] = _ListFlowTrue(res["bbox"])
            if "landmarks" in res:
                for lm in res["landmarks"]:
                    if "landmark" in lm:
                        lm["landmark"] = _ListFlowTrue(lm["landmark"])
                        if "connect" in lm:
                            if "label" in lm:
                                lm["connect"] = _ListFlowTrue(
                                    [
                                        res["landmarks"][e]["label"]
                                        for e in lm["connect"]
                                    ]
                                )
                            else:
                                lm["connect"] = _ListFlowTrue(lm["connect"])
            if "mask" in res:
                del res["mask"]

        return yaml.dump(results, sort_keys=False)


class Hand_DetectionResults(InferenceResults):
    """InferenceResult class implementation for pose detection results type"""

    @log_wrap
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for el in self._inference_results:
            if "landmarks" in el:
                for m in el["landmarks"]:
                    m["landmark"] = [
                        *self._conversion(*m["landmark"][:2]),
                        m["landmark"][2],
                    ]

    __init__.__doc__ = InferenceResults.__init__.__doc__

    def get_distance_color(self, value):
        value = max(-1, min(1, value))
        sigma = 0.5
        offset = 0.6
        red = int(math.exp(-((value - offset) ** 2) / (2 * (sigma) ** 2)) * 256)
        red = max(0, min(255, red))
        green = int(math.exp(-((value) ** 2) / (2 * (sigma) ** 2)) * 256)
        green = max(0, min(255, green))
        blue = int(math.exp(-((value + offset) ** 2) / (2 * (sigma) ** 2)) * 256)
        blue = max(0, min(255, blue))
        return (red, green, blue)

    @property
    def image_overlay(self):
        """Image with AI inference results drawn. Image type is defined by the selected graphical backend."""

        draw = create_draw_primitives(
            self._input_image, self._alpha, self._alpha, self._font_scale
        )
        current_color_set = itertools.cycle(
            self._overlay_color
            if isinstance(self._overlay_color, list)
            else [self._overlay_color]
        )
        for res in self._inference_results:
            if "landmarks" not in res or "score" not in res or "handedness" not in res:
                continue
            landmarks = res["landmarks"]
            overlay_color = next(current_color_set)
            for landmark in landmarks:
                point = landmark["landmark"]

                # draw lines
                for neighbor in landmark["connect"]:
                    point2 = landmarks[neighbor]["landmark"]
                    draw.draw_line(
                        point[0],
                        point[1],
                        point2[0],
                        point2[1],
                        self._line_width,
                        overlay_color,
                    )

                point_color = self.get_distance_color(
                    point[2] / self._model_params.InputH[0] * 3
                )

                # then draw point
                draw.draw_circle(
                    point[0],
                    point[1],
                    2 * self._line_width,
                    self._line_width,
                    point_color,
                    fill=True,
                )

                str = ""
                # draw probabilities on wrist only
                if self._show_labels:
                    str = landmark["label"]
                    if self._show_probabilities and landmark["label"] == "Wrist":
                        str = f"{str}:{_format_num(res['score'])},"
                        if res["handedness"] > 0.5:
                            str = f"{str} right:{res['handedness']:5.2f}"
                        else:
                            str = f"{str} left:{(1 - res['handedness']):5.2f}"
                elif self._show_probabilities and landmark["label"] == "Wrist":
                    str = f"{_format_num(res['score'])},"
                    if res["handedness"] > 0.5:
                        str = f"{str} right:{res['handedness']:5.2f}"
                    else:
                        str = f"{str} left:{(1 - res['handedness']):5.2f}"

                if str != "":
                    spacer = 3 * self._line_width
                    draw.draw_text_label(
                        point[0] + spacer,
                        point[1] - spacer,
                        point[0] + spacer,
                        point[1] + spacer,
                        overlay_color,
                        str,
                        self._line_width,
                    )

        return draw.image_overlay()

    def __str__(self):
        """
        Convert inference results to string
        """

        def landmarks(marks):
            return [
                dict(
                    label=m["label"],
                    category_id=m["category_id"],
                    landmark=_ListFlowTrue(m["landmark"]),
                    world_landmark=_ListFlowTrue(m["world_landmark"]),
                    connect=_ListFlowTrue([marks[e]["label"] for e in m["connect"]]),
                )
                for m in marks
            ]

        res_list = []
        for el in self._inference_results:
            d = {}
            if "score" in el:
                d["score"] = el["score"]
            if "handedness" in el:
                d["handedness"] = el["handedness"]
            if "landmarks" in el:
                d["landmarks"] = landmarks(el["landmarks"])
            res_list.append(d)

        return yaml.dump(res_list, sort_keys=False)


class SegmentationResults(InferenceResults):
    """InferenceResult class implementation for segmentation results type"""

    max_colors = 256

    @log_wrap
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "alpha" in kwargs and kwargs["alpha"] == "auto":
            self._alpha = 0.5

        if not isinstance(self._inference_results, list):
            raise DegirumException(
                "Segmentation Postprocessor: inference results data must be a list"
            )
        if len(self._inference_results) != 1:
            raise DegirumException(
                "Segmentation Postprocessor: inference results data must contain one element"
            )
        if not isinstance(self._inference_results[0], dict):
            raise DegirumException(
                "Segmentation Postprocessor: inference results data element must be a dictionary"
            )
        if "data" not in self._inference_results[0]:
            raise DegirumException(
                "Segmentation Postprocessor: inference results data element dictionary must contain 'data' key"
            )
        if not isinstance(self._inference_results[0]["data"], numpy.ndarray):
            raise DegirumException(
                "Segmentation Postprocessor: inference results 'data' value must be numpy.ndarray"
            )

    __init__.__doc__ = InferenceResults.__init__.__doc__

    @staticmethod
    def generate_overlay_color(model_params, label_dict) -> list:
        """Overlay colors generator.

        Returns:
            general overlay color data for segmentation results
        """
        colors = InferenceResults.generate_colors()
        if not label_dict:
            if model_params.OutputNumClasses <= 0:
                raise DegirumException(
                    "Segmentation Postprocessor: either non empty labels dictionary or OutputNumClasses greater than 0 must be specified for Segmentation postprocessor"
                )
            return colors[: model_params.OutputNumClasses]

        else:
            if any(not isinstance(k, int) for k in label_dict.keys()):
                raise DegirumException(
                    "Segmentation Postprocessor: non integer keys in label dictionary are not supported"
                )
            if any(
                k < 0 or k > SegmentationResults.max_colors for k in label_dict.keys()
            ):
                raise DegirumException(
                    f"Segmentation Postprocessor: label key values must be within [0, {SegmentationResults.max_colors}] range"
                )
            colors = colors[: len(label_dict)]
            for k, v in label_dict.items():
                if v == "background":
                    colors.insert(k, (0, 0, 0))  # default non-mask color for background
                    colors.pop(0)
            return colors

    @property
    def image_overlay(self):
        """Image with AI inference results drawn. Image type is defined by the selected graphical backend."""

        draw = create_draw_primitives(
            self._input_image, self._alpha, self._alpha, self._font_scale
        )
        result = (
            numpy.copy(self._inference_results[0]["data"]).squeeze().astype(numpy.uint8)
        )
        lut = numpy.empty((256, 1, 3), dtype=numpy.uint8)
        lut[:, :, :] = (0, 0, 0)  # default non-mask color
        current_color_set = itertools.cycle(
            self._overlay_color
            if isinstance(self._overlay_color, list)
            else [self._overlay_color]
        )
        for i in range(256):
            lut[i, :, :] = next(current_color_set)

        draw.image_segmentation_overlay(self._conversion, result, lut)
        return draw.image_overlay()

    def __str__(self):
        """
        Convert inference results to string
        """
        res = self._inference_results[0]["data"]
        res_list = {
            "segments": ", ".join(
                self._label_dictionary.get(i, str(i)) for i in numpy.unique(res)
            ),
        }
        return yaml.dump(res_list, sort_keys=False)


def _inference_result_type(model_params):
    """Create and return inference result builder function based on model parameters

    Parameters:
    - `model_params`: model parameters

    Returns inference result builder function
    """
    variants = {
        "None": lambda: InferenceResults,
        "Base": lambda: InferenceResults,
        "Classification": lambda: ClassificationResults,
        "MultiLabelClassification": lambda: MultiLabelClassificationResults,
        "Detection": lambda: DetectionResults,
        "DetectionYolo": lambda: DetectionResults,
        "DetectionYoloV8": lambda: DetectionResults,
        "DetectionYoloPlates": lambda: ClassificationResults,
        "FaceDetection": lambda: DetectionResults,
        "PoseDetection": lambda: DetectionResults,
        "PoseDetectionYoloV8": lambda: DetectionResults,
        "HandDetection": lambda: Hand_DetectionResults,
        "Segmentation": lambda: SegmentationResults,
    }

    postprocessor_type = model_params.OutputPostprocessType
    result_processor = variants.get(postprocessor_type, None)
    if result_processor is None:
        raise DegirumException(
            f"Model postprocessor type is not known: {postprocessor_type}"
        )
    return result_processor


@log_wrap
def create_postprocessor(*args, **kwargs) -> InferenceResults:
    """Create and return postprocessor object.

    For the list of arguments see documentation for constructor of [degirum.postprocessor.InferenceResults][] class.

    Returns:
        InferenceResults instance corresponding to model results type.
    """
    return _inference_result_type(kwargs["model_params"])()(*args, **kwargs)


def _create_overlay_color_dataset(model_params, label_dict):
    """Create and return default color data based on postprocessor type.

    Args:
        model_params (ModelParams): Model parameters.
        label_dict (dict[str, str]): Model labels dictionary.

    Returns:
        result (list[tuple] | tuple):
            overlay color data
    """
    return _inference_result_type(model_params)().generate_overlay_color(
        model_params, label_dict
    )
