bedtools getfasta -s -fi ../../Dataset/hg38_p12_ucsc.no_alts.no_fixs.fa -bed ../BAM_REF_Intersection/all_juncs/donor.bed -fo ../BAM_REF_Intersection/all_juncs/donor_seq.fa

bedtools getfasta -s -fi ../../Dataset/hg38_p12_ucsc.no_alts.no_fixs.fa -bed ../BAM_REF_Intersection/all_juncs/acceptor.bed -fo ../BAM_REF_Intersection/all_juncs/acceptor_seq.fa