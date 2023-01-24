from SpliceNN_utils import *
from SpliceNN_dataset_Chromsome import *
# from SpliceNN_Conformer import *
from SpliceNN import *
import numpy as np
import torch
import torch.nn as nn
import sys
from torch.optim import Optimizer, AdamW
from torch.optim.lr_scheduler import LambdaLR
from tqdm import tqdm
import math
import os

#############################
# Global variable definition
#############################
EPOCH_NUM = 25
BATCH_SIZE = 100
N_WORKERS = 1

# print("\033[1mContext nucleotides: %d\033[0m" % (SL))
# print("\033[1mSequence length (output): %d\033[0m" % (SL))
# same_seeds(0)
# device = torch.device("cuda" if torch.cuda.is_available() else "mps")
# print(f"[Info]: Use {device} now!")

L = 64
# W = np.asarray([11, 11, 11, 11, 11, 11, 11, 11,
#                 21, 21, 21, 21, 41, 41, 41, 41])
#                 # , 81, 81, 81, 81, 161, 161, 161, 161])
# AR = np.asarray([1, 1, 1, 1, 4, 4, 4, 4,
#                 10, 10, 10, 10, 25, 25, 25, 25])
#                 # , 50, 50, 50, 50, 100, 100, 100, 100])

W = np.asarray([11, 11, 11, 11, 11, 11, 11, 11,
                11, 11, 11, 11, 21, 21, 21, 21,
                21, 21, 21, 21])
                # , 81, 81, 81, 81, 161, 161, 161, 161])
AR = np.asarray([1, 1, 1, 1, 5, 5, 5, 5,
                 10, 10, 10, 10, 15, 15, 15, 15,
                20, 20, 20, 20])
                # , 50, 50, 50, 50, 100, 100, 100, 100])


# W = np.asarray([41, 41, 41, 41, 41, 41, 41, 41, 41, 41])
# AR = np.asarray([1, 1, 1, 1, 1, 1, 1, 1, 1, 1])

# W = np.asarray([21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21, 21])
# AR = np.asarray([1, 1, 1, 1, 2, 2, 2, 2, 4, 4, 4, 4, 8, 8, 8, 8])

CL = 2 * np.sum(AR*(W-1))
print("\033[1mContext nucleotides: %d\033[0m" % (SL))
print("\033[1mSequence length (output): %d\033[0m" % (SL))
same_seeds(0)
device = torch.device("cuda" if torch.cuda.is_available() else "mps")
print(f"[Info]: Use {device} now!")


#############################
# Model Initialization
#############################
model = SpliceNN(L, W, AR).to(device)
criterion = nn.BCELoss()
optimizer = AdamW(model.parameters(), lr=1e-3)
print(f"[Info]: Finish creating model!",flush = True)
print("model: ", model)


#############################
# Training Data initialization
#############################
train_loader, test_loader = get_dataloader(BATCH_SIZE, N_WORKERS)
train_iterator = iter(train_loader)
valid_iterator = iter(test_loader)
print(f"[Info]: Finish loading data!",flush = True)
print("train_iterator: ", len(train_loader))
print("valid_iterator: ", len(test_loader))
MODEL_OUTPUT_BASE = "./MODEL/SpliceAI_6_RB_p_n_nn_n1_TB_all_samples_thr_100_splitByChrom_L64_C16_L800_v27/"
LOG_OUTPUT_BASE = MODEL_OUTPUT_BASE + "LOG/"
LOG_OUTPUT_TRAIN_BASE = MODEL_OUTPUT_BASE + "LOG/TRAIN/"
LOG_OUTPUT_TEST_BASE = MODEL_OUTPUT_BASE + "LOG/TEST/"

os.makedirs(LOG_OUTPUT_TRAIN_BASE, exist_ok=True)
os.makedirs(LOG_OUTPUT_TEST_BASE, exist_ok=True)

