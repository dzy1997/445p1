# EECS 445 - Winter 2018
# Project 1 - project1.py

import pandas as pd
import numpy as np
import itertools
import string
import random

from sklearn.svm import SVC, LinearSVC
from sklearn.model_selection import StratifiedKFold, GridSearchCV
from sklearn import metrics
from matplotlib import pyplot as plt

def load_data(fname):
    """
    Reads in a csv file and return a dataframe. A dataframe df is similar to dictionary.
    You can access the label by calling df['label'], the content by df['content']
    the rating by df['rating']
    """
    return pd.read_csv(fname)


def get_split_binary_data():
    """
    Reads in the data from data/dataset.csv and returns it using
    extract_dictionary and generate_feature_matrix split into training and test sets.
    The binary labels take two values:
        -1: poor/average
         1: good
    Also returns the dictionary used to create the feature matrices.
    """
    fname = "data/dataset.csv"
    dataframe = load_data(fname)
    dataframe = dataframe[dataframe['label'] != 0]
    positiveDF = dataframe[dataframe['label'] == 1].copy()
    negativeDF = dataframe[dataframe['label'] == -1].copy()
    X_train = pd.concat([positiveDF[:500], negativeDF[:500]]).reset_index(drop=True).copy()
    dictionary = extract_dictionary(X_train)
    X_test = pd.concat([positiveDF[500:700], negativeDF[500:700]]).reset_index(drop=True).copy()
    Y_train = X_train['label'].values.copy()
    Y_test = X_test['label'].values.copy()
    X_train = generate_feature_matrix(X_train, dictionary)
    X_test = generate_feature_matrix(X_test, dictionary)

    return (X_train, Y_train, X_test, Y_test, dictionary)


def get_imbalanced_data(dictionary):
    """
    Reads in the data from data/imbalanced.csv and returns it using
    extract_dictionary and generate_feature_matrix as a tuple
    (X_train, Y_train) where the labels are binary as follows
        -1: poor/average
        1: good
    Input:
        dictionary: the dictionary created via get_split_binary_data
    """
    fname = "data/imbalanced.csv"
    dataframe = load_data(fname)
    dataframe = dataframe[dataframe['label'] != 0]
    positiveDF = dataframe[dataframe['label'] == 1].copy()
    negativeDF = dataframe[dataframe['label'] == -1].copy()
    dataframe = pd.concat([positiveDF[:300], negativeDF[:700]]).reset_index(drop=True).copy()
    X_train = generate_feature_matrix(dataframe, dictionary)
    Y_train = dataframe['label'].values.copy()

    return (X_train, Y_train)


def get_imbalanced_test(dictionary):
    """
    Reads in the data from data/dataset.csv and returns a subset of it
    reflecting an imbalanced test dataset
        -1: poor/average
        1: good
    Input:
        dictionary: the dictionary created via get_split_binary_data
    """
    fname = "data/dataset.csv"
    dataframe = load_data(fname)
    dataframe = dataframe[dataframe['label'] != 0]
    positiveDF = dataframe[dataframe['label'] == 1].copy()
    negativeDF = dataframe[dataframe['label'] == -1].copy()
    X_test = pd.concat([positiveDF[:400], negativeDF[:100]]).reset_index(drop=True).copy()
    Y_test = X_test['label'].values.copy()
    X_test = generate_feature_matrix(X_test, dictionary)

    return (X_test, Y_test)


def get_multiclass_training_data():
    """
    Reads in the data from data/dataset.csv and returns it using
    extract_dictionary and generate_feature_matrix as a tuple
    (X_train, Y_train) where the labels are multiclass as follows
        -1: poor
         0: average
         1: good
    Also returns the dictionary used to create X_train.
    """
    fname = "data/dataset.csv"
    dataframe = load_data(fname)
    dictionary = extract_dictionary(dataframe)
    X_train = generate_feature_matrix(dataframe, dictionary)
    Y_train = dataframe['label'].values.copy()

    return (X_train, Y_train, dictionary)


