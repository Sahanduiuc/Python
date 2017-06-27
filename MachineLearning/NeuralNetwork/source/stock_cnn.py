import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data
# import quandl
import numpy as np
from intraday import get_google_data
import pandas as pd

# quandl.ApiConfig.api_key = "pgZTGbk8X-D7SdwAS_wN"

# Hyper Parameter
# n_input = 78
n_output = 2
threshold = 0.2

# aapl = quandl.Dataset('WIKI/AAPL').data(
#     params={'start_date': '2001-01-01', 'end_date': '2010-01-01', 'transformation': 'rdiff'}).to_pandas()
# aapl_close = np.asarray(aapl['Adj. Close'])
# aapl_close_series = np.asarray([aapl_close[i:i + n_input] for i in range(0, aapl_close.shape[0] - n_input, n_input)])
# aapl_close_mean = np.asarray([aapl_close_series[i].mean() for i in range(aapl_close_series.shape[0])])
# aapl_close_mean_return = np.asarray([(i - j) / j for i, j in zip(aapl_close_mean[1:], aapl_close_mean[:-1])])
# aapl_close_mean_return_bool = aapl_close_mean_return > threshold
# print(aapl_close_mean_return_bool.shape[0])
# goog_intraday = get_google_finance_intraday('GOOG',60,40)
ibm = get_google_data('IBM',300,600)
ibm['date'] = [df.date() for df in ibm.index]
ibm['time'] = [df.time() for df in ibm.index]
ibm_time_series = ibm.pivot_table(index='time', values='CLOSE', columns='date')
ibm_time_series = ibm_time_series.fillna(method='bfill')
# ibm_close = ibm['CLOSE']
# ibm_close_group = ibm_close.groupby(pd.TimeGrouper('d'))
# ibm_close_mean = ibm_close_group.mean()
#
# valid = ibm_close_group.sum().notnull()
# ibm_close_series = ibm_close_group.apply(list).loc[valid]

# ibm_close_mean_dropna = ibm_close_mean.dropna(axis=0,how='any')
# ibm_close_mean_return = (ibm_close_mean_dropna[1:].values/ibm_close_mean_dropna[:-1] -1)*100
# ibm_close_mean_return_bool = ibm_close_mean_return>threshold
ibm_daily = ibm_time_series.mean()
ibm_daily_returns = 100*(ibm_daily.values[1:]/ibm_daily[:-1]-1)
ibm_daily_returns_bool = ibm_daily_returns > threshold

n_input = ibm_time_series.shape[0]  #79
n_samples = ibm_time_series.shape[1]-1  #49




# mnist = input_data.read_data_sets("MNIST_data",one_hot=True)
x = tf.placeholder(tf.float32, [None, n_input])
y_ = tf.placeholder(tf.float32, [None, n_output])
keep_prob = tf.placeholder(tf.float32)
x_image = tf.reshape(x, [-1, n_input, 1])

W_conv1 = tf.Variable(tf.truncated_normal([5, 1, 16]))
b_conv1 = tf.Variable(tf.truncated_normal([16]))
h_conv1 = tf.nn.relu(tf.nn.conv1d(x_image, W_conv1, stride=1, padding="SAME") + b_conv1)
# h_pooling = tf.nn.max_pool(h_conv1,ksize=[1,2,1],strides=[1,2,1],padding="SAME")

W_conv2 = tf.Variable(tf.truncated_normal([5, 16, 32]))
b_conv2 = tf.Variable(tf.truncated_normal([32]))
h_conv2 = tf.nn.relu(tf.nn.conv1d(h_conv1, W_conv2, stride=1, padding="SAME") + b_conv2)
# h_pooling = tf.nn.max_pool(h_conv2,ksize=[1,2,1],strides=[1,2,1],padding="SAME")
# h_pooling_flat = tf.reshape(h_pooling,[-1,10*32])
h_conv2_flat = tf.reshape(h_conv2, [-1, n_input * 32])