#############################
# Initialize scheduler
#############################
scheduler = get_cosine_schedule_with_warmup(optimizer, 1000, len(train_loader)*EPOCH_NUM)
print(f"[Info]: Initialized the scheduler! Warmup steps: ", 1000, ";  Total steps: ", len(train_loader)*EPOCH_NUM)

############################
# Log for training
############################
train_log_loss = LOG_OUTPUT_TRAIN_BASE + "train_loss.txt"
train_log_acc = LOG_OUTPUT_TRAIN_BASE + "train_accuracy.txt"
train_log_lr = LOG_OUTPUT_TRAIN_BASE + "train_lr.txt"

# train_log_A_topk_accuracy = LOG_OUTPUT_TRAIN_BASE + "train_A_topk_accuracy.txt"
# train_log_A_auc = LOG_OUTPUT_TRAIN_BASE + "train_A_auc.txt"
# train_log_A_threshold_precision = LOG_OUTPUT_TRAIN_BASE + "train_A_threshold_precision.txt"
# train_log_A_threshold_recall = LOG_OUTPUT_TRAIN_BASE + "train_A_threshold_recall.txt"
# train_log_D_topk_accuracy = LOG_OUTPUT_TRAIN_BASE + "train_D_topk_accuracy.txt"
# train_log_D_auc = LOG_OUTPUT_TRAIN_BASE + "train_D_auc.txt"
# train_log_D_threshold_precision = LOG_OUTPUT_TRAIN_BASE + "train_D_threshold_precision.txt"
# train_log_D_threshold_recall = LOG_OUTPUT_TRAIN_BASE + "train_D_threshold_recall.txt"
train_log_J_threshold_precision = LOG_OUTPUT_TRAIN_BASE + "train_J_threshold_precision.txt"
train_log_J_threshold_recall = LOG_OUTPUT_TRAIN_BASE + "train_J_threshold_recall.txt"

fw_train_log_loss = open(train_log_loss, 'w')
fw_train_log_acc = open(train_log_acc, 'w')
fw_train_log_lr = open(train_log_lr, 'w')

# fw_train_log_A_topk_accuracy = open(train_log_A_topk_accuracy, 'w')
# fw_train_log_A_auc = open(train_log_A_auc, 'w')
# fw_train_log_A_threshold_precision = open(train_log_A_threshold_precision, 'w')
# fw_train_log_A_threshold_recall = open(train_log_A_threshold_recall, 'w')
# fw_train_log_D_topk_accuracy = open(train_log_D_topk_accuracy, 'w')
# fw_train_log_D_auc = open(train_log_D_auc, 'w')
# fw_train_log_D_threshold_precision = open(train_log_D_threshold_precision, 'w')
# fw_train_log_D_threshold_recall = open(train_log_D_threshold_recall, 'w')
fw_train_log_J_threshold_precision = open(train_log_J_threshold_precision, 'w')
fw_train_log_J_threshold_recall = open(train_log_J_threshold_recall, 'w')

############################
# Log for testing
############################
test_log_loss = LOG_OUTPUT_TEST_BASE + "test_loss.txt"
test_log_acc = LOG_OUTPUT_TEST_BASE + "test_accuracy.txt"

# test_log_A_topk_accuracy = LOG_OUTPUT_TEST_BASE + "test_A_topk_accuracy.txt"
# test_log_A_auc = LOG_OUTPUT_TEST_BASE + "test_A_auc.txt"
# test_log_A_threshold_precision = LOG_OUTPUT_TEST_BASE + "test_A_threshold_precision.txt"
# test_log_A_threshold_recall = LOG_OUTPUT_TEST_BASE + "test_A_threshold_recall.txt"
# test_log_D_topk_accuracy = LOG_OUTPUT_TEST_BASE + "test_D_topk_accuracy.txt"
# test_log_D_auc = LOG_OUTPUT_TEST_BASE + "test_D_auc.txt"
# test_log_D_threshold_precision = LOG_OUTPUT_TEST_BASE + "test_D_threshold_precision.txt"
# test_log_D_threshold_recall = LOG_OUTPUT_TEST_BASE + "test_D_threshold_recall.txt"
test_log_J_threshold_precision = LOG_OUTPUT_TEST_BASE + "test_J_threshold_precision.txt"
test_log_J_threshold_recall = LOG_OUTPUT_TEST_BASE + "test_J_threshold_recall.txt"