def get_heldout_reviews(dictionary):
    """
    Reads in the data from data/heldout.csv and returns it as a feature
    matrix based on the functions extract_dictionary and generate_feature_matrix
    Input:
        dictionary: the dictionary created by get_multiclass_training_data
    """
    fname = "data/heldout.csv"
    dataframe = load_data(fname)
    X = generate_feature_matrix(dataframe, dictionary)
    return X


def generate_challenge_labels(y, uniqname):
    """
    Takes in a numpy array that stores the prediction of your multiclass
    classifier and output the prediction to held_out_result.csv. Please make sure that
    you do not change the order of the ratings in the heldout dataset since we will
    this file to evaluate your classifier.
    """
    pd.Series(np.array(y)).to_csv(uniqname+'.csv', header=['label'], index=False)
    return

def select_classifier(penalty='l2', c=1.0, degree=1, r=0.0, class_weight='balanced'):
    """
        Return a linear svm classifier based on the given
        penalty function and regularization parameter c.
        """
    # TODO: Optionally implement this helper function if you would like to
    # instantiate your SVM classifiers in a single function. You will need
    # to use the above parameters throughout the assignment.
    if penalty=="l2":
        return SVC(kernel="poly", C=c, degree=degree, coef0=r, class_weight=class_weight)
    if penalty=="l1":
        return LinearSVC(penalty="l1", C=c, class_weight=class_weight, dual=False)


def extract_dictionary(df):
    """
        Reads a panda dataframe, and returns a dictionary of distinct words
        mapping from each distinct word to its index (ordered by when it was found).
        Input:
        df: dataframe/output of load_data()
        Returns:
        a dictionary of distinct words that maps each distinct word
        to a unique index corresponding to when it was first found while
        iterating over all words in each review in the dataframe df
        """
    word_dict = {}
    
    # TODO: Implement this function
    index=0
    for text in df["text"]:
        for p in string.punctuation:
            text=text.replace(p," ")
        text=text.lower()
        spl=text.split()
        for word in spl:
            if word not in word_dict:
                word_dict[word]=index
                index=index+1
    return word_dict


def generate_feature_matrix(df, word_dict):
    """
        Reads a dataframe and the dictionary of unique words
        to generate a matrix of {1, 0} feature vectors for each review.
        Use the word_dict to find the correct index to set to 1 for each place
        in the feature vector. The resulting feature matrix should be of
        dimension (number of reviews, number of words).
        Input:
        df: dataframe that has the ratings and labels
        word_list: dictionary of words mapping to indices
        Returns:
        a feature matrix of dimension (number of reviews, number of words)
        """
    number_of_reviews = df.shape[0]
    number_of_words = len(word_dict)
    feature_matrix = np.zeros((number_of_reviews, number_of_words))
    # TODO: Implement this function
    index=0
    for text in df["text"]:
        for p in string.punctuation:
            text=text.replace(p," ")
        text=text.lower()
        spl=text.split()
        for word in spl:
            if word in word_dict:
                feature_matrix[index,word_dict[word]]=1
        index=index+1
    return feature_matrix

def cv_performance(clf, X, y, k=5, metric="accuracy"):
    """
        Splits the data X and the labels y into k-folds and runs k-fold
        cross-validation: for each fold i in 1...k, trains a classifier on
        all the data except the ith fold, and tests on the ith fold.
        Calculates the k-fold cross-validation performance metric for classifier
        clf by averaging the performance across folds.
        Input:
        clf: an instance of SVC()
        X: (n,d) array of feature vectors, where n is the number of examples
        and d is the number of features
        y: (n,) array of binary labels {1,-1}
        k: an int specifying the number of folds (default=5)
        metric: string specifying the performance metric (default='accuracy'
        other options: 'f1-score', 'auroc', 'precision', 'sensitivity',
        and 'specificity')
        Returns:
        average 'test' performance across the k folds as np.float64
        """
    # TODO: Implement this function
    scores = []
    #HINT: You may find the StratifiedKFold from sklearn.model_selection
    #to be useful
    skf = StratifiedKFold(n_splits=k)
    skf.get_n_splits(X,y)
    for train_index, test_index in skf.split(X, y):
        X_train, X_test = X[train_index], X[test_index]
        y_train, y_test = y[train_index], y[test_index]
        clf.fit(X_train,y_train)
        y_pred = clf.predict(X_test)
        if metric=="auroc":
            y_pred=clf.decision_function(X_test)
        score=performance(y_test, y_pred, metric)
        scores.append(score)
    
    #And return the average performance across all fold splits.
    return np.array(scores).mean()


