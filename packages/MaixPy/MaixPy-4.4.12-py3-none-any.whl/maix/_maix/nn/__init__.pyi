"""
maix.nn module
"""
from __future__ import annotations
import maix._maix.err
import maix._maix.image
import maix._maix.tensor
import typing
from . import F
__all__ = ['Classifier', 'F', 'FaceDetector', 'FaceObject', 'FaceRecognizer', 'LayerInfo', 'MUD', 'NN', 'Object', 'ObjectFloat', 'Objects', 'Retinaface', 'SelfLearnClassifier', 'YOLOv5', 'YOLOv8']
class Classifier:
    label_path: str
    labels: list[str]
    mean: list[float]
    scale: list[float]
    def __init__(self, model: str = '', dual_buff: bool = True) -> None:
        ...
    def classify(self, img: maix._maix.image.Image, softmax: bool = True, fit: maix._maix.image.Fit = ...) -> list[tuple[int, float]]:
        """
        Forward image to model, get result. Only for image input, use classify_raw for tensor input.
        
        Args:
          - img: image, format should match model input_type， or will raise err.Exception
          - softmax: if true, will do softmax to result, or will return raw value
          - fit: image resize fit mode, default Fit.FIT_COVER, see image.Fit.
        
        
        Returns: result, a list of (label, score). If in dual_buff mode, value can be one element list and score is zero when not ready. In C++, you need to delete it after use.
        """
    def classify_raw(self, data: maix._maix.tensor.Tensor, softmax: bool = True) -> list[tuple[int, float]]:
        """
        Forward tensor data to model, get result
        
        Args:
          - data: tensor data, format should match model input_type， or will raise err.Excetion
          - softmax: if true, will do softmax to result, or will return raw value
        
        
        Returns: result, a list of (label, score). In C++, you need to delete it after use.
        """
    def input_format(self) -> maix._maix.image.Format:
        """
        Get input image format, only for image input
        
        Returns: input image format, image::Format type.
        """
    def input_height(self) -> int:
        """
        Get model input height, only for image input
        
        Returns: model input size of height
        """
    def input_shape(self) -> list[int]:
        """
        Get input shape, if have multiple input, only return first input shape
        
        Returns: input shape, list type
        """
    def input_size(self) -> maix._maix.image.Size:
        """
        Get model input size, only for image input
        
        Returns: model input size
        """
    def input_width(self) -> int:
        """
        Get model input width, only for image input
        
        Returns: model input size of width
        """
    def load(self, model: str) -> maix._maix.err.Err:
        """
        Load model from file, model format is .mud,
        MUD file should contain [extra] section, have key-values:
        - model_type: classifier
        - input_type: rgb or bgr
        - mean: 123.675, 116.28, 103.53
        - scale: 0.017124753831663668, 0.01750700280112045, 0.017429193899782137
        - labels: imagenet_classes.txt
        
        Args:
          - model: MUD model path
        
        
        Returns: error code, if load failed, return error code
        """
class FaceDetector:
    mean: list[float]
    scale: list[float]
    def __init__(self, model: str = '', dual_buff: bool = True) -> None:
        ...
    def detect(self, img: maix._maix.image.Image, conf_th: float = 0.5, iou_th: float = 0.45, fit: maix._maix.image.Fit = ...) -> list[Object]:
        """
        Detect objects from image
        
        Args:
          - img: Image want to detect, if image's size not match model input's, will auto resize with fit method.
          - conf_th: Confidence threshold, default 0.5.
          - iou_th: IoU threshold, default 0.45.
          - fit: Resize method, default image.Fit.FIT_CONTAIN.
        
        
        Returns: Object list. In C++, you should delete it after use.
        """
    def input_format(self) -> maix._maix.image.Format:
        """
        Get input image format
        
        Returns: input image format, image::Format type.
        """
    def input_height(self) -> int:
        """
        Get model input height
        
        Returns: model input size of height
        """
    def input_size(self) -> maix._maix.image.Size:
        """
        Get model input size
        
        Returns: model input size
        """
    def input_width(self) -> int:
        """
        Get model input width
        
        Returns: model input size of width
        """
    def load(self, model: str) -> maix._maix.err.Err:
        """
        Load model from file
        
        Args:
          - model: Model path want to load
        
        
        Returns: err::Err
        """