fw_test_log_loss = open(test_log_loss, 'w')
fw_test_log_acc = open(test_log_acc, 'w')
# fw_test_log_A_topk_accuracy = open(test_log_A_topk_accuracy, 'w')
# fw_test_log_A_auc = open(test_log_A_auc, 'w')
# fw_test_log_A_threshold_precision = open(test_log_A_threshold_precision, 'w')
# fw_test_log_A_threshold_recall = open(test_log_A_threshold_recall, 'w')
# fw_test_log_D_topk_accuracy = open(test_log_D_topk_accuracy, 'w')
# fw_test_log_D_auc = open(test_log_D_auc, 'w')
# fw_test_log_D_threshold_precision = open(test_log_D_threshold_precision, 'w')
# fw_test_log_D_threshold_recall = open(test_log_D_threshold_recall, 'w')
fw_test_log_J_threshold_precision = open(test_log_J_threshold_precision, 'w')
fw_test_log_J_threshold_recall = open(test_log_J_threshold_recall, 'w')

def get_lr(optimizer):
    for param_group in optimizer.param_groups:
        return param_group['lr']

def train_one_epoch(epoch_idx, train_loader):
    epoch_loss = 0
    epoch_acc = 0
    epoch_donor_acc = 0
    epoch_acceptor_acc = 0

    print("**********************")
    print("** Training Dataset **")
    print("**********************")
    pbar = tqdm(total=len(train_loader), ncols=0, desc="Train", unit=" step")

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
    # for data in train_loader:
    for batch_idx, data in enumerate(train_loader):
        # print("batch_idx: ", batch_idx)
        # DNAs:  torch.Size([40, 800, 4])
        # labels:  torch.Size([40, 1, 800, 3])
        DNAs, labels, chr = data 
        DNAs = DNAs.to(torch.float32).to(device)
        labels = labels.to(torch.float32).to(device)

        DNAs = torch.permute(DNAs, (0, 2, 1))
        # labels = torch.permute(labels, (0, 2, 1))
        loss, accuracy, yp = model_fn(DNAs, labels, model, criterion)
        
        #######################################
        # predicting splice / non-splice
        #######################################    
        batch_loss = loss.item()
        batch_acc = accuracy
        epoch_loss += loss.item()
        epoch_acc += accuracy

        labels = labels.to("cpu")
        yp = yp.to("cpu")
        J_G_TP, J_G_FN, J_G_FP, J_G_TN, J_TP, J_FN, J_FP, J_TN = junc_statistics(labels, yp, 0.5, J_G_TP, J_G_FN, J_G_FP, J_G_TN)        


        pbar.update(1)
        pbar.set_postfix(
            batch_id=batch_idx,
            idx_train=len(train_loader)*BATCH_SIZE,
            loss=f"{batch_loss:.6f}",
            accuracy=f"{batch_acc:.6f}",
            J_Precision=f"{J_TP/(J_TP+J_FP+1e-6):.6f}",
            J_Recall=f"{J_TP/(J_TP+J_FN+1e-6):.6f}"
        )
        loss.backward()
        optimizer.step()
        scheduler.step()
        optimizer.zero_grad()

        fw_train_log_loss.write(str(batch_loss)+ "\n")
        fw_train_log_acc.write(str(batch_acc)+ "\n")
        fw_train_log_lr.write(str(get_lr(optimizer))+ "\n")
        # fw_train_log_A_topk_accuracy.write(str(A_accuracy)+ "\n")
        # fw_train_log_A_auc.write(str(A_auc)+ "\n")
        # fw_train_log_A_threshold_precision.write(f"{A_TP/(A_TP+A_FP+1e-6):.6f}\n")
        # fw_train_log_A_threshold_recall.write(f"{A_TP/(A_TP+A_FN+1e-6):.6f}\n")
        # fw_train_log_D_topk_accuracy.write(str(D_accuracy)+ "\n")
        # fw_train_log_D_auc.write(str(D_auc)+ "\n")
        # fw_train_log_D_threshold_precision.write(f"{D_TP/(D_TP+D_FP+1e-6):.6f}\n")
        # fw_train_log_D_threshold_recall.write(f"{D_TP/(D_TP+D_FN+1e-6):.6f}\n")
        fw_train_log_J_threshold_precision.write(f"{J_TP/(J_TP+J_FP+1e-6):.6f}\n")
        fw_train_log_J_threshold_recall.write(f"{J_TP/(J_TP+J_FN+1e-6):.6f}\n")


        #######################################
        # predicting pb for every bp
        #######################################    
        # is_expr = (labels.sum(axis=(1,2)) >= 1)
        # # print("is_expr: ", is_expr)

        # # Acceptor_YL = labels[is_expr, 1, :].flatten().to('cpu').detach().numpy()
        # Acceptor_YL = labels[is_expr, 1, :].flatten().to('cpu').detach().numpy()
        # Acceptor_YP = yp[is_expr, 1, :].flatten().to('cpu').detach().numpy()
        # Donor_YL = labels[is_expr, 2, :].flatten().to('cpu').detach().numpy()
        # Donor_YP = yp[is_expr, 2, :].flatten().to('cpu').detach().numpy()

        # A_YL = labels[is_expr, 1, :].to('cpu').detach().numpy()
        # A_YP = yp[is_expr, 1, :].to('cpu').detach().numpy()
        # D_YL = labels[is_expr, 2, :].to('cpu').detach().numpy()
        # D_YP = yp[is_expr, 2, :].to('cpu').detach().numpy()

        # J_G_TP, J_G_FN, J_G_FP, J_G_TN, J_TP, J_FN, J_FP, J_TN = print_junc_statistics(D_YL, A_YL, D_YP, A_YP, 0.5, J_G_TP, J_G_FN, J_G_FP, J_G_TN)        
        # A_accuracy, A_auc = print_top_1_statistics(Acceptor_YL, Acceptor_YP)
        # D_accuracy, D_auc = print_top_1_statistics(Donor_YL, Donor_YP)
        # A_G_TP, A_G_FN, A_G_FP, A_G_TN, A_TP, A_FN, A_FP, A_TN = print_threshold_statistics(Acceptor_YL, Acceptor_YP, 0.5, A_G_TP, A_G_FN, A_G_FP, A_G_TN)
        # D_G_TP, D_G_FN, D_G_FP, D_G_TN, D_TP, D_FN, D_FP, D_TN = print_threshold_statistics(Donor_YL, Donor_YP, 0.5, D_G_TP, D_G_FN, D_G_FP, D_G_TN)

        # batch_loss = loss.item()
        # epoch_loss += loss.item()
        # epoch_donor_acc += D_accuracy
        # epoch_acceptor_acc += A_accuracy

        # pbar.update(1)
        # pbar.set_postfix(
        #     batch_id=batch_idx,
        #     idx_train=len(train_loader)*BATCH_SIZE,
        #     loss=f"{batch_loss:.6f}",
        #     # accuracy=f"{batch_acc:.6f}",
        #     A_accuracy=f"{A_accuracy:.6f}",
        #     D_accuracy=f"{D_accuracy:.6f}",
        #     A_auc = f"{A_auc:.6f}",
        #     D_auc = f"{D_auc:.6f}",
        #     # A_TP=A_TP,
        #     # A_FN=A_FN, 
        #     # A_FP=A_FP, 
        #     # A_TN=A_TN,
        #     # D_TP=D_TP,
        #     # D_FN=D_FN, 
        #     # D_FP=D_FP, 
        #     # D_TN=D_TN,
        #     A_Precision=f"{A_TP/(A_TP+A_FP+1e-6):.6f}",
        #     A_Recall=f"{A_TP/(A_TP+A_FN+1e-6):.6f}",
        #     D_Precision=f"{D_TP/(D_TP+D_FP+1e-6):.6f}",
        #     D_Recall=f"{D_TP/(D_TP+D_FN+1e-6):.6f}",
        #     J_Precision=f"{J_TP/(J_TP+J_FP+1e-6):.6f}",
        #     J_Recall=f"{J_TP/(J_TP+J_FN+1e-6):.6f}"
        # )
        # loss.backward()
        # optimizer.step()
        # scheduler.step()
        # optimizer.zero_grad()

        # fw_train_log_loss.write(str(batch_loss)+ "\n")
        # fw_train_log_lr.write(str(get_lr(optimizer))+ "\n")
        # fw_train_log_A_topk_accuracy.write(str(A_accuracy)+ "\n")
        # fw_train_log_A_auc.write(str(A_auc)+ "\n")
        # fw_train_log_A_threshold_precision.write(f"{A_TP/(A_TP+A_FP+1e-6):.6f}\n")
        # fw_train_log_A_threshold_recall.write(f"{A_TP/(A_TP+A_FN+1e-6):.6f}\n")
        # fw_train_log_D_topk_accuracy.write(str(D_accuracy)+ "\n")
        # fw_train_log_D_auc.write(str(D_auc)+ "\n")
        # fw_train_log_D_threshold_precision.write(f"{D_TP/(D_TP+D_FP+1e-6):.6f}\n")
        # fw_train_log_D_threshold_recall.write(f"{D_TP/(D_TP+D_FN+1e-6):.6f}\n")
        # fw_train_log_J_threshold_precision.write(f"{J_TP/(J_TP+J_FP+1e-6):.6f}\n")
        # fw_train_log_J_threshold_recall.write(f"{J_TP/(J_TP+J_FN+1e-6):.6f}\n")
    pbar.close()

    # print(f'Epoch {epoch_idx+0:03}: | Loss: {epoch_loss/len(train_loader):.5f} | Donor Acc: {epoch_donor_acc/len(train_loader):.3f} | Acceptor Acc: {epoch_acceptor_acc/len(train_loader):.3f}')
    # print(f'Junction Precision: {J_G_TP/(J_G_TP+J_G_FP):.5f} | Junction Recall: {J_G_TP/(J_G_TP+J_G_FN):.5f} | TP: {J_G_TP} | FN: {J_G_FN} | FP: {J_G_FP} | TN: {J_G_TN}')
    # print(f'Donor Precision   : {D_G_TP/(D_G_TP+D_G_FP):.5f} | Donor Recall   : {D_G_TP/(D_G_TP+D_G_FN):.5f} | TP: {D_G_TP} | FN: {D_G_FN} | FP: {D_G_FP} | TN: {D_G_TN}')
    # print(f'Acceptor Precision: {A_G_TP/(A_G_TP+A_G_FP):.5f} | Acceptor Recall: {A_G_TP/(A_G_TP+A_G_FN):.5f} | TP: {A_G_TP} | FN: {A_G_FN} | FP: {A_G_FP} | TN: {A_G_TN}')
    # print ("Learning rate: %.5f" % (get_lr(optimizer)))
    # print("\n\n")


    print(f'Epoch {epoch_idx+0:03}: | Loss: {epoch_loss/len(train_loader):.5f} | Acc: {epoch_acc/len(train_loader):.3f}')
    print(f'Junction Precision: {J_G_TP/(J_G_TP+J_G_FP):.5f} | Junction Recall: {J_G_TP/(J_G_TP+J_G_FN):.5f} | TP: {J_G_TP} | FN: {J_G_FN} | FP: {J_G_FP} | TN: {J_G_TN}')
    print ("Learning rate: %.5f" % (get_lr(optimizer)))
    print("\n\n")


