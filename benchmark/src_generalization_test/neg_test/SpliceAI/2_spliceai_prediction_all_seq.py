import tensorflow as tf
from tensorflow.keras import backend as K
import os, sys
# import h5py
import matplotlib.pyplot as plt
from utils import *
import gc 

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import matplotlib.pyplot as plt; plt.rcdefaults()
# from tqdm import tqdm
# import warnings

from keras.models import load_model
from pkg_resources import resource_filename
# from spliceai.utils import one_hot_encode
import numpy as np
# from sklearn.metrics import accuracy_score, confusion_matrix, roc_auc_score, roc_curve, precision_recall_curve
# import pickle 

CONSTANT_SIZE = 10
def seq_name(seq):
    return seq[1:]

def main(argv):
    
    # defining input arguments
    BATCH_SIZE = int(argv[0]) * 2 # doubled because FASTA has 2 lines per entry
    BATCH_SIZE_BASE = 500 * 2
    TYPE = argv[1]
    database = argv[2]
    spliceai_version = argv[3]

    ##################################################
    # CHANGEME: getting the path of the spliceai files
    ##################################################
    input_dir = f'./1_output/{database}'
    output_dir = f'./2_output/spliceai_result_{spliceai_version}/{database}'

    path = f'./models/spliceai{spliceai_version}.h5'
    print(">> path\t\t: ", path)
    print(">> database\t: ", database)
    model = load_model(resource_filename('spliceai', path), compile=False)
    print(repr(model))
    all_lines = []
    label = '+'

    # input
    da_faf = f'{input_dir}/{database}_seq_{TYPE}.fa'

    # output
    os.makedirs(output_dir, exist_ok=True)
    d_score_tsv_f = f'{output_dir}/spliceai_all_seq.score.d.{TYPE}.{database}.tsv'
    a_score_tsv_f = f'{output_dir}/spliceai_all_seq.score.a.{TYPE}.{database}.tsv'
    n_score_tsv_f = f'{output_dir}/spliceai_all_seq.score.n.{TYPE}.{database}.tsv'
    name_tsv_f = f'{output_dir}/spliceai_all_seq.name.{TYPE}.{database}.tsv'

    d_score_fw = open(d_score_tsv_f, "a")
    a_score_fw = open(a_score_tsv_f, "a") 
    n_score_fw = open(n_score_tsv_f, "a") 
    name_fw = open(name_tsv_f, "a") 

    #################################
    ## Get all lines of sequences in FASTA file
    #################################
    with open(da_faf, "r") as f:
        print("Processing : ", da_faf)
        lines = f.read().splitlines()
        all_lines = lines
    print("all_lines  : ", len(all_lines))

    #################################
    ## Processing 'POSITIVE' samples
    #################################
    COUNTER = 0
    pidx = 0
    
    pidx = BATCH_SIZE-BATCH_SIZE_BASE
    seq = ""
    print("BATCH_SIZE     : ", BATCH_SIZE)
    print("BATCH_SIZE_BASE: ", BATCH_SIZE_BASE)

    while pidx < len(all_lines):
        print(pidx)
        if pidx == BATCH_SIZE:
            exit()    
        if pidx % 2 == 0:
            chr, start, end, strand = all_lines[pidx].split(";")
            #chr = chr[1:]
            name_fw.write(' '.join([chr, start, end, strand])+"\n")

            pass
        elif pidx % 2 == 1:
            seq = all_lines[pidx]
            X, Y = create_datapoints(seq, label)
            X = X[None, :]
            # Y = np.array(Y)
            X = tf.convert_to_tensor(X, dtype=tf.float32)
            # Y = tf.convert_to_tensor(Y, dtype=tf.float32)

            Y_pred = model.predict(X)
            
            K.clear_session()
            # del model
            gc.collect()
            COUNTER += 1
            # print("X.shape     : ", X.shape)
            # print("Y_pred.shape: ", Y_pred.shape)

            # donor_p = Y_pred[0][200-1][2]
            # acceptor_p = Y_pred[0][len(Y_pred)-200-1][1]
            # print("(chr, start, end, strand): ", (chr, start, end, strand))

            # print("donor_p    : ", donor_p)
            # print("acceptor_p : ", acceptor_p)

            # Y_pred = np.array(Y_pred)
            # print(Y_pred)
            # print("Y_pred.shape: ", Y_pred.shape)

            d_scores = Y_pred[0, :, 2]
            a_scores = Y_pred[0, :, 1]
            n_scores = Y_pred[0, :, 0]
            np.savetxt(d_score_fw, d_scores.reshape((1,len(d_scores))), delimiter=" ")
            np.savetxt(a_score_fw, a_scores.reshape((1,len(a_scores))), delimiter=" ")
            np.savetxt(n_score_fw, n_scores.reshape((1,len(n_scores))), delimiter=" ")
        pidx += 1
        print("====================")
        if pidx %100 == 0:
            print("pidx: ", pidx)


if __name__ == "__main__":
    main(sys.argv[1:])
