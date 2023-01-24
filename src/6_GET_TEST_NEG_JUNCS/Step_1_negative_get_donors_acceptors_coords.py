from Bio import SeqIO
import random
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

targets = {
    "chr1": 248956422,
    "chr2": 242193529,
    "chr3": 198295559,
    "chr4": 190214555,
    "chr5": 181538259,
    "chr6": 170805979,
    "chr7": 159345973,
    "chr8": 145138636,
    "chr9": 138394717,
    "chr10": 133797422,
    "chr11": 135086622,
    "chr12": 133275309,
    "chr13": 114364328,
    "chr14": 107043718,
    "chr15": 101991189,
    "chr16": 90338345,
    "chr17": 83257441,
    "chr18": 80373285,
    "chr19": 58617616,
    "chr20": 64444167,
    "chr21": 46709983,
    "chr22": 50818468,
    "chrX": 156040895,
    "chrY": 57227415
}

def get_hg38_chrom_size():
    f_chrs = open("../hg38_chrom_size.tsv", "r")
    lines = f_chrs.read().splitlines()
    chrs = {}
    for line in lines:
        eles = line.split("\t")
        chrs[eles[0]] = int(eles[1])
    return chrs

chrs = get_hg38_chrom_size()

# TARGET = "NEG_junctions"
TARGET = "NEG_noncan_junctions"

EACH_JUNC_PER_CHROM = 5000
MIN_JUNC = 400
MAX_JUNC = 2000
ROOT_DIR = "../TEST/"+TARGET+"/"
os.makedirs(ROOT_DIR, exist_ok=True)
os.makedirs(ROOT_DIR+"donor/", exist_ok=True)
os.makedirs(ROOT_DIR+"acceptor/", exist_ok=True)
os.makedirs(ROOT_DIR+"d_a/", exist_ok=True)

threshold = "100"
hg38_ref = "../../Dataset/hg38_p12_ucsc.no_alts.no_fixs.fa"
D_A_POSITIONS = set()

def task(description, sequence):
    fw_donor = open(ROOT_DIR+"donor/"+description+"_donor.bed", "w")
    fw_acceptor = open(ROOT_DIR+"acceptor/"+description+"_acceptor.bed", "w")
    fw_da = open(ROOT_DIR+"d_a/"+description+"_d_a.bed", "w")
    print("description: ", description)
    # for i in range(EACH_JUNC_PER_CHROM):
    idx = 0
    while True:
        # if description == "chr13":
        #     print("idx: ", idx)
        if idx >= EACH_JUNC_PER_CHROM:
            break
        if idx % 1000 == 0:
            print("\t", idx)
        select_num = random.randint(0, len(sequence)-10000)
        # print("\tselect_num: ", select_num)
        # Finding the 'GT'
        donor_idx = 0
        acceptor_idx = 0
        

        if TARGET == "NEG_junctions":
            no_donor = False
            no_acceptor = False
            while not((select_num+donor_idx+1) < len(sequence) and sequence[select_num+donor_idx] == "G" and sequence[select_num+donor_idx+1] == "T"):
                # if description == "chr13":
                #     print("donor_idx: ", donor_idx)
                donor_idx += 1
                if select_num+donor_idx+1 >= chrs[description]:
                    no_donor = True
                    break
                if donor_idx > 10000:
                    no_donor = True
                    break
            if no_donor:
                continue

            while not((select_num+donor_idx+acceptor_idx) < len(sequence) and sequence[select_num+donor_idx+acceptor_idx-2] == "A" and sequence[select_num+donor_idx+acceptor_idx-1] == "G" and acceptor_idx > MIN_JUNC):
                # if description == "chr13":
                #     print("acceptor_idx: ", acceptor_idx)
                acceptor_idx += 1
                if select_num+donor_idx+acceptor_idx >= chrs[description]:
                    no_acceptor = True
                    break
                if acceptor_idx > 10000:
                    no_donor = True
                    break
            if no_acceptor:
                continue

        elif TARGET == "NEG_noncan_junctions":

            donor_idx = 0
            acceptor_idx = random.randint(MIN_JUNC, MAX_JUNC)

        donor_s = select_num+donor_idx-200
        donor_e = select_num+donor_idx+200
        acceptor_s = select_num+donor_idx+acceptor_idx-200
        acceptor_e = select_num+donor_idx+acceptor_idx+200

        ######################################################
        # Check if the donors and acceptors are in range.
        ######################################################
        if donor_e >= chrs[description] or acceptor_e >= chrs[description] or donor_s <= 0 or acceptor_s <= 0:
            continue
        
        ######################################################
        # Make sure there are no donors or acceptors inside the sequences.
        ######################################################
        in_da_set = False

        for d in range(donor_s, donor_e):
            if (description, d) in D_A_POSITIONS:
                in_da_set = True
        for a in range(acceptor_s, acceptor_e):
            if (description, a) in D_A_POSITIONS:
                in_da_set = True
        if in_da_set:
            continue

        D_A_POSITIONS.add((description, select_num+donor_idx))
        D_A_POSITIONS.add((description, select_num+donor_idx+acceptor_idx))

        fw_da.write(description + "\t" + str(select_num+donor_idx) + "\t" + str(select_num+donor_idx+acceptor_idx+1) + "\t" + "JUNC_donor\t1\t+\n")
        fw_donor.write(description + "\t" + str(donor_s) + "\t" + str(donor_e) + "\t" + "JUNC_donor\t1\t+\n")
        fw_acceptor.write(description + "\t" + str(acceptor_s) + "\t" + str(acceptor_e) + "\t" + "JUNC_donor\t1\t+\n")
        idx += 1
    fw_donor.close()
    fw_acceptor.close()
    fw_da.close()