W_fc1 = tf.Variable(tf.truncated_normal([n_input * 32, 100]))
b_fc1 = tf.Variable(tf.truncated_normal([100]))
h_fc1 = tf.matmul(h_conv2_flat, W_fc1) + b_fc1
h_fc1_dropout = tf.nn.dropout(h_fc1, keep_prob=keep_prob)

W_fc2 = tf.Variable(tf.truncated_normal([100, n_output]))
b_fc2 = tf.Variable(tf.truncated_normal([n_output]))
h_fc2 = tf.matmul(h_fc1_dropout, W_fc2) + b_fc2

cross_entropy = tf.nn.softmax_cross_entropy_with_logits(logits=h_fc2, labels=y_)
train_step = tf.train.AdamOptimizer(1e-3).minimize(cross_entropy)
accuracy = tf.reduce_mean(tf.cast(tf.equal(tf.argmax(h_fc2, axis=1), tf.argmax(y_, axis=1)), tf.float32))
accuracy2 = tf.reduce_sum(tf.cast(
    tf.logical_and(tf.equal(tf.argmax(y_,axis=1),1),tf.equal(tf.argmax(h_fc2,axis=1),1))
    ,tf.float32))/tf.reduce_sum(tf.cast(tf.equal(tf.argmax(y_,axis=1),1),tf.float32))
accuracy3 = tf.reduce_sum(tf.cast(
    tf.logical_and(tf.equal(tf.argmax(y_,axis=1),0),tf.equal(tf.argmax(h_fc2,axis=1),0))
    ,tf.float32))/tf.reduce_sum(tf.cast(tf.equal(tf.argmax(y_,axis=1),0),tf.float32))

# accuracy = tf.reduce_mean(tf.logical_and(tf.equal(tf.argmax(h_fc2, axis=1), 1),
#                           tf.equal(tf.argmax(y_, axis=1), 1)))
with tf.Session() as sess:
    sess = tf.Session()
    sess.run(tf.global_variables_initializer())

    # for i in range(aapl_close_mean_return_bool.shape[0]):
    #     #batch = mnist.train.next_batch(100)
    #     batch_x = aapl_close_series[i]
    #     batch_y = aapl_close_mean_return_bool[i]
    #
    #     if i%10 == 0:
    #         print("step%d accuracy%g" %(i,sess.run(accuracy,feed_dict={x:batch_x,y_:batch_y,keep_prob:1})))
    #
    #     sess.run(train_step, feed_dict={x: batch_x, y_: batch_y, keep_prob: 0.4})

    # train_x = aapl_close_series[:-1]
    # b = np.zeros((np.size(aapl_close_mean_return_bool), 2))
    # n_samples = aapl_close_mean_return_bool.shape[0]
    # b[np.arange(n_samples), aapl_close_mean_return_bool * 1] = 1
    # train_y = b

    # train_x = ibm_close_series[:-1]
    # n_sample = ibm_close_mean_return_bool.shape[0]
    # train_y = np.zeros((n_sample,2))
    # train_y[np.arange(n_sample),ibm_close_mean_return_bool*1] = 1

    train_x = ibm_time_series.ix[:,:-1]
    train_x = train_x.as_matrix().T
    train_y = np.zeros((n_samples,2))
    train_y[np.arange(n_samples),ibm_daily_returns_bool*1] = 1


    # print("step%d accuracy%g" %(1,sess.run(accuracy,feed_dict={x:train_x,y_:train_y,keep_prob:1})))
    # sess.run(train_step, feed_dict={x: train_x, y_: train_y, keep_prob: 0.4})
    # print("step%d accuracy%g" %(1,sess.run(accuracy,feed_dict={x:train_x,y_:train_y,keep_prob:1})))
    train_x_batches = train_x.reshape((-1, 49, n_input))
    train_y_batches = train_y.reshape((-1, 49, n_output))
    j = 0
    for i in range(50):
        for batch in zip(train_x_batches, train_y_batches):
            j += 1
            print("step %d, accuracy %g" % (j, sess.run(accuracy, feed_dict={x: batch[0], y_: batch[1], keep_prob: 0.3})))
            sess.run(train_step, feed_dict={x: batch[0], y_: batch[1], keep_prob: 0.4})