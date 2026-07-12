# Algorithm

This page explains the algorithm tracks from simple ideas to implementation details. Each method explains what it is, why the project needs it, how it is used here, what its inputs and outputs are, and how to judge whether the result is normal.

## Defect detection

Defect detection answers two questions: where the defect is, and which class it belongs to.

The input is a photovoltaic cell image. The output is a list of detection boxes. Each box contains coordinates, a class, and a confidence score. For example, the model may output a crack box with class `crack` and confidence `0.91`.

The project uses YOLO-style detectors through Ultralytics. YOLO divides the image into many candidate regions and predicts box position and class in one forward pass. It is fast, which makes it useful for ONNX and TensorRT deployment comparisons.

A detection result should not be judged by one visualization. The main metrics are:

- mAP50: average precision when a predicted box overlaps a ground truth box by at least 0.5 IoU.
- mAP50-95: average precision across multiple IoU thresholds, which is stricter than mAP50.
- Recall: the fraction of real defects found by the model.
- Per-class AP: detection quality for each defect class.

Recall matters in photovoltaic defect detection. A missed defect may continue into the next production step. A false positive has a cost too, but it can usually be reviewed.

## Defect classification

Defect classification answers whether the whole image is abnormal, or how severe the defect is.

The input is an image of one cell. The output can be a class or a score. For ELPV, the model can output `normal` or `defect`, or it can output a defect probability close to `0.66`.

A classification model usually has a feature extractor and a classification head. The feature extractor turns the image into a vector. The head turns the vector into class probabilities. The project includes ResNet-18 and Swin-T baselines for ELPV because they provide two image-level references: a convolutional model and a transformer model.

A classification result should be checked with a confusion matrix, F1, AUC, and recall for each severity level. If a model performs well on normal samples but misses mild defects, it is not a good screening model.

## Anomaly detection

Anomaly detection asks whether an image contains regions that do not look like normal samples.

It differs from supervised detection. Supervised detection needs labeled boxes for a defect class before it can learn that class. Anomaly detection mainly learns the texture distribution of normal samples. If a region deviates from that distribution, the model can assign a higher anomaly score.

PatchCore is the intended anomaly-detection baseline for the normal-sample track. PatchCore stores local features from normal images. During inference, it compares local features from a test image with the normal feature memory. If a local feature is far from the normal memory, that region is more likely to be abnormal.

The input is a normal training set and a test image. The output is an image-level anomaly score and a pixel or region heatmap. A normal result should satisfy two conditions: normal samples receive low anomaly scores, and clearly defective samples receive high scores.

Anomaly detection is useful for new defects and extremely rare defects. It does not fully replace a detector because it usually does not output fine-grained classes, but it can work as a screening module that sends suspicious samples to a person or a later model.

## Preprocessing

Preprocessing transforms an image before it enters the model. The goal is not to make the image look nicer. The goal is to make defects easier for the model to see.

EL images often have uneven brightness, silicon texture interference, busbar interference, and low-contrast microcracks. Preprocessing candidates include CLAHE, gamma correction, and simple filtering.

CLAHE means contrast limited adaptive histogram equalization. It increases local contrast while limiting noise amplification. The input is a grayscale image, and the output is an enhanced grayscale image.

Preprocessing should not be accepted by visual inspection alone. The same model should be compared on the same test set, especially on recall for cracks, scratches, and finger interruptions. If recall does not improve, or false positives increase sharply, that preprocessing step should not be enabled by default.

## Deployment optimization

Training models usually run in PyTorch. Deployment cares more about latency, throughput, and resource use.

ONNX is a model exchange format. It exports a PyTorch model into a more portable computation graph that can be executed by ONNX Runtime or TensorRT. The input is trained weights and an input size. The output is an `.onnx` file.

TensorRT is NVIDIA's inference optimizer. It can optimize the graph for a specific GPU and input shape, and it can use FP16 or INT8 to reduce compute cost. The input is an ONNX model. The output is an `.engine` file.

A deployment result should be judged by accuracy and speed together. PyTorch, ONNX Runtime, and TensorRT should be compared on the same test set, input size, and hardware. Speed only matters if output differences do not meaningfully hurt mAP or recall.