def main():
    ############################################################
    # Excluding Positive JUNCS`../BAM_junctions/100_juncs/d_a.bed`
    ############################################################
    with open("../BAM_junctions/"+str(threshold)+"_juncs/d_a.bed", "r") as f:
        lines = f.read().splitlines()
        for line in lines:
            # print(line)
            eles = line.split("\t")
            # print("eles[0], eles[1]: ", eles[0], eles[1], eles[2])
            D_A_POSITIONS.add((eles[0], eles[1]))
            D_A_POSITIONS.add((eles[0], eles[2]))
    print("D_A_POSITIONS: ", len(D_A_POSITIONS))

    ############################################################
    # Excluding REF JUNCS `../REF_junctions/ref_d_a.sort.bed`
    ############################################################
    with open("../REF_junctions/ref_d_a.sort.bed", "r") as f:
        lines = f.read().splitlines()
        for line in lines:
            # print(line)
            eles = line.split("\t")
            # print("eles[0], eles[1]: ", eles[0], eles[1], eles[2])
            D_A_POSITIONS.add((eles[0], eles[1]))
            D_A_POSITIONS.add((eles[0], eles[2]))
    print("D_A_POSITIONS: ", len(D_A_POSITIONS))

    ############################################################
    # Excluding NEG noncan JUNCS `../NEG_noncan_junctions/d_a.bed`
    ############################################################
    with open("../NEG_noncan_junctions/d_a.bed", "r") as f:
        lines = f.read().splitlines()
        for line in lines:
            # print(line)
            eles = line.split("\t")
            # print("eles[0], eles[1]: ", eles[0], eles[1], eles[2])
            D_A_POSITIONS.add((eles[0], eles[1]))
            D_A_POSITIONS.add((eles[0], eles[2]))
    print("D_A_POSITIONS: ", len(D_A_POSITIONS))

    ############################################################
    # Excluding NEG JUNCS `../NEG_junctions/d_a.bed`
    ############################################################
    with open("../NEG_junctions/d_a.bed", "r") as f:
        lines = f.read().splitlines()
        for line in lines:
            # print(line)
            eles = line.split("\t")
            # print("eles[0], eles[1]: ", eles[0], eles[1], eles[2])
            D_A_POSITIONS.add((eles[0], eles[1]))
            D_A_POSITIONS.add((eles[0], eles[2]))
    print("D_A_POSITIONS: ", len(D_A_POSITIONS))


    with open(hg38_ref, 'r') as handle:
        # print("Len: ", len(SeqIO.parse(handle, 'fasta')))
        Path(ROOT_DIR+"donor/").mkdir(parents=True, exist_ok=True)
        Path(ROOT_DIR+"acceptor/").mkdir(parents=True, exist_ok=True)
        Path(ROOT_DIR+"d_a/").mkdir(parents=True, exist_ok=True)

        workers = 20
        # with ThreadPoolExecutor(workers) as pool:
        for record in SeqIO.parse(handle, 'fasta'):            
            # Extract individual parts of the FASTA record
            identifier = record.id
            description = record.description
            sequence = record.seq
            sequence = str(sequence).upper()

            # print("description: ", description)
            if (description in targets.keys()):
                task(description, sequence)
                # processed = pool.submit(task, description, sequence[0:100000])

if __name__ == "__main__":
    main()