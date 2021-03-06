import email_process as ep
import numpy as np
import process as pr
import time

start_time = time.time()

DP = pr.Data_Process()

DP.read_data(detail=True)
DP.data_frequency(idf=True)

# Joint prob of word and email being spam
joint_prob_spam = np.zeros(len(DP.vocab))

# Joint prob of word and email being not spam
joint_prob_notspam = np.zeros(len(DP.vocab))

# Check if spam and not spam are organized contiguously.
# If it is, the position where a new type starts is stored in diff.
# Otherwise an exception is raised
start = DP.train_email_class[0]
diff = 0
for index in range(len(DP.train_email_class)):
    if start != DP.train_email_class[index]:
        diff = index
        start = DP.train_email_class[index]

for index in range(diff, len(DP.train_email_class)):
    if start != DP.train_email_class[index]:
        raise Exception("train_email_class not contiguous")

# Record count of words in spam and not spam respectively
if start == 1:
    joint_prob_spam = np.sum(DP.train_bag_words[:diff],axis=0)
    joint_prob_notspam = np.sum(DP.train_bag_words[diff:],axis=0)
else:
    joint_prob_notspam = np.sum(DP.train_bag_words[:diff],axis=0)
    joint_prob_spam = np.sum(DP.train_bag_words[diff:],axis=0)

# Kill zeros
joint_prob_spam = [n+1 for n in joint_prob_spam]
joint_prob_notspam = [n+1 for n in joint_prob_notspam]

# Normalize the joint probability
total_count = np.sum(joint_prob_notspam) + np.sum(joint_prob_spam)

joint_prob_spam = [n/float(total_count) for n in joint_prob_spam]
joint_prob_notspam = [n/float(total_count) for n in joint_prob_notspam]


temp = np.array([joint_prob_notspam, joint_prob_spam])

# The marginal distribution of each word
word_prob = np.sum(temp, axis=0)

# The marginal distribution of each class
class_prob = np.sum(temp, axis=1)

print "Prob of each class: ", class_prob[0], class_prob[1]
print "Total prob of word: ", np.sum(word_prob)
print "Total prob of joint prob: ", np.sum(joint_prob_spam) + np.sum(joint_prob_notspam)

# Compute the ratio inside the logarithm of mutual information
ratio_spam = [joint_prob_spam[i]/(class_prob[1]*word_prob[i]) for i in range(len(word_prob))]
ratio_notspam = [joint_prob_notspam[i]/(class_prob[0]*word_prob[i]) for i in range(len(word_prob))]

# Compute mutual information
from math import log
I = np.zeros(len(word_prob))
for i in range(len(word_prob)):
    I[i] = joint_prob_spam[i]*log(ratio_spam[i]) + joint_prob_notspam[i]*log(ratio_notspam[i])

# Sort mutual information in descending order and take first num terms
word_index_raw = np.argsort(I)[::-1]

fit_time = time.time() - start_time

hour, minute, second = pr.time_process(fit_time)

print '\n'
print 'fit time: ' + str(hour) + "h " + str(minute) + "m " + str(second) + "s "

from sklearn.naive_bayes import MultinomialNB

list_range = range(10,1001,10)

temp = 1024
while temp < len(word_index_raw):
    list_range.append(temp)
    temp = temp * 2

list_range.append(len(word_index_raw))

false_pos = []
false_neg = []
error_prob = []

total_email = float(len(DP.test_email_class))


start_time = time.time()
for num in list_range:
    #print "Choose " + str(num) + " words for fitting..."
    word_index = word_index_raw[:num]

    clf = MultinomialNB().fit(DP.train_bag_words_transformed[:,word_index], DP.train_email_class)
    predicted = clf.predict(DP.test_bag_words_transformed[:,word_index])

    total_error, notspam_error, spam_error = pr.test_result(predicted, DP.test_email_class, print_out = False)

    error_prob.append(float(total_error)/total_email)
    false_neg.append(spam_error)
    false_pos.append(notspam_error)

predict_time = time.time() - start_time
hour, minute, second = pr.time_process(predict_time)

print '\n'
print 'Total prediction time: ' + str(hour) + "h " + str(minute) + "m " + str(second) + "s "
print '\n'

f = open("NB_Mutual_result.txt",'w')
print >> f, "Number_of_Words", "Error_Prob", "False_Pos", "False_Neg"

for i in range(len(list_range)):
    print >> f, list_range[i], error_prob[i], false_pos[i], false_neg[i]

import pylab

# Set fonts for plotting
font = {'weight' : 'normal',
        'size'   : 18}

pylab.rc('font', **font)

pylab.figure(1)
ax=pylab.subplot(111)
ax.set_xlim(xmin = list_range[0] - 1, xmax = list_range[-1]+1)
pylab.semilogx(list_range, error_prob, linewidth = 0, marker = 'o', markersize = 6)
pylab.xlabel("Number of Words")
pylab.ylabel("Error Prob")
pylab.savefig("Error_prob_nb_mutual.pdf", box_inches='tight')

pylab.figure(2)
ax=pylab.subplot(111)
ax.set_xlim(xmin = list_range[0] - 1, xmax = list_range[-1]+1)
pylab.semilogx(list_range, false_pos, label = "false positive", linewidth = 0, marker = 'o', markersize = 6)
pylab.semilogx(list_range, false_neg, label = "false negative", linewidth = 0, marker = 's', markersize = 6)
pylab.legend(loc='upper right', ncol=1, prop={'size':15})
pylab.xlabel("Number of Words")
pylab.ylabel("Number of Emails")
pylab.savefig("False_pos_neg_nb_mutual.pdf", box_inches='tight')

pylab.show()


"""
print '\n',"First " + str(num) +" words of highest MI:"
for i in range(len(word_index)):
    print vocab[word_index[i]], I[word_index[i]]
"""
