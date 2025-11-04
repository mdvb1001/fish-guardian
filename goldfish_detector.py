#!/usr/bin/env python3
"""
Goldfish Detector Module
Uses YOLOv8 EdgeTPU model to detect goldfish in aquarium images
"""

import numpy as np
import tflite_runtime.interpreter as tflite
from PIL import Image
from typing import List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class GoldfishDetector:
    """
    Goldfish detection using YOLOv8 INT8 EdgeTPU model

    Features:
    - Coral EdgeTPU acceleration (11.9 FPS)
    - INT8 quantized model for maximum performance
    - Confidence-based filtering
    - Bounding box extraction
    """

    def __init__(
        self,
        model_path: str = 'models/goldfish_best_edgetpu_int8.tflite',
        conf_threshold: float = 0.5,
        use_edgetpu: bool = True
    ):
        """
        Initialize goldfish detector

        Args:
            model_path: Path to TFLite model file
            conf_threshold: Minimum confidence for detections (0-1)
            use_edgetpu: Use Coral EdgeTPU acceleration if available
        """
        self.model_path = model_path
        self.conf_threshold = conf_threshold
        self.use_edgetpu = use_edgetpu

        # Load model
        logger.info(f"Loading model: {model_path}")
        self._load_model()

        # Get model details
        self.input_details = self.interpreter.get_input_details()[0]
        self.output_details = self.interpreter.get_output_details()

        # Extract input shape
        self.input_shape = self.input_details['shape']
        self.input_height = self.input_shape[1]
        self.input_width = self.input_shape[2]
        self.input_dtype = self.input_details['dtype']

        # Get output quantization parameters
        self.output_dtype = self.output_details[0]['dtype']
        self.output_scale = self.output_details[0].get('quantization_parameters', {}).get('scales', [1.0])[0]
        self.output_zero_point = self.output_details[0].get('quantization_parameters', {}).get('zero_points', [0])[0]

        logger.info(f"Model loaded successfully")
        logger.info(f"  Input: {self.input_width}x{self.input_height}, dtype={self.input_dtype}")
        logger.info(f"  Output: dtype={self.output_dtype}, scale={self.output_scale}, zero_point={self.output_zero_point}")
        logger.info(f"  Acceleration: {'EdgeTPU' if self.using_edgetpu else 'CPU'}")
        logger.info(f"  Confidence threshold: {self.conf_threshold}")

    def _load_model(self):
        """Load TFLite model with optional EdgeTPU delegation"""
        try:
            if self.use_edgetpu:
                # Try loading with EdgeTPU delegate
                self.interpreter = tflite.Interpreter(
                    model_path=self.model_path,
                    experimental_delegates=[
                        tflite.load_delegate('libedgetpu.so.1')
                    ]
                )
                self.using_edgetpu = True
                logger.info("EdgeTPU delegate loaded successfully")
            else:
                raise Exception("EdgeTPU disabled by user")

        except Exception as e:
            # Fall back to CPU
            logger.warning(f"EdgeTPU delegate failed: {e}")
            logger.warning("Falling back to CPU mode")
            self.interpreter = tflite.Interpreter(model_path=self.model_path)
            self.using_edgetpu = False

        self.interpreter.allocate_tensors()

    def preprocess_image(self, image: Image.Image) -> np.ndarray:
        """
        Preprocess PIL image for INT8 model input

        Args:
            image: PIL Image

        Returns:
            Preprocessed numpy array ready for model input
        """
        # Resize to model input size
        image_resized = image.resize(
            (self.input_width, self.input_height),
            Image.LANCZOS
        )

        # Convert to numpy array
        if self.input_dtype == np.int8:
            # INT8 model: convert (0-255) → (-128 to 127)
            input_data = np.array(image_resized, dtype=np.uint8).astype(np.float32)
            input_data = (input_data - 128).astype(np.int8)
        elif self.input_dtype == np.uint8:
            # UINT8 model: keep as (0-255)
            input_data = np.array(image_resized, dtype=np.uint8)
        else:  # np.float32
            # FLOAT32 model: normalize to (0-1)
            input_data = np.array(image_resized, dtype=np.float32) / 255.0

        # Add batch dimension
        input_data = np.expand_dims(input_data, axis=0)

        return input_data

    def detect(self, image: Image.Image, nms_threshold: float = 0.45) -> List[dict]:
        """
        Detect goldfish in image

        Args:
            image: PIL Image
            nms_threshold: IoU threshold for Non-Maximum Suppression (default: 0.45)

        Returns:
            List of detections after NMS, each dict contains:
                - bbox: (x, y, w, h) in pixel coordinates
                - confidence: detection confidence (0-1)
        """
        # Get original image dimensions
        img_width, img_height = image.size

        # Preprocess
        input_data = self.preprocess_image(image)

        # Run inference
        self.interpreter.set_tensor(self.input_details['index'], input_data)
        self.interpreter.invoke()

        # Get output
        output = self.interpreter.get_tensor(self.output_details[0]['index'])

        # Dequantize if INT8 model
        if self.output_dtype in [np.int8, np.uint8]:
            output = (output.astype(np.float32) - self.output_zero_point) * self.output_scale

        # Parse YOLOv8 output: shape (1, 5, N) where 5 = [x, y, w, h, conf]
        detections = []

        if len(output.shape) == 3 and output.shape[1] == 5:
            # Extract confidences
            confidences = output[0, 4, :]

            # Find high-confidence detections
            high_conf_indices = np.where(confidences > self.conf_threshold)[0]

            # Collect detections with scaled coordinates
            boxes = []
            scores = []

            for idx in high_conf_indices:
                # Get normalized coordinates (0-1 range)
                x_center_norm = output[0, 0, idx]
                y_center_norm = output[0, 1, idx]
                w_norm = output[0, 2, idx]
                h_norm = output[0, 3, idx]
                conf = confidences[idx]

                # Scale to image dimensions
                x_center = x_center_norm * img_width
                y_center = y_center_norm * img_height
                w = w_norm * img_width
                h = h_norm * img_height

                # Convert center format to corner format for NMS
                x1 = x_center - w / 2
                y1 = y_center - h / 2
                x2 = x_center + w / 2
                y2 = y_center + h / 2

                boxes.append([x1, y1, x2, y2])
                scores.append(conf)

            # Apply Non-Maximum Suppression
            if len(boxes) > 0:
                boxes = np.array(boxes)
                scores = np.array(scores)
                keep_indices = self._nms(boxes, scores, nms_threshold)

                for idx in keep_indices:
                    x1, y1, x2, y2 = boxes[idx]
                    # Convert back to center format (x, y, w, h)
                    x_center = (x1 + x2) / 2
                    y_center = (y1 + y2) / 2
                    w = x2 - x1
                    h = y2 - y1

                    detections.append({
                        'bbox': (float(x_center), float(y_center), float(w), float(h)),
                        'confidence': float(scores[idx])
                    })

        return detections

    def _nms(self, boxes: np.ndarray, scores: np.ndarray, threshold: float) -> List[int]:
        """
        Non-Maximum Suppression to remove duplicate detections

        Args:
            boxes: Array of shape (N, 4) with format [x1, y1, x2, y2]
            scores: Array of shape (N,) with confidence scores
            threshold: IoU threshold for considering boxes as duplicates

        Returns:
            List of indices to keep
        """
        if len(boxes) == 0:
            return []

        # Sort by confidence score (descending)
        order = scores.argsort()[::-1]

        keep = []
        while len(order) > 0:
            # Pick the box with highest confidence
            i = order[0]
            keep.append(i)

            # Calculate IoU with remaining boxes
            xx1 = np.maximum(boxes[i, 0], boxes[order[1:], 0])
            yy1 = np.maximum(boxes[i, 1], boxes[order[1:], 1])
            xx2 = np.minimum(boxes[i, 2], boxes[order[1:], 2])
            yy2 = np.minimum(boxes[i, 3], boxes[order[1:], 3])

            w = np.maximum(0.0, xx2 - xx1)
            h = np.maximum(0.0, yy2 - yy1)
            intersection = w * h

            box_area = (boxes[i, 2] - boxes[i, 0]) * (boxes[i, 3] - boxes[i, 1])
            other_areas = (boxes[order[1:], 2] - boxes[order[1:], 0]) * (boxes[order[1:], 3] - boxes[order[1:], 1])
            union = box_area + other_areas - intersection

            iou = intersection / (union + 1e-6)

            # Keep boxes with IoU below threshold
            inds = np.where(iou <= threshold)[0]
            order = order[inds + 1]

        return keep

    def detect_count(self, image: Image.Image) -> int:
        """
        Quick detection - just return count of goldfish

        Args:
            image: PIL Image

        Returns:
            Number of goldfish detected
        """
        detections = self.detect(image)
        return len(detections)

    def detect_with_boxes(
        self,
        image: Image.Image
    ) -> Tuple[int, List[Tuple[int, int, int, int]]]:
        """
        Detect goldfish and return count + bounding boxes

        Args:
            image: PIL Image

        Returns:
            Tuple of (count, list of (x, y, w, h) boxes)
        """
        detections = self.detect(image)
        boxes = [det['bbox'] for det in detections]
        return len(detections), boxes


