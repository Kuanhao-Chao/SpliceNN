import torch
from SpliceNN import *
from SpliceNN_utils import *
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as pl

def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "mps")
    model = torch.load("./MODEL/SpliceNN_4.pt")
    # seq = "AGTTCTTTATTGATTGGTGTGCCGTTTTCTCTGGAAGCCTCTTAAGAACACAGTGGCGCAGGCTGGGTGGAGCCGTCCCCCCATGGAGCACAGGCAGACAGAAGTCCCCGCCCCAGCTGTGTGGCCTCAAGCCAGCCTTCCGCTCCTTGAAGCTGGTCTCCACACAGTGCTGGTTCCGTCACCCCCTCCCAAGGAAGTAGGTCTGAGCAGCTTGTCCTGGCTGTGTCCATGTCAGAGCAACGGCCCAAGTCTGGGTCTGGGGGGGAAGGTGTCATGGAGCCCCCTACGATTCCCAGTCGTCCTCGTCCTCCTCTGCCTGTGGCTGCTGCGGTGGCGGCAGAGGAGGGATGGAGTCTGACACGCGGGCAAAGGCTCCTCCGGGCCCCTCACCAGCCCCAGGTTTATTGATTGGTGTGCCGTTTTCTCTGGAAGCCTCTTAAGAGAAGAACACAGTGGCGCAGGCTGGGTGGAGCCGTCCCCCCATGGAGCACAGGCAGACAAAAGTCCCCGCCCCAGCTGTGTGGCCTCAAGCCAGCCTTCCGCTCCTTGAAGCTGGTCTCCACACAGTGCTGGTTCCGTCACCCCCTCCCAAGGAAGTAGGTCTGAGCAGCTTGTCCTGGCTGTGTCCATGTCAGAGCAACGGCCCAAGTCTGGGTCTGGGGGGGAAGGTGTCATGGAGCCCCCTAGGATTCCCAGTCGTCCTCGTCCTCCTCTGCCTGTGGCTGCTGCGGTGGCGGCAGAGGAGGGATGGAGTCTGACACGCGGGCAAAGGCTCCTCCGGGCCCCTCACCAGCCCCAGG"

    seq = "AGGCTGAGGCAGGCAGATCATCTGAGGTCAGGAGTTCAGGACCAGCCTGGCCAACATGATGAAACCGCGTCTCTACTGAAAATACCAAAATTAGAGGGGCATGGTGGTGGTCACCTGTAATCCCAGCTACTTGGGAGGCCGAGGCAGGAGAACTGCTCAAAACTGGGAGGCAGAGGTTGCAGTGAGCCGAGATCACGCCACGACACTCCAGCCTGGGTGGCAGAGCAAGACTCTGTCTCAAAAAAAAAAAAAAGATACCTCATTATAATTTTAATTATAGTTTTGAACACCAGTAAGGTTACACACTTTTTCTTATGAATGTTATTTGTCTATTTTGAAATAGCTTTCTAATAATCACAATCTAAATCTACTTTATTCCTGAAAGGTCAGTTGTGGGTTGCATGTGGAAAATGCTCCTCTGCAGCAGAAGTATAATTGCCTTTCATTCCTTCGAGATGCTCTTGCAGGAGTAGGCAAGAATGTTGATCTGCCATCTATTCTTAACAAGGAGAGAAAGCAGAAATGTGGACTAAGGATTGTTAGGGGAAAGCAATTTAGATGGAATCAGGTACTACAATGTGCCAAATGATATGATGATTAGATCTGTTTGAACCCTGTTTAAGCCTTTATGAGGATTTTTTTTTAATGGCAAACTATCTTGGAGCTCTGCCCACAAGGCAAATGGCTACTAACCAAAGACTATTTATTTGCAGAAAATCCATCAAAGTCGTTACATGCAGATGAGTCACAAAGAGAAGATATCATCCTTTCATGATCCCCAGCCCCACTTCACCAAACTG"
    X, Y = create_datapoints(seq, '-')
    X = torch.Tensor(np.array([X])).to(torch.float32).to(device)
    Y = torch.Tensor(np.array(Y)).to(torch.float32).to(device)

    print("X: ", X.size())
    print("Y: ", Y.size())

    DNAs = torch.permute(X, (0, 2, 1))
    labels = torch.permute(Y, (0, 2, 1))


    loss, yp = model_fn(DNAs, labels, model, None, device)

    is_expr = (labels.sum(axis=(1,2)) >= 1)
    print("is_expr: ",is_expr)

    Acceptor_YL = labels[is_expr, 1, :].flatten().to('cpu').detach().numpy()
    Acceptor_YP = yp[is_expr, 1, :].flatten().to('cpu').detach().numpy()
    Donor_YL = labels[is_expr, 2, :].flatten().to('cpu').detach().numpy()
    Donor_YP = yp[is_expr, 2, :].flatten().to('cpu').detach().numpy()

    # objects = ('Python', 'C++', 'Java', 'Perl', 'Scala', 'Lisp')
    y_pos = np.arange(len(Acceptor_YL))
    print(y_pos)

    fig, ax = plt.subplots(figsize=(12, 6))
    ax2 = ax.twinx()  
    # Acceptor_YP[Acceptor_YP > 0.5] = 0

    ax.bar(y_pos, Acceptor_YP, align='center', alpha=0.5, width=5, color="blue")
    ax2.bar(y_pos, Donor_YP, align='center', alpha=0.5, width=5, color="red")

    # for label in (ax.get_xticklabels() + ax.get_yticklabels()):
    #     label.set_fontsize(10)
    # plt.rc('xtick',labelsize=3)
    # plt.xticks(y_pos, rotation = 45)
    plt.ylabel('SpliceNN prediction score')
    plt.title('SpliceNN')

    plt.savefig("spliceNN", dpi=300)



    A_accuracy, A_auc = print_top_1_statistics(Acceptor_YL, Acceptor_YP)
    D_accuracy, D_auc = print_top_1_statistics(Donor_YL, Donor_YP)
    # print("labels: ", labels)
    # print("Acceptor_YL: ", Acceptor_YL)
    # print("Acceptor_YP: ", Acceptor_YP)
    # print("Donor_YL: ", Donor_YL)
    # print("Donor_YP: ", Donor_YP)

    print("A_accuracy: ", A_accuracy)
    print("A_auc     : ", A_auc)
    print("D_accuracy: ", D_accuracy)
    print("D_auc     : ", D_auc)
    # print("loss: ", loss)
    # print("yp: ", yp)

    # print("X: ", X[5100])
    # print("Y: ", Y[200])
    # print("Y: ", Y[600])

    # mode.

if __name__ == "__main__":
    main()