class FaceObject:
    class_id: int
    face: maix._maix.image.Image
    feature: list[float]
    h: int
    points: list[int]
    score: float
    w: int
    x: int
    y: int
    def __init__(self, x: int = 0, y: int = 0, w: int = 0, h: int = 0, class_id: int = 0, score: float = 0, points: list[int] = [], feature: list[float] = [], face: maix._maix.image.Image = ...) -> None:
        ...
    def __str__(self) -> str:
        """
        FaceObject info to string
        
        Returns: FaceObject info string
        """
class FaceRecognizer:
    features: list[list[float]]
    labels: list[str]
    mean_detector: list[float]
    mean_feature: list[float]
    scale_detector: list[float]
    scale_feature: list[float]
    def __init__(self, detect_model: str = '', feature_model: str = '', dual_buff: bool = True) -> None:
        ...
    def add_face(self, face: FaceObject, label: str) -> maix._maix.err.Err:
        """
        Add face to lib
        
        Args:
          - face: face object, find by recognize
          - label: face label(name)
        """
    def input_format(self) -> maix._maix.image.Format:
        """
        Get input image format
        
        Returns: input image format, image::Format type.
        """
    def input_height(self) -> int:
        """
        Get model input height
        
        Returns: model input size of height
        """
    def input_size(self) -> maix._maix.image.Size:
        """
        Get model input size
        
        Returns: model input size
        """
    def input_width(self) -> int:
        """
        Get model input width
        
        Returns: model input size of width
        """
    def load(self, detect_model: str, feature_model: str) -> maix._maix.err.Err:
        """
        Load model from file
        
        Args:
          - detect_model: face detect model path, default empty, you can load model later by load function.
          - feature_model: feature extract model
        
        
        Returns: err::Err
        """
    def load_faces(self, path: str) -> maix._maix.err.Err:
        """
        Load faces info from a file
        
        Args:
          - path: from where to load, string type.
        
        
        Returns: err::Err type
        """
    def recognize(self, img: maix._maix.image.Image, conf_th: float = 0.5, iou_th: float = 0.45, compare_th: float = 0.8, get_feature: bool = False, get_face: bool = False, fit: maix._maix.image.Fit = ...) -> list[FaceObject]:
        """
        Detect objects from image
        
        Args:
          - img: Image want to detect, if image's size not match model input's, will auto resize with fit method.
          - conf_th: Detect confidence threshold, default 0.5.
          - iou_th: Detect IoU threshold, default 0.45.
          - compare_th: Compare two face score threshold, default 0.8, if two faces' score < this value, will see this face fas unknown.
          - get_feature: return feature or not, if true will copy features to result, if false will not copy feature to result to save time and memory.
          - get_face: return face image or not, if true result object's face attribute will valid, or face sttribute is empty. Get face image will alloc memory and copy image, so will lead to slower speed.
          - fit: Resize method, default image.Fit.FIT_CONTAIN.
        
        
        Returns: FaceObject list. In C++, you should delete it after use.
        """
    def remove_face(self, idx: int = -1, label: str = '') -> maix._maix.err.Err:
        """
        remove face from lib
        
        Args:
          - idx: index of face in lib, default -1 means use label, idx and label must have one, idx have high priotiry.
          - label: which face to remove, default to empty string mean use idx, idx and label must have one, idx have high priotiry.
        """
    def save_faces(self, path: str) -> maix._maix.err.Err:
        """
        Save faces info to a file
        
        Args:
          - path: where to save, string type.
        
        
        Returns: err.Err type
        """
class LayerInfo:
    dtype: maix._maix.tensor.DType
    name: str
    shape: list[int]
    def __init__(self, name: str = '', dtype: maix._maix.tensor.DType = ..., shape: list[int] = []) -> None:
        ...
    def __str__(self) -> str:
        """
        To string
        """
    def shape_int(self) -> int:
        """
        Shape as one int type, multiply all dims of shape
        """
    def to_str(self) -> str:
        """
        To string
        """
class MUD:
    items: dict[str, dict[str, str]]
    type: str
    def __init__(self, model_path: str = None) -> None:
        ...
    def load(self, model_path: str) -> maix._maix.err.Err:
        """
        Load model from file
        
        Args:
          - model_path: direction [in], model file path, model format can be MUD(model universal describe file) file.
        
        
        Returns: error code, if load success, return err::ERR_NONE
        """
