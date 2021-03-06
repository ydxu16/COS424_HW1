import email_process as ep
import numpy as np
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.metrics import roc_curve, auc, precision_recall_curve
import pylab

# Any string with "Not" or "Non" in it is assigned with 0; otherwise 1
# In this case, "NotSpam" is 0, "Spam" is 1
def label_extract(class_label):
    if class_label.find("Not") > -1 or class_label.find("Non") > -1:
        return 0
    else:
        return 1

class Data_Process(object):
    def __init__(self,filename=None):
        self.fig_num_ = 1
        if filename == None:
            self.filename = {}
        else:
            self.filename = filename

        # A dictionary for various filenames
        self.filename_key = (["train_bag_words","train_class", "train_email","vocab","test_class",
            "test_email","test_bag_words"])
        self.filename_name = (["train_emails_bag_of_words_200.dat","train_emails_classes_200.txt",
            "train_emails_samples_class_200.txt","train_emails_vocab_200.txt",
            "test_emails_classes_0.txt","test_emails_samples_class_0.txt",
            "test_emails_bag_of_words_0.dat"])

        self._filename_construct()

    def _filename_construct(self):
        for i in range(len(self.filename_key)):
            try:
                self.filename[self.filename_key[i]]
            except:
                self.filename[self.filename_key[i]] = self.filename_name[i]


    def read_data(self, detail=False):
        # Email names for training set
        self.train_email_name = np.loadtxt(self.filename["train_email"], dtype=str)

        # Classes of each email for training set
        self.train_email_class = np.loadtxt(self.filename["train_class"], dtype=str)
        
        # Vocabulary
        self.vocab = np.loadtxt(self.filename["vocab"],dtype=str)

        # Change "NotSpam" and "Spam" to 0 and 1
        self.label = {}
        self.label[self.train_email_class[0]] = label_extract(self.train_email_class[0])
        self.label[self.train_email_class[-1]] = label_extract(self.train_email_class[-1])

        self.train_email_class = [self.label[n] for n in self.train_email_class]

        # Bag of words for training set
        self.train_bag_words = ep.read_bagofwords_dat(self.filename["train_bag_words"],
            len(self.train_email_name))

        # Read test data
        self.test_email_name = np.loadtxt(self.filename["test_email"], dtype=str)
        self.test_email_class = np.loadtxt(self.filename["test_class"], dtype=str)
        self.test_bag_words = ep.read_bagofwords_dat(self.filename["test_bag_words"],
            len(self.test_email_name))

        self.test_email_class = [self.label[n] for n in self.test_email_class]

        if detail:
            print "Total number of emails: ", len(self.train_email_name)
            print "Total number of class labels: ", len(self.train_email_class)
            print "Total number of words: ", len(self.vocab)

    def data_frequency(self, idf = False, sublinear_tf = False):
        tfidf_transformer = TfidfTransformer(use_idf = idf, sublinear_tf = sublinear_tf)
        self.train_bag_words_transformed = tfidf_transformer.fit_transform(self.train_bag_words)
        self.test_bag_words_transformed = tfidf_transformer.transform(self.test_bag_words)

    def ROC_curve(self, proba, filename = None, save_plot = True, xmin = -0.01, xmax = 1,
                  ymin = 0, ymax = 1.01, fig_num = 1, plot_show = True):
        fpr, tpr, thresholds = roc_curve(self.test_email_class, proba)
        roc_area = auc(fpr,tpr)

        font = {'size'   : 18}
        pylab.rc('font', **font)

        if fig_num < self.fig_num_:
            fig_num = self.fig_num_

        pylab.figure(fig_num)
        ax=pylab.subplot(111)
        ax.set_xlim(xmin = xmin, xmax = xmax)
        ax.set_ylim(ymax = ymax, ymin = ymin)

        x = np.linspace(0,1,100)
        legend = "ROC curve (area = " + str(roc_area) + " )"
        pylab.plot(fpr, tpr, label = legend,linewidth = 3)
        pylab.plot(x,x,linestyle = "--", linewidth = 3)

        pylab.xlabel("False Positive Rate")
        pylab.ylabel("True Positive Rate")
        pylab.legend(loc="lower right", ncol=1, prop={'size':16})

        if (filename is not None) and (save_plot is True):
            pylab.savefig(filename+".pdf",box_inches='tight')

        self.fig_num_ += 1

        if plot_show is True:
            pylab.show()

    def PRC_curve(self, proba, filename = None, save_plot = True, xmin = -0.01, xmax = 1,
                  ymin = 0, ymax = 1.01, fig_num = 1, plot_show = True):
        precision, recall, thresholds = precision_recall_curve(self.test_email_class, proba)

        font = {'size'   : 18}
        pylab.rc('font', **font)

        if fig_num < self.fig_num_:
            fig_num = self.fig_num_

        pylab.figure(fig_num)
        ax=pylab.subplot(111)
        ax.set_xlim(xmin = xmin, xmax = xmax)
        ax.set_ylim(ymax = ymax, ymin = ymin)

        x = np.linspace(0,1,100)
        legend = "Precision recall curve"

        pylab.plot(recall, precision, label = legend,linewidth = 3)
        #pylab.plot(x,x,linestyle = "--", linewidth = 3)

        pylab.xlabel("Recall")
        pylab.ylabel("Precision")
        pylab.legend(loc="lower right", ncol=1, prop={'size':16})

        if (filename is not None) and (save_plot is True):
            pylab.savefig(filename+".pdf",box_inches='tight')

        self.fig_num_ += 1

        if plot_show is True:
            pylab.show()

def test_result(predicted, test_email_class, print_out = True):
    total_error = 0
    spam_error = 0
    notspam_error = 0
    for n in range(len(predicted)):
        s = predicted[n] - test_email_class[n]
        total_error += abs(s)
        notspam_error += max(s,0)
        spam_error += abs(min(0,s))

    if print_out:
        print "Total Number of Wrong Prediction: ", total_error
        print "Total Number of Spam Error: ", spam_error
        print "Total Number of Non-Spam Error: ", notspam_error
        print "Total Number of Test Emails: ", len(test_email_class)
        print "Probability of Error: ", float(total_error)/float(len(test_email_class))
        print "Matching Probability: ", 1 - float(total_error)/float(len(test_email_class))

    return total_error, notspam_error, spam_error

def time_process(elapse_time):
    from math import floor
    hour = floor(elapse_time / 3600)
    minute = floor((elapse_time - 3600*hour) / 60)
    second = elapse_time - 3600*hour - 60 * minute
    return hour, minute, second

