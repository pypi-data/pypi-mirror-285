import tensorflow as tf
from tqdm import tqdm


class ModelTrainer:
    """
    Responsible for training the model. Scope becomes an issues when dealing with @tf.function.
    It's easier to place all of the training code into an object so we don't run into issues.
    Once the object is created, the __call__ method will train and return the results and the
    trained model.
    """

    def __init__(self, model, epochs, batch_size, train_dataset, train_dataset_size, val_dataset, val_dataset_size,
                 model_out, lr=1e-3):
        """
        Set up the necessary variables that will be used during training, including the model, optimizer,
        encoder, and other metrics.

        :param model: The ARU-Net segmentation model to be trained
        :param epochs: The number of epochs to train the model
        :param batch_size: How many images will be included in a mini-batch
        :param train_dataset:
        :param train_dataset_size: The size of the train dataset
        :param val_dataset:
        :param val_dataset_size: The size of the val dataset
        :param lr: The learning rate
        :param model_out: The path to the weights if we are starting from a pre-trained model
        """
        self.model = model
        self.epochs = epochs
        self.batch_size = batch_size
        self.train_dataset = train_dataset
        self.train_dataset_size = train_dataset_size
        self.val_dataset = val_dataset
        self.val_dataset_size = val_dataset_size
        self.model_out = model_out

        self.optimizer = tf.keras.optimizers.RMSprop(learning_rate=lr)
        self.objective = tf.keras.losses.SparseCategoricalCrossentropy()

        self.train_loss = tf.keras.metrics.Mean(name='train_loss')
        self.val_loss = tf.keras.metrics.Mean(name='val_loss')

        self.train_iou = tf.keras.metrics.MeanIoU(num_classes=2, name='train_iou')
        self.val_iou = tf.keras.metrics.MeanIoU(num_classes=2, name='val_iou')

    def save_model(self):
        """
        Saves the model weights to the specified "model_out" path
        :return: None
        """
        tf.print('Saving Model Weights to', self.model_out)
        self.model.save_weights(self.model_out)

    @tf.function
    def train_step(self, images, labels):
        """
        One training step given a mini-batch of images and labels. Note the use of the annotation, @tf.function.
        This annotation will allow TensorFlow to analyze the method and speed up training. However you must be
        careful on what is placed inside @tf.function. See the following links for details:
        * https://www.tensorflow.org/api_docs/python/tf/function
        * https://www.tensorflow.org/guide/function
        * https://pgaleone.eu/tensorflow/tf.function/2019/03/21/dissecting-tf-function-part-1/
        * https://pgaleone.eu/tensorflow/tf.function/2019/04/03/dissecting-tf-function-part-2/

        :param images: mini-batch of images in tensor format
        :param labels: mini-batch of labels in tensor format
        :return: None
        """
        with tf.GradientTape() as tape:
            predictions = self.model(images, training=True)
            loss = self.objective(labels, predictions)
            # loss += tf.add_n(self.model.losses)

        gradients = tape.gradient(loss, self.model.trainable_variables)
        self.optimizer.apply_gradients(zip(gradients, self.model.trainable_variables))
        self.train_loss(loss)
        self.train_iou(labels, tf.argmax(predictions, axis=3))

    @tf.function
    def val_step(self, images, labels):
        """
        One validation step given a mini-batch of images and labels

        :param images: mini-batch of images in tensor format
        :param labels: mini-batch of labels in tensor format
        :return: None
        """
        predictions = self.model(images, training=False)
        loss = self.objective(labels, predictions)
        # loss += tf.add_n(self.model.losses)

        self.val_loss(loss)
        self.val_iou(labels, tf.argmax(predictions, axis=3))

    def train(self):
        """
        Main Training Loop

        This method trains the model according to the parameters passed in __init__. It will run for the specified
        number of epochs, keep track of loss and IoU metrics and return the model and the metrics.

        :return: Trained Model, (Train-Loss over time, Validation-Loss over time),
                 (Train-IoU over time, Validation-IoU over time)
        """
        train_losses, val_losses = [], []
        train_ious, val_ious = [], []

        # Threshold that determines when weights start to be saved
        best_val_loss = 100

        try:
            for epoch in range(self.epochs):
                # Reset our metrics for each epoch
                self.train_loss.reset_states()
                self.val_loss.reset_states()
                self.train_iou.reset_states()
                self.val_iou.reset_states()

                # Train Step
                train_loop = tqdm(total=self.train_dataset_size // self.batch_size, position=0, leave=True)
                for images, labels in self.train_dataset:
                    self.train_step(images, labels)
                    train_loop.set_description('Train - Epoch: {}, Loss: {:.4f}, IoU: {:.4f}'.format(
                        epoch, self.train_loss.result(), self.train_iou.result()))
                    train_loop.update(1)
                train_loop.close()

                # Validation Step
                val_loop = tqdm(total=self.val_dataset_size // self.batch_size, position=0, leave=True)
                for images, labels, in self.val_dataset:
                    self.val_step(images, labels)
                    val_loop.set_description('Val   - Epoch: {}, Loss: {:.4f}, IoU: {:.4f}'.format(
                        epoch, self.val_loss.result(), self.val_iou.result()))
                    val_loop.update(1)
                val_loop.close()

                train_losses.append(self.train_loss.result().numpy())
                val_losses.append(self.val_loss.result().numpy())
                train_ious.append(self.train_iou.result().numpy())
                val_ious.append(self.val_iou.result().numpy())

                if val_losses[-1] < best_val_loss:
                    self.save_model()
                    best_val_loss = val_losses[-1]

        except Exception as e:
            print('Exception caught during training: {0}'.format(e))
        finally:
            tf.print('Finished Training')
            return self.model, (train_losses, val_losses), (train_ious, val_ious)

    def __call__(self):
        """
        Calls self.train() method which contains main training loop.

        :return The model, train/val losses as tuple, train/val ious as tuple
        """
        return self.train()