def select_param_linear(X, y, k=5, metric="accuracy", C_range = [], penalty='l2'):
    """
        Sweeps different settings for the hyperparameter of a linear-kernel SVM,
        calculating the k-fold CV performance for each setting on X, y.
        Input:
        X: (n,d) array of feature vectors, where n is the number of examples
        and d is the number of features
        y: (n,) array of binary labels {1,-1}
        k: int specifying the number of folds (default=5)
        metric: string specifying the performance metric (default='accuracy',
        other options: 'f1-score', 'auroc', 'precision', 'sensitivity',
        and 'specificity')
        C_range: an array with C values to be searched over
        Returns:
        The parameter value for a linear-kernel SVM that maximizes the
        average 5-fold CV performance.
        """
    # TODO: Implement this function
    #HINT: You should be using your cv_performance function here
    #to evaluate the performance of each SVM
    maxc=0
    maxperf=0
    for c in C_range:
        clf = select_classifier(penalty=penalty, c=c)
        perf = cv_performance(clf, X, y, k=5, metric=metric)
        print(c, perf)
        if perf>maxperf:
            maxperf=perf
            maxc=c
    return maxc


def plot_weight(X,y,penalty,metric="",C_range=[]):
    """
        Takes as input the training data X and labels y and plots the L0-norm
        (number of nonzero elements) of the coefficients learned by a classifier
        as a function of the C-values of the classifier.
        """
    
    print("Plotting the number of nonzero entries of the parameter vector as a function of C")
    norm0 = []
    
    # TODO: Implement this part of the function
    #Here, for each value of c in C_range, you should
    #append to norm0 the L0-norm of the theta vector that is learned
    #when fitting an L2- or L1-penalty, degree=1 SVM to the data (X, y)
    
    for c in C_range:
        clf = select_classifier(penalty=penalty, c=c)
        clf.fit(X,y)
        n0=0
        for c in clf.coef_:
            if c!=0:
                n0+=1
        norm0.append(n0)
    
    #This code will plot your L0-norm as a function of c
    plt.plot(C_range, norm0)
    plt.xscale('log')
    plt.legend(['L0-norm'])
    plt.xlabel("Value of C")
    plt.ylabel("Norm of theta")
    plt.title('Norm-'+penalty+'_penalty.png')
    plt.savefig('Norm-'+penalty+'_penalty.png')
    plt.close()


def select_param_quadratic(X, y, k=5, metric="accuracy", param_range=[]):
    """
        Sweeps different settings for the hyperparameters of an quadratic-kernel SVM,
        calculating the k-fold CV performance for each setting on X, y.
        Input:
        X: (n,d) array of feature vectors, where n is the number of examples
        and d is the number of features
        y: (n,) array of binary labels {1,-1}
        k: an int specifying the number of folds (default=5)
        metric: string specifying the performance metric (default='accuracy'
        other options: 'f1-score', 'auroc', 'precision', 'sensitivity',
        and 'specificity')
        parameter_values: a (num_param, 2)-sized array containing the
        parameter values to search over. The first column should
        represent the values for C, and the second column should
        represent the values for r. Each row of this array thus
        represents a pair of parameters to be tried together.
        Returns:
        The parameter value(s) for a quadratic-kernel SVM that maximize
        the average 5-fold CV performance
        """
    # TODO: Implement this function
    # Hint: This will be very similar to select_param_linear, except
    # the type of SVM model you are using will be different...
    
    maxc=0
    macr=0
    maxperf=0
    for c,r in param_range:
        clf=select_classifier(c=c, degree=2, r=r)
        perf=cv_performance(clf, X, y, k=k, metric=metric)
        if perf>maxperf:
            maxc=c
            maxr=r
            maxperf=perf
    return maxc, maxr


