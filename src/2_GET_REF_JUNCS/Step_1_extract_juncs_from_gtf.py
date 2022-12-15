import os 
import re
import json 
import torch

def chr_name_convert():
    f_chrs = open("../Refseq_2_UCSU_chromosome_names.tsv", "r")
    lines = f_chrs.read().splitlines()
    chrs = {}
    for line in lines:
        eles = line.split("\t")
        chrs[eles[0]] = eles[1]
    return chrs


def main():

    chrs = chr_name_convert()
    
    mapping_f = open("../../Dataset/mapping.json")
    mapping = json.load(mapping_f)
    mapping_f.close()
    print(mapping)
    gene_id_2_name = {}
    gene_id_2_features = {}
    JUNC_COUNTER = 0
    fw = open("../REF_junctions/ref_d_a.bed", 'w')
    with open("../../Dataset/GRCh38_latest_genomic.gff", 'r') as f:
    # with open("../../Dataset/hg38c_protein_and_lncRNA.gtf", 'r') as f:

        lists = f.read().splitlines() 

        transcript_id = ""
        prev_transcript_id = ""
        gene_id = ""
        prev_gene_id = ""
        gene_name = ""
        prev_gene_name = ""
        chr = ""
        prev_chr = ""
        strand = "."
        prev_strand = "."
        boundaries = set()

        starts = []
        ends = []

        WRITE = False
        encoding_ls = [0]
        for line in lists:
            line = line.split("\t")
            if len(line) < 8:
                continue

            if (line[2] == "exon"):

                # features = line[8].split(";")
                # print("features: ", features)
                match = re.search(r"transcript_id=\w+", line[8])
                if match is not None:
                    # print(match.group()[14:])
                    transcript_id = match.group()[14:]
                # transcript_id = features[0][15:-1]
                # print("transcript_id: ", transcript_id)
                # gene_id = features[1][10:-1]
                # gene_name = features[2][12:-1]
                    chr = line[0]
                    strand = line[6]
                    exon_start = int(line[3])
                    exon_end = int(line[4])
                    # print("chr: ", chr)
                    # print("strand: ", strand)
                    # print("exon_start: ", exon_start)
                    # print("exon_end: ", exon_end)

                    print("transcript_id: ", transcript_id)
                    # print("gene_id: ", gene_id)
                    # print("gene_name: ", gene_name)
                    # print("chr: ", chr)
                    # print("exon_start: ", exon_start)
                    # print("exon_end: ", exon_end)

                    if prev_transcript_id != transcript_id:
                        # print(transcript_id)
                        # print("starts: ", starts)
                        # print("ends  : ",  ends)

                        if prev_strand == '-':
                            starts.reverse()    
                            ends.reverse()
                        
                        starts = starts[1:]
                        ends = ends[:-1]

                        if (prev_chr in chrs.keys()):
                            for idx in range(len(starts)):
                                JUNC_COUNTER += 1
                                # print(chr + "\t" + str(ends[idx]) + "\t" + str(starts[idx]) + "\t" + "JUNC"+str(JUNC_COUNTER) + "\t1\t" + strand + "\n")
                                # fw.write(chr + "\t" + str(ends[idx]) + "\t" + str(starts[idx]) + "\t" + "JUNC" + "\t1\t" + strand + "\n")
                                fw.write(chrs[prev_chr] + "\t" + str(ends[idx]) + "\t" + str(starts[idx]) + "\t" + "JUNC" + "\t1\t" + prev_strand + "\n")
                            
                        starts.clear()
                        ends.clear()
                    starts.append(exon_start)
                    ends.append(exon_end)

                    prev_transcript_id = transcript_id
                    prev_chr = chr
                    prev_strand = strand
    fw.close()

if __name__ == "__main__":
    main()