class NN:
    def __init__(self, model: str = '', dual_buff: bool = True) -> None:
        ...
    def extra_info(self) -> dict[str, str]:
        """
        Get model extra info define in MUD file
        
        Returns: extra info, dict type, key-value object, attention: key and value are all string type.
        """
    def forward(self, inputs: maix._maix.tensor.Tensors, copy_result: bool = True, dual_buff_wait: bool = False) -> maix._maix.tensor.Tensors:
        """
        forward run model, get output of model,
        this is specially for MaixPy, not efficient, but easy to use in MaixPy
        
        Args:
          - input: direction [in], input tensor
          - copy_result: If set true, will copy result to a new variable; else will use a internal memory, you can only use it until to the next forward.
        Default true to avoid problems, you can set it to false manually to make speed faster.
          - dual_buff_wait: bool type, only for dual_buff mode, if true, will inference this image and wait for result, default false.
        
        
        Returns: output tensor. In C++, you should manually delete tensors in return value and return value.
        If dual_buff mode, it can be NULL(None in MaixPy) means not ready.
        """
    def forward_image(self, img: maix._maix.image.Image, mean: list[float] = [], scale: list[float] = [], fit: maix._maix.image.Fit = ..., copy_result: bool = True, dual_buff_wait: bool = False) -> maix._maix.tensor.Tensors:
        """
        forward model, param is image
        
        Args:
          - img: input image
          - mean: mean value, a list type, e.g. [0.485, 0.456, 0.406], default is empty list means not normalize.
          - scale: scale value, a list type, e.g. [1/0.229, 1/0.224, 1/0.225], default is empty list means not normalize.
          - fit: fit mode, if the image size of input not equal to model's input, it will auto resize use this fit method,
        default is image.Fit.FIT_FILL for easy coordinate calculation, but for more accurate result, use image.Fit.FIT_CONTAIN is better.
          - copy_result: If set true, will copy result to a new variable; else will use a internal memory, you can only use it until to the next forward.
        Default true to avoid problems, you can set it to false manually to make speed faster.
          - dual_buff_wait: bool type, only for dual_buff mode, if true, will inference this image and wait for result, default false.
        
        
        Returns: output tensor. In C++, you should manually delete tensors in return value and return value.
        If dual_buff mode, it can be NULL(None in MaixPy) means not ready.
        """
    def inputs_info(self) -> list[LayerInfo]:
        """
        Get model input layer info
        
        Returns: input layer info
        """
    def load(self, model: str) -> maix._maix.err.Err:
        """
        Load model from file
        
        Args:
          - model: direction [in], model file path, model format can be MUD(model universal describe file) file.
        
        
        Returns: error code, if load success, return err::ERR_NONE
        """
    def loaded(self) -> bool:
        """
        Is model loaded
        
        Returns: true if model loaded, else false
        """
    def outputs_info(self) -> list[LayerInfo]:
        """
        Get model output layer info
        
        Returns: output layer info
        """
    def set_dual_buff(self, enable: bool) -> None:
        """
        Enable dual buff or disable dual buff
        
        Args:
          - enable: true to enable, false to disable
        """
class Object:
    class_id: int
    h: int
    points: list[int]
    score: float
    seg_mask: maix._maix.image.Image
    w: int
    x: int
    y: int
    def __init__(self, x: int = 0, y: int = 0, w: int = 0, h: int = 0, class_id: int = 0, score: float = 0, points: list[int] = []) -> None:
        ...
    def __str__(self) -> str:
        """
        Object info to string
        
        Returns: Object info string
        """
class ObjectFloat:
    class_id: float
    h: float
    points: list[float]
    score: float
    w: float
    x: float
    y: float
    def __init__(self, x: float = 0, y: float = 0, w: float = 0, h: float = 0, class_id: float = 0, score: float = 0, points: list[float] = []) -> None:
        ...
    def __str__(self) -> str:
        """
        Object info to string
        
        Returns: Object info string
        """
class Objects:
    def __init__(self) -> None:
        ...
    def __item__(self, idx: int) -> Object:
        """
        Get object item
        """
    def __iter__(self) -> typing.Iterator:
        ...
    def __len__(self) -> int:
        """
        Get size
        """
    def add(self, x: int = 0, y: int = 0, w: int = 0, h: int = 0, class_id: int = 0, score: float = 0, points: list[int] = []) -> Object:
        """
        Add object to objects
        """
    def at(self, idx: int) -> Object:
        """
        Get object item
        """
    def remove(self, idx: int) -> maix._maix.err.Err:
        """
        Remove object form objects
        """
