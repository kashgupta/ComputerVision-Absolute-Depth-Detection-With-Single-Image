from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import tensorflow as tf
import numpy as np


def myModel(features, labels, mode):
    # Create three fully connected layers respectively of size 10, 20, and 10 with
    # each layer having a dropout probability of 0.1
    net = features["x"]
    numClasses = 2
    numFeatures = 5
    for units in [numFeatures, 4, 3, numClasses]:
        net = tf.layers.dense(net, units=units, activation=tf.nn.relu)
        net = tf.layers.dropout(net, rate=0.1)

    # Compute logits (1 per class)
    logits = tf.layers.dense(net, numFeatures, activation=None)

    # Compute predictions via the argmax over the logits
    predicted_classes = tf.argmax(logits, 1)
    if mode == tf.estimator.ModeKeys.PREDICT:
        predictions = {
            'class': predicted_classes,
            'prob': tf.nn.softmax(logits)
        }
        return tf.estimator.EstimatorSpec(mode, predictions=predictions)

    # Convert the labels to a one-hot tensor of shape (length of features, 3) and
    # with a on-value of 1 for each one-hot vector of length 3.
    onehot_labels = tf.one_hot(labels, numFeatures, 1, 0)

    # Compute the loss as the cross-entropy of the softmax outputs
    loss = tf.losses.softmax_cross_entropy(onehot_labels=onehot_labels, logits=logits)

    # Create training optimizer, using adagrad to minimize the cross entropy loss
    if mode == tf.estimator.ModeKeys.TRAIN:
        optimizer = tf.train.AdagradOptimizer(learning_rate=0.1)
        train_op = optimizer.minimize(loss, global_step=tf.train.get_global_step())
        return tf.estimator.EstimatorSpec(mode, loss=loss, train_op=train_op)

    # Compute evaluation metrics
    eval_metric_ops = {
        'accuracy': tf.metrics.accuracy(
            labels=labels, predictions=predicted_classes)
    }

    return tf.estimator.EstimatorSpec(mode, loss=loss, eval_metric_ops=eval_metric_ops)

def runNeuralNet(Xtrain, Ytrain, Xtest):
    #get the classifier
    estimator = tf.estimator.Estimator(model_fn=myModel)

    #train the model in 1000 steps
    input_fn = tf.estimator.inputs.numpy_input_fn({"x": Xtrain}, y=Ytrain, num_epochs=None, shuffle=True)
    numSteps = 10000
    estimator.train(input_fn=input_fn, steps=numSteps)

    #print out the results
    train_input_fn = tf.estimator.inputs.numpy_input_fn({"x": Xtrain}, y=Ytrain, batch_size=4, num_epochs=1, shuffle=False)
    train_metrics = estimator.evaluate(input_fn=train_input_fn)
    print("train metrics: %r" % train_metrics)

    # predict classes for the test data
    test_input_fn = tf.estimator.inputs.numpy_input_fn({"x": Xtest}, num_epochs=1, shuffle=False)
    predictions = estimator.predict(input_fn=test_input_fn)
    y_predicted = np.array(list(p['class'] for p in predictions))

    return y_predicted

if __name__ == '__main__':
    tf.app.run()