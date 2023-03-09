import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import torch
import torch.nn as nn
# from TEST_dataset import *
from splam_dataset_Chromsome import *
from SPLAM import *
# from splam_utils import *
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
from tqdm import tqdm
import warnings
from sklearn.metrics import precision_recall_curve, roc_curve
import pickle 
import platform

warnings.filterwarnings("ignore")

MODEL_VERSION = "SPLAM_v5/"

def main():
    #############################
    # Global variable definition
    #############################
    EPOCH_NUM = 20
    BATCH_SIZE = 100
    N_WORKERS = 1

    #############################
    # Selecting device
    #############################
    device_str = None
    if torch.cuda.is_available():
        device_str = "cuda"
    else:
        if platform.system() == "Darwin":
            device_str = "mps"
        else:
            device_str = "cpu"
    device = torch.device(device_str)
    print(f"\033[1m[Info]: Use {device} now!\033[0m")

    MODEL = "./MODEL/"+MODEL_VERSION+"splam_21.pt"
    MODEL_OUTPUT_BASE = "../src_tools_evaluation/splam_result/"
    os.makedirs(MODEL_OUTPUT_BASE)
    model = torch.load(MODEL)

    #############################
    # Model Initialization
    #############################
    print(f"[Info]: Finish loading model!",flush = True)
    print("model: ", model)

    #############################
    # Training Data initialization
    #############################
    TARGET = 'test'

    criterion = nn.BCELoss()

    BATCH_SIZE = 100
    for shuffle in [True, False]:
        print("########################################")
        print(" Model: ", model)
        print("########################################")
        test_loader = get_eval_dataloader(BATCH_SIZE, MODEL_VERSION, N_WORKERS, shuffle)

        # test_iterator = iter(test_loader)
        print(f"[Info]: Finish loading data!", flush = True)
        print("valid_iterator: ", len(test_loader))
        LOG_OUTPUT_TEST_BASE = MODEL_OUTPUT_BASE + "/" + "LOG/"
        os.makedirs(LOG_OUTPUT_TEST_BASE, exist_ok=True)





        epoch_loss = 0
        epoch_acc = 0
        epoch_donor_acc = 0
        epoch_acceptor_acc = 0

        print("**********************")
        print("** Testing Dataset **")
        print("**********************")
        pbar = tqdm(total=len(test_loader), ncols=0, desc="Test", unit=" step")
        
        A_G_TP = 1e-6
        A_G_FN = 1e-6
        A_G_FP = 1e-6
        A_G_TN = 1e-6
        D_G_TP = 1e-6
        D_G_FN = 1e-6
        D_G_FP = 1e-6
        D_G_TN = 1e-6

        J_G_TP = 1e-6
        J_G_FN = 1e-6
        J_G_FP = 1e-6
        J_G_TN = 1e-6
        #######################################
        # Important => setting model into evaluation mode
        #######################################   
        model.eval()
        for batch_idx, data in enumerate(test_loader):
            # print("batch_idx: ", batch_idx)
            # DNAs:  torch.Size([40, 800, 4])
            # labels:  torch.Size([40, 1, 800, 3])
            DNAs, labels, chr = data 
            DNAs = DNAs.to(torch.float32).to(device)
            labels = labels.to(torch.float32).to(device)

            DNAs = torch.permute(DNAs, (0, 2, 1))
            labels = torch.permute(labels, (0, 2, 1))
            loss, yp = model_fn(DNAs, labels, model, criterion)


            #######################################
            # predicting all bp.
            #######################################    
            is_expr = (labels.sum(axis=(1,2)) >= 1)
            # print("is_expr: ", is_expr)

            # Acceptor_YL = labels[is_expr, 1, :].flatten().to('cpu').detach().numpy()
            Acceptor_YL = labels[is_expr, 1, :].flatten().to('cpu').detach().numpy()
            Acceptor_YP = yp[is_expr, 1, :].flatten().to('cpu').detach().numpy()
            Donor_YL = labels[is_expr, 2, :].flatten().to('cpu').detach().numpy()
            Donor_YP = yp[is_expr, 2, :].flatten().to('cpu').detach().numpy()

            A_YL = labels[is_expr, 1, :].to('cpu').detach().numpy()
            A_YP = yp[is_expr, 1, :].to('cpu').detach().numpy()
            D_YL = labels[is_expr, 2, :].to('cpu').detach().numpy()
            D_YP = yp[is_expr, 2, :].to('cpu').detach().numpy()

            J_G_TP, J_G_FN, J_G_FP, J_G_TN, J_TP, J_FN, J_FP, J_TN = print_junc_statistics(D_YL, A_YL, D_YP, A_YP, JUNC_THRESHOLD, J_G_TP, J_G_FN, J_G_FP, J_G_TN)        
            A_accuracy, A_auprc = print_top_1_statistics(Acceptor_YL, Acceptor_YP)
            D_accuracy, D_auprc = print_top_1_statistics(Donor_YL, Donor_YP)
            A_G_TP, A_G_FN, A_G_FP, A_G_TN, A_TP, A_FN, A_FP, A_TN = print_threshold_statistics(Acceptor_YL, Acceptor_YP, JUNC_THRESHOLD, A_G_TP, A_G_FN, A_G_FP, A_G_TN)
            D_G_TP, D_G_FN, D_G_FP, D_G_TN, D_TP, D_FN, D_FP, D_TN = print_threshold_statistics(Donor_YL, Donor_YP, JUNC_THRESHOLD, D_G_TP, D_G_FN, D_G_FP, D_G_TN)

            batch_loss = loss.item()
            epoch_loss += loss.item()
            epoch_donor_acc += D_accuracy
            epoch_acceptor_acc += A_accuracy

            pbar.update(1)
            pbar.set_postfix(
                batch_id=batch_idx,
                idx_test=len(test_loader)*BATCH_SIZE,
                loss=f"{batch_loss:.6f}",
                # accuracy=f"{batch_acc:.6f}",
                # A_accuracy=f"{A_accuracy:.6f}",
                # D_accuracy=f"{D_accuracy:.6f}",
                A_auprc = f"{A_auprc:.6f}",
                D_auprc = f"{D_auprc:.6f}",
                # A_TP=A_TP,
                # A_FN=A_FN, 
                # A_FP=A_FP, 
                # A_TN=A_TN,
                # D_TP=D_TP,
                # D_FN=D_FN, 
                # D_FP=D_FP, 
                # D_TN=D_TN,
                A_Precision=f"{A_TP/(A_TP+A_FP+1e-6):.6f}",
                A_Recall=f"{A_TP/(A_TP+A_FN+1e-6):.6f}",
                D_Precision=f"{D_TP/(D_TP+D_FP+1e-6):.6f}",
                D_Recall=f"{D_TP/(D_TP+D_FN+1e-6):.6f}",
                J_Precision=f"{J_TP/(J_TP+J_FP+1e-6):.6f}",
                J_Recall=f"{J_TP/(J_TP+J_FN+1e-6):.6f}"
            )
            loss.backward()
            optimizer.step()
            scheduler.step()
            optimizer.zero_grad()

            fw_test_log_loss.write(str(batch_loss)+ "\n")
            fw_test_log_A_auprc.write(str(A_auprc)+ "\n")
            fw_test_log_A_threshold_precision.write(f"{A_TP/(A_TP+A_FP+1e-6):.6f}\n")
            fw_test_log_A_threshold_recall.write(f"{A_TP/(A_TP+A_FN+1e-6):.6f}\n")
            fw_test_log_D_auprc.write(str(D_auprc)+ "\n")
            fw_test_log_D_threshold_precision.write(f"{D_TP/(D_TP+D_FP+1e-6):.6f}\n")
            fw_test_log_D_threshold_recall.write(f"{D_TP/(D_TP+D_FN+1e-6):.6f}\n")
            fw_test_log_J_threshold_precision.write(f"{J_TP/(J_TP+J_FP+1e-6):.6f}\n")
            fw_test_log_J_threshold_recall.write(f"{J_TP/(J_TP+J_FN+1e-6):.6f}\n")
        pbar.close()

        print(f'Epoch {epoch_idx+0:03}: | Loss: {epoch_loss/len(test_loader):.5f} | Donor top-k Acc: {epoch_donor_acc/len(test_loader):.3f} | Acceptor top-k Acc: {epoch_acceptor_acc/len(test_loader):.3f}')
        print(f'Junction Precision: {J_G_TP/(J_G_TP+J_G_FP):.5f} | Junction Recall: {J_G_TP/(J_G_TP+J_G_FN):.5f} | TP: {J_G_TP} | FN: {J_G_FN} | FP: {J_G_FP} | TN: {J_G_TN}')
        print(f'Donor Precision   : {D_G_TP/(D_G_TP+D_G_FP):.5f} | Donor Recall   : {D_G_TP/(D_G_TP+D_G_FN):.5f} | TP: {D_G_TP} | FN: {D_G_FN} | FP: {D_G_FP} | TN: {D_G_TN}')
        print(f'Acceptor Precision: {A_G_TP/(A_G_TP+A_G_FP):.5f} | Acceptor Recall: {A_G_TP/(A_G_TP+A_G_FN):.5f} | TP: {A_G_TP} | FN: {A_G_FN} | FP: {A_G_FP} | TN: {A_G_TN}')
        print ("Learning rate: %.5f" % (get_lr(optimizer)))
        print("\n\n")






        # ############################
        # # Log for testing
        # ############################
        # test_log_loss = LOG_OUTPUT_TEST_BASE + "test_loss.txt"
        # test_log_D_threshold_accuracy = LOG_OUTPUT_TEST_BASE + "test_D_threshold_accuracy.txt"
        # test_log_D_threshold_precision = LOG_OUTPUT_TEST_BASE + "test_D_threshold_precision.txt"
        # test_log_D_threshold_recall = LOG_OUTPUT_TEST_BASE + "test_D_threshold_recall.txt"

        # fw_test_log_loss = open(test_log_loss, 'w')
        # fw_test_log_D_threshold_accuracy = open(test_log_D_threshold_accuracy, 'w')
        # fw_test_log_D_threshold_precision = open(test_log_D_threshold_precision, 'w')
        # fw_test_log_D_threshold_recall = open(test_log_D_threshold_recall, 'w')
        # # test_one_epoch(0, test_loader)
        # print("*********************")
        # print("** Testing Dataset **")
        # print("*********************")
        # epoch_loss = 0
        # epoch_acc = 0
        # pbar = tqdm(total=len(test_loader), ncols=0, desc="Test", unit=" step")

        # J_G_TP = 1e-6
        # J_G_FN = 1e-6
        # J_G_FP = 1e-6
        # J_G_TN = 1e-6
        # All_Junction_YL = []
        # All_Junction_YP = []

        # model.eval()
        # # model.train()
        # with torch.no_grad():
        #     for batch_idx, data in enumerate(test_loader):
        #         # DNAs:  torch.Size([40, 800, 4])
        #         # labels:  torch.Size([40, 1, 800, 3])
        #         DNAs, labels, chr = data 
        #         DNAs = DNAs.to(torch.float32).to(device)
        #         labels = labels.to(torch.float32).to(device)

        #         DNAs = torch.permute(DNAs, (0, 2, 1))
        #         loss, accuracy, yps = model_fn(DNAs, labels, model, criterion)
            

        #         #######################################
        #         # predicting splice / non-splice
        #         #######################################    
        #         batch_loss = loss.item()
        #         batch_acc = accuracy
        #         epoch_loss += loss.item()
        #         epoch_acc += accuracy

        #         labels = labels.to("cpu").detach().numpy()
        #         yps = yps.to("cpu").detach().numpy()

        #         J_G_TP, J_G_FN, J_G_FP, J_G_TN, J_TP, J_FN, J_FP, J_TN = junc_statistics(labels, yps, 0.5, J_G_TP, J_G_FN, J_G_FP, J_G_TN)      

        #         All_Junction_YL.extend(labels)
        #         All_Junction_YP.extend(yps)

        #         pbar.update(1)
        #         pbar.set_postfix(
        #             epoch=batch_idx,
        #             idx_train=len(test_loader)*BATCH_SIZE,
        #             loss=f"{batch_loss:.6f}",
        #             accuracy=f"{batch_acc:.6f}",
        #             J_Precision=f"{J_TP/(J_TP+J_FP+1.e-10):.6f}",
        #             J_Recall=f"{J_TP/(J_TP+J_FN+1.e-10):.6f}"
        #         )
        #         fw_test_log_loss.write(str(batch_loss)+ "\n")
        #         fw_test_log_D_threshold_accuracy.write(str(batch_acc)+ "\n")
        #         fw_test_log_D_threshold_precision.write(f"{J_TP/(J_TP+J_FP+1.e-10):.6f}\n")
        #         fw_test_log_D_threshold_recall.write(f"{J_TP/(J_TP+J_FN+1.e-10):.6f}\n")
        # pbar.close()

        # TYPE = "shuffle" if shuffle else "noshuffle"

        # print("All_Junction_YP: ", All_Junction_YP)
        # print("All_Junction_YL: ", All_Junction_YL)

        # with open(MODEL_OUTPUT_BASE + "/splam." + TYPE + ".pkl", 'wb') as f: 
        #     pickle.dump(All_Junction_YP, f)
        #     pickle.dump(All_Junction_YL, f)


        # ############################
        # # Plotting ROC / PR curves
        # ############################
        # plot_roc_curve(All_Junction_YL, All_Junction_YP, "Acceptor")
        # plt.savefig(MODEL_OUTPUT_BASE+"output_800bp_roc_"+TYPE+".png", dpi=300)
        # plt.close()
        # plot_pr_curve(All_Junction_YL, All_Junction_YP, "Acceptor")
        # plt.savefig(MODEL_OUTPUT_BASE+"output_800bp_pr_"+TYPE+".png", dpi=300)
        # plt.close()

        # print(f'Epoch {0+0:03}: | Loss: {epoch_loss/len(test_loader):.5f} | Acc: {epoch_acc/len(test_loader):.3f}')
        # print(f'Expected #prediction: {len(test_loader)*BATCH_SIZE+0:03}')
        # print(f'Junction Precision  : {J_G_TP/(J_G_TP+J_G_FP):.5f} | Junction Recall: {J_G_TP/(J_G_TP+J_G_FN):.5f} | TP: {J_G_TP} | FN: {J_G_FN} | FP: {J_G_FP} | TN: {J_G_TN}')
        # print("")
        # print("\n\n")


def plot_pr_curve(true_y, y_prob, label):
    """
    plots the roc curve based of the probabilities
    """
    fpr, tpr, thresholds = precision_recall_curve(true_y, y_prob)
    plt.plot(fpr, tpr, label=label)
    plt.legend()
    plt.xlabel('Recall')
    plt.ylabel('Precision')

def plot_roc_curve(true_y, y_prob, label):
    """
    plots the roc curve based of the probabilities
    """
    fpr, tpr, thresholds = roc_curve(true_y, y_prob)
    plt.plot(fpr, tpr, label=label)
    plt.legend()
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')


if __name__ == "__main__":
    main()