class Retinaface:
    mean: list[float]
    scale: list[float]
    def __init__(self, model: str = '', dual_buff: bool = True) -> None:
        ...
    def detect(self, img: maix._maix.image.Image, conf_th: float = 0.4, iou_th: float = 0.45, fit: maix._maix.image.Fit = ...) -> list[Object]:
        """
        Detect objects from image
        
        Args:
          - img: Image want to detect, if image's size not match model input's, will auto resize with fit method.
          - conf_th: Confidence threshold, default 0.4.
          - iou_th: IoU threshold, default 0.45.
          - fit: Resize method, default image.Fit.FIT_CONTAIN.
        
        
        Returns: Object list. In C++, you should delete it after use.
        """
    def input_format(self) -> maix._maix.image.Format:
        """
        Get input image format
        
        Returns: input image format, image::Format type.
        """
    def input_height(self) -> int:
        """
        Get model input height
        
        Returns: model input size of height
        """
    def input_size(self) -> maix._maix.image.Size:
        """
        Get model input size
        
        Returns: model input size
        """
    def input_width(self) -> int:
        """
        Get model input width
        
        Returns: model input size of width
        """
    def load(self, model: str) -> maix._maix.err.Err:
        """
        Load model from file
        
        Args:
          - model: Model path want to load
        
        
        Returns: err::Err
        """
class SelfLearnClassifier:
    label_path: str
    labels: list[str]
    mean: list[float]
    scale: list[float]
    def __init__(self, model: str = '', dual_buff: bool = True) -> None:
        ...
    def add_class(self, img: maix._maix.image.Image, fit: maix._maix.image.Fit = ...) -> None:
        """
        Add a class to recognize
        
        Args:
          - img: Add a image as a new class
          - fit: image resize fit mode, default Fit.FIT_COVER, see image.Fit.
        """
    def add_sample(self, img: maix._maix.image.Image, fit: maix._maix.image.Fit = ...) -> None:
        """
        Add sample, you should call learn method after add some samples to learn classes.
        Sample image can be any of classes we already added.
        
        Args:
          - img: Add a image as a new sample.
        """
    def class_num(self) -> int:
        """
        Get class number
        """
    def classify(self, img: maix._maix.image.Image, fit: maix._maix.image.Fit = ...) -> list[tuple[int, float]]:
        """
        Classify image
        
        Args:
          - img: image, format should match model input_type， or will raise err.Exception
          - fit: image resize fit mode, default Fit.FIT_COVER, see image.Fit.
        
        
        Returns: result, a list of (idx, distance), smaller distance means more similar. In C++, you need to delete it after use.
        """
    def clear(self) -> None:
        """
        Clear all class and samples
        """
    def input_format(self) -> maix._maix.image.Format:
        """
        Get input image format, only for image input
        
        Returns: input image format, image::Format type.
        """
    def input_height(self) -> int:
        """
        Get model input height, only for image input
        
        Returns: model input size of height
        """
    def input_shape(self) -> list[int]:
        """
        Get input shape, if have multiple input, only return first input shape
        
        Returns: input shape, list type
        """
    def input_size(self) -> maix._maix.image.Size:
        """
        Get model input size, only for image input
        
        Returns: model input size
        """
    def input_width(self) -> int:
        """
        Get model input width, only for image input
        
        Returns: model input size of width
        """
    def learn(self) -> int:
        """
        Start auto learn class features from classes image and samples.
        You should call this method after you add some samples.
        
        Returns: learn epoch(times), 0 means learn nothing.
        """
    def load(self, path: str) -> list[str]:
        """
        Load features info from binary file
        
        Args:
          - path: feature info binary file path, e.g. /root/my_classes.bin
        """
    def load_model(self, model: str) -> maix._maix.err.Err:
        """
        Load model from file, model format is .mud,
        MUD file should contain [extra] section, have key-values:
        - model_type: classifier_no_top
        - input_type: rgb or bgr
        - mean: 123.675, 116.28, 103.53
        - scale: 0.017124753831663668, 0.01750700280112045, 0.017429193899782137
        
        Args:
          - model: MUD model path
        
        
        Returns: error code, if load failed, return error code
        """
    def rm_class(self, idx: int) -> maix._maix.err.Err:
        """
        Remove a class
        
        Args:
          - idx: index, value from 0 to class_num();
        """
    def rm_sample(self, idx: int) -> maix._maix.err.Err:
        """
        Remove a sample
        
        Args:
          - idx: index, value from 0 to sample_num();
        """
    def sample_num(self) -> int:
        """
        Get sample number
        """
    def save(self, path: str, labels: list[str] = []) -> maix._maix.err.Err:
        """
        Save features and labels to a binary file
        
        Args:
          - path: file path to save, e.g. /root/my_classes.bin
          - labels: class labels, can be None, or length must equal to class num, or will return err::Err
        
        
        Returns: maix.err.Err if labels exists but length not equal to class num, or save file failed, or class num is 0.
        """