def test_one_epoch(epoch_idx, test_loader):
    print("*********************")
    print("** Testing Dataset **")
    print("*********************")
    epoch_loss = 0
    epoch_acc = 0
    # epoch_donor_acc = 0
    # epoch_acceptor_acc = 0
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
    for batch_idx, data in enumerate(test_loader):
        # print("batch_idx: ", batch_idx)
        # DNAs:  torch.Size([40, 800, 4])
        # labels:  torch.Size([40, 1, 800, 3])
        DNAs, labels, chr = data 
        # print("\nDNAs: ", DNAs.size())
        # print("labels: ", labels.size())
        DNAs = DNAs.to(torch.float32).to(device)
        labels = labels.to(torch.float32).to(device)
        # print("DNAs  : ", DNAs)
        # print("labels: ", labels)

        DNAs = torch.permute(DNAs, (0, 2, 1))
        # labels = torch.permute(labels, (0, 2, 1))
        loss, accuracy, yp = model_fn(DNAs, labels, model, criterion)
        # loss, yp = model_fn(DNAs, labels, model)
        
        #######################################
        # predicting splice / non-splice
        #######################################    
        batch_loss = loss.item()
        batch_acc = accuracy
        epoch_loss += loss.item()
        epoch_acc += accuracy

        labels = labels.to("cpu")
        yp = yp.to("cpu")
        J_G_TP, J_G_FN, J_G_FP, J_G_TN, J_TP, J_FN, J_FP, J_TN = junc_statistics(labels, yp, 0.5, J_G_TP, J_G_FN, J_G_FP, J_G_TN)        


        pbar.update(1)
        pbar.set_postfix(
            batch_id=batch_idx,
            idx_train=len(train_loader)*BATCH_SIZE,
            loss=f"{batch_loss:.6f}",
            accuracy=f"{batch_acc:.6f}",
            J_Precision=f"{J_TP/(J_TP+J_FP+1e-6):.6f}",
            J_Recall=f"{J_TP/(J_TP+J_FN+1e-6):.6f}"
        )

        fw_train_log_loss.write(str(batch_loss)+ "\n")
        fw_train_log_acc.write(str(batch_acc)+ "\n")
        fw_train_log_lr.write(str(get_lr(optimizer))+ "\n")
        # fw_train_log_A_topk_accuracy.write(str(A_accuracy)+ "\n")
        # fw_train_log_A_auc.write(str(A_auc)+ "\n")
        # fw_train_log_A_threshold_precision.write(f"{A_TP/(A_TP+A_FP+1e-6):.6f}\n")
        # fw_train_log_A_threshold_recall.write(f"{A_TP/(A_TP+A_FN+1e-6):.6f}\n")
        # fw_train_log_D_topk_accuracy.write(str(D_accuracy)+ "\n")
        # fw_train_log_D_auc.write(str(D_auc)+ "\n")
        # fw_train_log_D_threshold_precision.write(f"{D_TP/(D_TP+D_FP+1e-6):.6f}\n")
        # fw_train_log_D_threshold_recall.write(f"{D_TP/(D_TP+D_FN+1e-6):.6f}\n")
        fw_train_log_J_threshold_precision.write(f"{J_TP/(J_TP+J_FP+1e-6):.6f}\n")
        fw_train_log_J_threshold_recall.write(f"{J_TP/(J_TP+J_FN+1e-6):.6f}\n")


        #######################################
        # predicting pb for every bp
        #######################################    
        # is_expr = (labels.sum(axis=(1,2)) >= 1)

        # Acceptor_YL = labels[is_expr, 1, :].flatten().to('cpu').detach().numpy()
        # Acceptor_YP = yp[is_expr, 1, :].flatten().to('cpu').detach().numpy()
        # Donor_YL = labels[is_expr, 2, :].flatten().to('cpu').detach().numpy()
        # Donor_YP = yp[is_expr, 2, :].flatten().to('cpu').detach().numpy()

        # A_YL = labels[is_expr, 1, :].to('cpu').detach().numpy()
        # A_YP = yp[is_expr, 1, :].to('cpu').detach().numpy()
        # D_YL = labels[is_expr, 2, :].to('cpu').detach().numpy()
        # D_YP = yp[is_expr, 2, :].to('cpu').detach().numpy()

        # J_G_TP, J_G_FN, J_G_FP, J_G_TN, J_TP, J_FN, J_FP, J_TN = print_junc_statistics(D_YL, A_YL, D_YP, A_YP, 0.5, J_G_TP, J_G_FN, J_G_FP, J_G_TN)
        # A_accuracy, A_auc = print_top_1_statistics(Acceptor_YL, Acceptor_YP)
        # D_accuracy, D_auc = print_top_1_statistics(Donor_YL, Donor_YP)

        # A_G_TP, A_G_FN, A_G_FP, A_G_TN, A_TP, A_FN, A_FP, A_TN = print_threshold_statistics(Acceptor_YL, Acceptor_YP, 0.5, A_G_TP, A_G_FN, A_G_FP, A_G_TN)
        # D_G_TP, D_G_FN, D_G_FP, D_G_TN, D_TP, D_FN, D_FP, D_TN = print_threshold_statistics(Donor_YL, Donor_YP, 0.5, D_G_TP, D_G_FN, D_G_FP, D_G_TN)

        # batch_loss = loss.item()
        # epoch_loss += loss.item()
        # epoch_donor_acc += D_accuracy
        # epoch_acceptor_acc += A_accuracy

        # pbar.update(1)
        # pbar.set_postfix(
        #     batch_id=batch_idx,
        #     idx_train=len(test_loader)*BATCH_SIZE,
        #     loss=f"{batch_loss:.6f}",
        #     # accuracy=f"{batch_acc:.6f}",
        #     A_accuracy=f"{A_accuracy:.6f}",
        #     D_accuracy=f"{D_accuracy:.6f}",
        #     A_auc = f"{A_auc:.6f}",
        #     D_auc = f"{D_auc:.6f}",
        #     # A_TP=A_TP,
        #     # A_FN=A_FN, 
        #     # A_FP=A_FP, 
        #     # A_TN=A_TN,
        #     # D_TP=D_TP,
        #     # D_FN=D_FN, 
        #     # D_FP=D_FP, 
        #     # D_TN=D_TN,
        #     A_Precision=f"{A_TP/(A_TP+A_FP+1e-6):.6f}",
        #     A_Recall=f"{A_TP/(A_TP+A_FN+1e-6):.6f}",
        #     D_Precision=f"{D_TP/(D_TP+D_FP+1e-6):.6f}",
        #     D_Recall=f"{D_TP/(D_TP+D_FN+1e-6):.6f}",
        #     J_Precision=f"{J_TP/(J_TP+J_FP+1e-6):.6f}",
        #     J_Recall=f"{J_TP/(J_TP+J_FN+1e-6):.6f}"
        # )
        fw_test_log_loss.write(str(batch_loss)+ "\n")
        fw_test_log_acc.write(str(batch_acc)+"\n")
        # # fw_test_log_A_topk_accuracy.write(str(A_accuracy)+ "\n")
        # # fw_test_log_A_auc.write(str(A_auc)+ "\n")
        # # fw_test_log_A_threshold_precision.write(f"{A_TP/(A_TP+A_FP+1e-6):.6f}\n")
        # # fw_test_log_A_threshold_recall.write(f"{A_TP/(A_TP+A_FN+1e-6):.6f}\n")
        # # fw_test_log_D_topk_accuracy.write(str(D_accuracy)+ "\n")
        # # fw_test_log_D_auc.write(str(D_auc)+ "\n")
        # # fw_test_log_D_threshold_precision.write(f"{D_TP/(D_TP+D_FP+1e-6):.6f}\n")
        # # fw_test_log_D_threshold_recall.write(f"{D_TP/(D_TP+D_FN+1e-6):.6f}\n")
        fw_test_log_J_threshold_precision.write(f"{J_TP/(J_TP+J_FP+1e-6):.6f}\n")
        fw_test_log_J_threshold_recall.write(f"{J_TP/(J_TP+J_FN+1e-6):.6f}\n")
    pbar.close()
    # print(f'Epoch {epoch_idx+0:03}: | Loss: {epoch_loss/len(test_loader):.5f} | Donor Acc: {epoch_donor_acc/len(test_loader):.3f} | Acceptor Acc: {epoch_acceptor_acc/len(test_loader):.3f}')
    # print(f'Junction Precision: {J_G_TP/(J_G_TP+J_G_FP):.5f} | Junction Recall: {J_G_TP/(J_G_TP+J_G_FN):.5f} | TP: {J_G_TP} | FN: {J_G_FN} | FP: {J_G_FP} | TN: {J_G_TN}')
    # print(f'Donor Precision   : {D_G_TP/(D_G_TP+D_G_FP):.5f} | Donor Recall   : {D_G_TP/(D_G_TP+D_G_FN):.5f} | TP: {D_G_TP} | FN: {D_G_FN} | FP: {D_G_FP} | TN: {D_G_TN}')
    # print(f'Acceptor Precision: {A_G_TP/(A_G_TP+A_G_FP):.5f} | Acceptor Recall: {A_G_TP/(A_G_TP+A_G_FN):.5f} | TP: {A_G_TP} | FN: {A_G_FN} | FP: {A_G_FP} | TN: {A_G_TN}')

    print(f'Epoch {epoch_idx+0:03}: | Loss: {epoch_loss/len(test_loader):.5f} | Acc: {epoch_acc/len(test_loader):.3f}')
    print(f'Junction Precision: {J_G_TP/(J_G_TP+J_G_FP):.5f} | Junction Recall: {J_G_TP/(J_G_TP+J_G_FN):.5f} | TP: {J_G_TP} | FN: {J_G_FN} | FP: {J_G_FP} | TN: {J_G_TN}')

    print("")
    print("\n\n")