# Convenience function for single-use detection
def detect_goldfish(
    image: Image.Image,
    model_path: str = 'models/goldfish_best_edgetpu_int8.tflite',
    conf_threshold: float = 0.5
) -> int:
    """
    One-off goldfish detection

    Args:
        image: PIL Image
        model_path: Path to model file
        conf_threshold: Minimum confidence threshold

    Returns:
        Number of goldfish detected
    """
    detector = GoldfishDetector(model_path, conf_threshold)
    return detector.detect_count(image)


if __name__ == "__main__":
    # Test the detector
    import subprocess
    import os
    import time

    print("=" * 70)
    print("GOLDFISH DETECTOR TEST")
    print("=" * 70)

    # Capture test image
    print("\n📸 Capturing test image...")
    test_image_path = 'test_detector.jpg'
    subprocess.run([
        'rpicam-still', '-o', test_image_path,
        '--width', '640', '--height', '640',
        '--timeout', '1', '-n'
    ], check=True, capture_output=True, timeout=10)
    print(f"✅ Image captured: {test_image_path}")

    # Load image
    image = Image.open(test_image_path)

    # Test detector
    print("\n🔧 Initializing detector...")
    detector = GoldfishDetector(
        model_path='models/goldfish_best_edgetpu_int8.tflite',
        conf_threshold=0.3  # Lower threshold for testing
    )

    # Single detection
    print("\n⚡ Running detection...")
    detections = detector.detect(image)

    print(f"\n📊 Results:")
    print(f"   Goldfish detected: {len(detections)}")

    if detections:
        print(f"\n   Detections:")
        for i, det in enumerate(detections, 1):
            x, y, w, h = det['bbox']
            conf = det['confidence']
            print(f"   {i}. Confidence: {conf:.3f}, BBox: ({x:.1f}, {y:.1f}, {w:.1f}, {h:.1f})")
    else:
        print("\n   No goldfish detected. Try:")
        print("   - Lowering conf_threshold")
        print("   - Ensuring goldfish are visible in frame")
        print("   - Checking camera view of tank")

    # Benchmark
    print("\n⏱️  Benchmarking performance...")
    num_runs = 20
    start = time.time()
    for _ in range(num_runs):
        detector.detect(image)
    elapsed = time.time() - start

    avg_time_ms = (elapsed / num_runs) * 1000
    fps = num_runs / elapsed

    print(f"   Average time: {avg_time_ms:.1f}ms per image")
    print(f"   FPS: {fps:.1f}")

    if fps >= 10:
        print(f"   ✅ EXCELLENT! Fast enough for real-time monitoring")
    elif fps >= 5:
        print(f"   ✅ GOOD! Suitable for monitoring")
    else:
        print(f"   ⚠️  SLOW: Check EdgeTPU is being used")

    # Cleanup
    os.remove(test_image_path)

    print("\n" + "=" * 70)
    print("✅ Test complete!")
    print("=" * 70)
