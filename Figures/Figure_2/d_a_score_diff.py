import matplotlib.pyplot as plt
import pickle
import numpy as np
import os
from util import *
import seaborn as sns
from sklearn import svm


# define a function to calculate precision, recall, F1 score, and queue rate
def calculate_metrics(threshold, true_labels, predict_probabilities):
    predictions = (predict_probabilities >= threshold).astype(int)
    true_positives = np.sum((predictions == 1) & (true_labels == 1))
    false_positives = np.sum((predictions == 1) & (true_labels == 0))
    false_negatives = np.sum((predictions == 0) & (true_labels == 1))
    true_negatives = np.sum((predictions == 0) & (true_labels == 0))
    precision = true_positives / (true_positives + false_positives)
    recall = true_positives / (true_positives + false_negatives)
    f1_score = 2 * (precision * recall) / (precision + recall)
    queue_rate = (true_positives + false_positives) / (true_positives + false_positives + true_negatives + false_negatives)
    return precision, recall, f1_score, queue_rate


def main():
    # for SPLAM_VERSION in ["SPLAM_v11", "SPLAM_v12"]:

    #####################################
    # Declaring parameters for probability & prediction array
    #####################################

    MANE_OR_ALTS = "ALTS"

    with open("../../src_tools_evaluation/spliceai_result/spliceai.da.N.merged.BOTH.pkl", "rb") as fr:
        spliceai_N_d_label = pickle.load(fr)
        spliceai_N_d_pred = pickle.load(fr)
        spliceai_N_a_label = pickle.load(fr)
        spliceai_N_a_pred = pickle.load(fr)

        # j_pred_prob = [x.numpy() for x in j_pred_prob]
        # j_pred_prob = [x.numpy() for x in j_pred_prob]

        print("\tspliceai_N_d_label : ", len(spliceai_N_d_label))
        print("\tspliceai_N_d_pred: ", len(spliceai_N_d_pred))
        print("\tspliceai_N_d_label : ", len(spliceai_N_d_label[spliceai_N_d_label == 1]))
        print("\tspliceai_N_d_pred: ", spliceai_N_d_pred)
        print("")
        print("\tspliceai_N_a_label : ", len(spliceai_N_a_label))
        print("\tspliceai_N_a_pred: ", len(spliceai_N_a_pred))
        print("\tspliceai_N_a_pred: ", len(spliceai_N_a_label[spliceai_N_a_label == 1]))
        print("\tspliceai_N_a_pred: ", spliceai_N_a_pred)
        print("")

    with open("../../src_tools_evaluation/spliceai_result/spliceai.da.noN.merged.BOTH.pkl", "rb") as fr:
        spliceai_noN_d_label = pickle.load(fr)
        spliceai_noN_d_pred = pickle.load(fr)
        spliceai_noN_a_label = pickle.load(fr)
        spliceai_noN_a_pred = pickle.load(fr)

        print("\tspliceai_noN_d_label : ", len(spliceai_noN_d_label))
        print("\tspliceai_noN_d_pred: ", len(spliceai_noN_d_pred))
        print("\tspliceai_noN_d_pred: ", spliceai_noN_d_pred)
        print("")
        print("\tspliceai_noN_a_label : ", len(spliceai_noN_a_label))
        print("\tspliceai_noN_a_pred: ", len(spliceai_noN_a_pred))
        print("\tspliceai_noN_a_pred: ", spliceai_noN_a_pred)
        print("")
        

    plt.figure(figsize=(9, 4))
    for type in ["filter", "nofilter"]:
        for SPLAM_VERSION in ["SPLAM_v11"]:#, "SPLAM_v12"]:
            os.makedirs("./IMG/"+SPLAM_VERSION+"/d_a_diff_plot/", exist_ok=True)
            #####################################
            # Creating directories for visualization.
            #####################################
            os.makedirs("./IMG/"+SPLAM_VERSION+"/DT_plot/", exist_ok=True)

            score_N_diff = spliceai_N_d_pred - spliceai_N_a_pred
            # if type == "filter":
            #     score_N_diff = score_N_diff[(score_N_diff> 0.15 )| (score_N_diff< -0.15)]

            score_noN_diff = spliceai_noN_d_pred - spliceai_noN_a_pred
            # if type == "filter":
            #     score_noN_diff = score_noN_diff[(score_noN_diff> 0.15) | (score_noN_diff< -0.15)]


            with open("../../src_tools_evaluation/splam_result/"+SPLAM_VERSION+"/splam.da.noshuffle.merged.BOTH.pkl",'rb') as f:
                splam_d_label = pickle.load(f)
                splam_d_pred = pickle.load(f)
                splam_a_label = pickle.load(f)
                splam_a_pred = pickle.load(f)
                print("\tsplam_d_label : ", len(splam_d_label))
                print("\tsplam_d_pred: ", len(splam_d_pred))
                print("")
                print("\tsplam_a_label : ", len(splam_a_label))
                print("\tsplam_a_pred: ", len(splam_a_pred))
                print("")

                splam_score_diff = splam_d_pred - splam_a_pred
                # if type == "filter":
                #     splam_score_diff = splam_score_diff[(splam_score_diff> 0.15) | (splam_score_diff< -0.15)]

                # generate some sample data for predict probabilities and true labels
                # predict_probabilities = np.minimum(splam_d_pred,splam_a_pred)
                # true_labels = splam_d_label


                if type == "nofilter":
                    sns.kdeplot(score_noN_diff, shade=True, clip = (-1.0, 1.0), alpha=0.25, label="SpliceAI-10k", color="#ff7f0e")
                elif type == "filter":
                    sns.kdeplot(score_noN_diff, shade=True, clip = (-1.0, -0.15), alpha=0.25, label="SpliceAI-10k", color="#ff7f0e")#, cut = -0.15)
                    sns.kdeplot(score_noN_diff, shade=True, clip = (0.15, 1.0), alpha=0.25, color="#ff7f0e")#, cut = 0.15)


                if type == "nofilter":
                    sns.kdeplot(splam_score_diff, shade=True, clip = (-1.0, 1.0), alpha=0.25, label="SPLAM", color="#2ca02c")
                elif type == "filter":
                    sns.kdeplot(splam_score_diff, shade=True, clip = (-1.0, -0.15), alpha=0.25, label="SPLAM", color="#2ca02c")#, cut = -0.15)
                    sns.kdeplot(splam_score_diff, shade=True, clip = (0.15, 1.0), alpha=0.25, color="#2ca02c")#, cut = 0.15)


                # if type == "nofilter":
                #     sns.kdeplot(score_N_diff, shade=True, clip = (-1.0, 1.0), alpha=0.25, label="SpliceAI-10k-Ns", color="#4C72B0")
                # elif type == "filter":
                #     sns.kdeplot(score_N_diff, shade=True, clip = (-1.0, -0.15), alpha=0.25, label="SpliceAI-10k-Ns", color="#4C72B0")#, cut = -0.15)
                #     sns.kdeplot(score_N_diff, shade=True, clip = (0.15, 1.0), alpha=0.25, color="#4C72B0")#, cut = 0.15)
                
                plt.axvline(x=-0.15, linestyle='--', color='black', label = "cutoff line (0.15 / -0.15)" )#, label='Optimal Threshold (maximum F1 score)')
                plt.axvline(x=0.15, linestyle='--', color='black')#, label='Optimal Threshold (maximum F1 score)')


                plt.xlabel('Scores')
                plt.ylabel('Density')
                # 'Score difference plot ('+
                # plt.rcParams['text.usetex'] = True
                # plt.rcParams.update(plt.rcParamsDefault)
                # plt.rcParams['text.usetex'] = True
                plt.title('Score difference plot ('+r'$Donor\;site\;score\;-\;Acceptor\;site\;score$)')

                # plt.text(2.5, 25, "My Plot", fontdict={'fontname': 'Arial', 'fontsize': 12, 'fontweight': 'bold'})
                # plt.text(2.5, 22, "Subtitle", fontdict={'fontname': 'Times New Roman', 'fontsize': 10})

                plt.legend(loc="upper right")
                plt.tight_layout()
                plt.grid(True)
                # Add a legend
                plt.savefig("./IMG/"+SPLAM_VERSION+"/d_a_diff_plot/"+type+".png", dpi=300)
                plt.clf()
                print(">>> Finish plotting 1 figure!")


if __name__ == "__main__":
    main()