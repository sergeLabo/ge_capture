

import tensorflow as tf



class Movenet:
    """La reconnaissance de squelette"""

    def __init__(self, current_dir):
        """Model performant, simple pose mais lourd
        TF Lite --> pas de CUDA
        """
        model_path = current_dir + "/lite-model_movenet_singlepose_thunder_3.tflite"
        print("movenet model path:", model_path)
        self.interpreter = tf.lite.Interpreter(model_path)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        self.movenet_keypoints = None

    def skeleton_detection(self, frame, threshold):
        if frame is not None:
            image = tf.expand_dims(frame, axis=0)
            # Resize and pad the image to keep the aspect ratio and fit the expected size.
            image = tf.image.resize_with_pad(image, 256, 256)
            input_image = tf.cast(image, dtype=tf.float32)
            self.interpreter.set_tensor(self.input_details[0]['index'], input_image.numpy())
            self.interpreter.invoke()
            # Output is a [1, 1, 17, 3] numpy array.
            self.movenet_keypoints_with_scores = self.interpreter.get_tensor(self.output_details[0]['index'])
            # Construction de ma liste de 17 keypoints = self.movenet_keypoints
            self.get_movenet_keypoints(threshold)

    def get_movenet_keypoints(self, threshold):
        """keypoints_with_scores = TODO à retrouver
        keypoints = [None, [200, 300], None, [100, 700], ...] = 17 items
        """
        keypoints = []
        for item in self.movenet_keypoints_with_scores[0][0]:
            if item[2] > threshold:
                x = int(item[1]*256)
                y = int((item[0]*256))
                keypoints.append([x, y])

            else:
                keypoints.append(None)
        self.movenet_keypoints = keypoints

    def movenet_close(self):
        print("Fermeture de Movenet")
        del self.interpreter
