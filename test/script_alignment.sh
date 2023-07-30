# Step 1: extract splice junctions in the alignment file
splam extract -P SRR1352129_chr9_sub.bam -o tmp_out_alignment

# Step 2: score all the extracted splice junctions
splam score -G chr9_subset.fa -m ../model/splam_script.pt -o tmp_out_alignment tmp_out_alignment/junction.bed

#Step 3: output the cleaned alignment file
splam clean -o tmp_out_alignment
