# mkdir ./NEG_noncan_junctions/pre_filter/
SEQ_LENGTH=800
for DONOR_F in "./NEG_noncan_junctions/${SEQ_LENGTH}bp/donor"/*
do
    echo "$DONOR_F"
    sort -k2,2n -k3,3n "$DONOR_F" >> ./NEG_noncan_junctions/${SEQ_LENGTH}bp/donor.bed
done

for ACCEPTOR_F in "./NEG_noncan_junctions/${SEQ_LENGTH}bp/acceptor"/*
do
    echo "$ACCEPTOR_F"
    sort -k2,2n -k3,3n "$ACCEPTOR_F" >> ./NEG_noncan_junctions/${SEQ_LENGTH}bp/acceptor.bed
done

for D_A in "./NEG_noncan_junctions/${SEQ_LENGTH}bp/d_a"/*
do
    echo "$D_A"
    sort -k2,2n -k3,3n "$D_A"  >> ./NEG_noncan_junctions/${SEQ_LENGTH}bp/d_a.bed
done