def performance(y_true, y_pred, metric="accuracy"):
    """
        Calculates the performance metric as evaluated on the true labels
        y_true versus the predicted labels y_pred.
        Input:
        y_true: (n,) array containing known labels
        y_pred: (n,) array containing predicted scores
        metric: string specifying the performance metric (default='accuracy'
        other options: 'f1-score', 'auroc', 'precision', 'sensitivity',
        and 'specificity')
        Returns:
        the performance as an np.float64
        """
    # TODO: Implement this function
    # This is an optional but very useful function to implement.
    # See the sklearn.metrics documentation for pointers on how to implement
    # the requested metrics.

    if metric=="auroc":
        return metrics.roc_auc_score(y_true,y_pred)
    m=metrics.confusion_matrix(y_true,y_pred)
    tp,fn,fp,tn=m[0,0],m[0,1],m[1,0],m[1,1]
    if metric=="accuracy":
        return (tp+tn)/(tp+tn+fp+tn)
    if metric=="f1-score":
        pre=tp/(tp+fp)
        sen=tp/(tp+fn)
        return 2*pre*sen/(pre+sen)
    if metric=="sensitivity":
        return tp/(tp+fn)
    if metric=="precision":
        return tp/(tp+fp)
    if metric=="specificity":
        return tn/(tn+fp)


