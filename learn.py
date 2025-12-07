import tensorflow as tf
from tensorflow.keras.activations import softplus

def lstar_loss(h_matrix,h_r,path_cost):
    f = tf.reshape(h_r, [1, -1])+path_cost
    tf.convert_to_tensor(h_matrix,dtype = tf.float32)
    o = tf.matmul(f,h_matrix)
    soft = tf.map_fn(softplus,o)
    return tf.reduce_mean(soft, axis=-1)