def main():
    #############################
    # Model Training
    #############################
    for epoch_num in range(EPOCH_NUM):
        train_one_epoch(epoch_num, train_loader)
        test_one_epoch(epoch_num, test_loader)
        torch.save(model, MODEL_OUTPUT_BASE+'SpliceNN_'+str(epoch_num)+'.pt')
        # test_one_epoch(epoch_num)

    fw_train_log_loss.close()
    fw_train_log_acc.close()
    fw_train_log_lr.close()
    # fw_train_log_A_topk_accuracy.close()
    # fw_train_log_A_auc.close()
    # fw_train_log_A_threshold_precision.close()
    # fw_train_log_A_threshold_recall.close()
    # fw_train_log_D_topk_accuracy.close()
    # fw_train_log_D_auc.close()
    # fw_train_log_D_threshold_precision.close()
    # fw_train_log_D_threshold_recall.close()

    fw_test_log_loss.close()
    fw_test_log_acc.close()
    # fw_test_log_A_topk_accuracy.close()
    # fw_test_log_A_auc.close()
    # fw_test_log_A_threshold_precision.close()
    # fw_test_log_A_threshold_recall.close()
    # fw_test_log_D_topk_accuracy.close()
    # fw_test_log_D_auc.close()
    # fw_test_log_D_threshold_precision.close()
    # fw_test_log_D_threshold_recall.close()

if __name__ == "__main__":
    main()