def main():
    # Read binary data
    # NOTE: READING IN THE DATA WILL NOT WORK UNTIL YOU HAVE FINISHED
    #       IMPLEMENTING generate_feature_matrix AND extract_dictionary
    X_train, Y_train, X_test, Y_test, dictionary_binary = get_split_binary_data()
    IMB_features, IMB_labels = get_imbalanced_data(dictionary_binary)
    IMB_test_features, IMB_test_labels = get_imbalanced_test(dictionary_binary)
    
    # TODO: Questions 2, 3, 4
    # average count of non-zero features
    
    # q2
    print("Number of unique words:",len(X_train[0]))
    print("Average number of non-zero features:",np.sum(X_train)/len(X_train))
    
    #q3.1(c)
    metrics=["accuracy","f1-score","auroc","precision","sensitivity","specificity"]
    selected_C=0
    C_range=[1e-3, 1e-2, 0.1,1,10,100,1000]
    for me in metrics:
        maxc=select_param_linear(X_train, y_train, metric=me, C_range = C_range)
        clf=select_classifier(c=maxc)
        score=cv_performance(clf, X_train, y_train, metric=me)
        print("C=",maxc,"is optimal under",me,"metric, cv_perf=",score)
        if me=="auroc":
            selected_C=maxc
    
    #q3.1(d)
    clf=select_classifier(c=selected_C)
    clf.fit(X_train)
    y_pred = clf.decision_function(X_test)
    auroc_score=performance(y_test, y_pred, metric="auroc")
    print("q3.1(d) Choose C which maximizes AUROC")
    print("The AUROC score is:",auroc_score)
    y_pred = clf.predict(X_test)
    for me in metrics:
        if me!="auroc":
            score=performance(y_test, y_pred, metric=me)
            print("The",me,"score is",score)

    #q3.1(e)
    plot_weight(X_train, y_train, "l2", C_range=C_range)

    #q3.1(f)
    clf = select_classifier(c=0.1)
    clf.fit(X_train,y_train)
    arg=clf.coef_.argsort()
    min_ind4=arg[:4]
    max_ind4=arg[:-5:-1]
    minwords=[]
    maxwords=[]
    
    for ind in min_ind4:
        for word, index in dictionary_binary.items():
            if index==ind:
                minwords.append(word)
    print("Most negative words")
    for i in range(4):
        print(clf.coef_[min_ind4[i]], minwords[i])
    
    
    for ind in max_ind4:
        for word, index in dictionary_binary.items():
            if index==ind:
                maxwords.append(word)
    print("Most positive words")
    for i in range(4):
        print(clf.coef_[max_ind4[i]], maxwords[i])
    
    #q3.2(a)
    r_range=[1e-3, 1e-2, 0.1, 1, 10, 100, 1000]
    cr_range=[]
    for c in C_range:
        for r in r_range:
            cr_range.append([c,r])
    [maxc,maxr]=select_param_quadratic(X_train, y_train, param_range=cr_range)
    print("q3.2(a)")
    print("C=",maxc,"r=",maxr,"is optimal")

    #q3.2(b)
    cr_range=[]
    for i in range(25):
        lgc=random.uniform(-3,3)
        lgr=random.uniform(-3,3)
        cr_range.append([10**lgc, 10**lgr])
    [maxc,maxr]=select_param_quadratic(X_train, y_train, param_range=cr_range)
    print("q3.2(b)")
    print("C=",maxc,"r=",maxr,"is optimal")
    
    #q3.4(a)
    maxc=0
    maxperf=0
    for c in C_range:
        clf=select_classifier(penalty='l1', c=c)
        y_pred=clf.decision_function(X_test)
        perf=performance(y_test, y_pred, "auroc")
        if perf>maxperf:
            maxc=c
            maxperf=perf
    print("q3.4(a)")
    print("c=",maxc,"is optimal")
    
    #q3.4(b)
    plot_weight(X_train, y_train, "l1", C_range=C_range)
    
    #q4.1(b)
    clf = select_classifier(c=0.01, class_weight={-1: 10,1 :1})
    clf.fit(X_train, y_train)
    y_pred=clf.decision_function(X_test)
    perf=performance(y_test, y_pred, metric="auroc")
    print("q4.1(b)")
    print("The auroc score is:",perf)
    y_pred=clf.predict(X_test)
    for me in metrics:
        if me!="auroc":
            perf=performance(y_test,y_pred,metric=me)
            print("The",me,"score is",score)
    
    #q4.2(a)
    clf = select_classifier(c=0.01, class_weight={-1: 1,1 :1})
    clf.fit(IMB_features, IMB_labels)
    y_pred=clf.decision_function(IMB_test_features)
    perf=performance(IMB_test_labels, y_pred, metric="auroc")
    print("q4.2(a)")
    print("The auroc score is:",perf)
    y_pred=clf.predict(X_test)
    for me in metrics:
        if me!="auroc":
            perf=performance(IMB_test_labels,y_pred,metric=me)
            print("The",me,"score is",score)

    #q4.3(a) choose auroc
    W_range=[-2,-1.5,-1,-0.5,0,0.5,1,1.5,2]
    W_range=[10**w for w in W_range]
    maxwn=0
    maxwp=0
    maxperf=0
    for Wn in W_range:
        for Wp in W_range:
            clf = select_classifier(c=1, class_weight={-1: Wn, 1:Wp})
            perf=cv_performance(clf, IMB_features, IMB_labels, metric="auroc")
            if perf>maxperf:
                maxperf=perf
                maxwn=Wn
                maxwp=Wp
    print("q4.3(a) Wn=",maxwn,"Wp=",maxwp,"is optimal")
    print("performance is:",maxperf)

    clf = select_classifier(c=1, class_weight={-1: 100, 1:100})
    perf = cv_performance(clf,IMB_features,IMB_labels,metric="auroc")
                        
    #q4.3(b)
    print("q4.3(b)")
    print("The auroc score is",maxperf)
    clf = select_classifier(c=1, class_weight={-1: maxwn, 1:maxwp})
    clf.fit(IMB_features, IMB_labels)
    y_pred=clf.predict(IMB_test_features)
    for me in metrics:
        if me != "auroc":
            perf=performance(IMB_test_labels, y_pred, metric=me)
            print("The",me,"score is",perf)

    #q4.4
    y_pred=clf.predict(IMB_test_features)

    clf1=select_classifier(c=1, class_weight={-1: 1,1 :1})
    clf1.fit(IMB_features, IMB_labels)
    y_pred1=clf1.predict(IMB_test_features)
    
    
    # Read multiclass dataange = C_range
    # TODO: Question 5: Apply a classifier to heldout features, and then use
    #       generate_challenge_labels to print the predicted labels
    multiclass_features, multiclass_labels, multiclass_dictionary = get_multiclass_training_data()
    heldout_features = get_heldout_reviews(multiclass_dictionary)


# if __name__ == '__main__':
#     main()