class YOLOv5:
    anchors: list[float]
    label_path: str
    labels: list[str]
    mean: list[float]
    scale: list[float]
    def __init__(self, model: str = '', dual_buff: bool = True) -> None:
        ...
    def detect(self, img: maix._maix.image.Image, conf_th: float = 0.5, iou_th: float = 0.45, fit: maix._maix.image.Fit = ...) -> list[Object]:
        """
        Detect objects from image
        
        Args:
          - img: Image want to detect, if image's size not match model input's, will auto resize with fit method.
          - conf_th: Confidence threshold, default 0.5.
          - iou_th: IoU threshold, default 0.45.
          - fit: Resize method, default image.Fit.FIT_CONTAIN.
        
        
        Returns: Object list. In C++, you should delete it after use.
        """
    def input_format(self) -> maix._maix.image.Format:
        """
        Get input image format
        
        Returns: input image format, image::Format type.
        """
    def input_height(self) -> int:
        """
        Get model input height
        
        Returns: model input size of height
        """
    def input_size(self) -> maix._maix.image.Size:
        """
        Get model input size
        
        Returns: model input size
        """
    def input_width(self) -> int:
        """
        Get model input width
        
        Returns: model input size of width
        """
    def load(self, model: str) -> maix._maix.err.Err:
        """
        Load model from file
        
        Args:
          - model: Model path want to load
        
        
        Returns: err::Err
        """
class YOLOv8:
    label_path: str
    labels: list[str]
    mean: list[float]
    scale: list[float]
    def __init__(self, model: str = '', dual_buff: bool = True) -> None:
        ...
    def detect(self, img: maix._maix.image.Image, conf_th: float = 0.5, iou_th: float = 0.45, fit: maix._maix.image.Fit = ..., keypoint_th: float = 0.5) -> Objects:
        """
        Detect objects from image
        
        Args:
          - img: Image want to detect, if image's size not match model input's, will auto resize with fit method.
          - conf_th: Confidence threshold, default 0.5.
          - iou_th: IoU threshold, default 0.45.
          - fit: Resize method, default image.Fit.FIT_CONTAIN.
          - keypoint_th: keypoint threshold, default 0.5, only for yolov8-pose model.
        
        
        Returns: Object list. In C++, you should delete it after use.
        If model is yolov8-pose, object's points have value, and if points' value < 0 means that point is invalid(conf < keypoint_th).
        """
    def draw_pose(self, img: maix._maix.image.Image, points: list[int], radius: int = 4, color: maix._maix.image.Color = ..., body: bool = True) -> None:
        """
        Draw pose keypoints on image
        
        Args:
          - img: image object, maix.image.Image type.
          - points: keypoits, int list type, [x, y, x, y ...]
          - radius: radius of points.
          - color: color of points.
          - body: true, if points' length is 17*2 and body is ture, will draw lines as human body, if set to false won't draw lines, default true.
        """
    def draw_seg_mask(self, img: maix._maix.image.Image, x: int, y: int, seg_mask: maix._maix.image.Image, threshold: int = 127) -> None:
        """
        Draw segmentation on image
        
        Args:
          - img: image object, maix.image.Image type.
          - seg_mask: segmentation mask image by detect method, a grayscale image
          - threshold: only mask's value > threshold will be draw on image, value from 0 to 255.
        """
    def input_format(self) -> maix._maix.image.Format:
        """
        Get input image format
        
        Returns: input image format, image::Format type.
        """
    def input_height(self) -> int:
        """
        Get model input height
        
        Returns: model input size of height
        """
    def input_size(self) -> maix._maix.image.Size:
        """
        Get model input size
        
        Returns: model input size
        """
    def input_width(self) -> int:
        """
        Get model input width
        
        Returns: model input size of width
        """
    def load(self, model: str) -> maix._maix.err.Err:
        """
        Load model from file
        
        Args:
          - model: Model path want to load
        
        
        Returns: err::Err
        """
