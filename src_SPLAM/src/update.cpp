#include "update.h"
#include <fstream>
#include <iostream>
#include <cctype>
#include <sstream>
#include <filesystem>
#include <progressbar/progressbar.hpp>

// #include "predict.h"
// #include "extract.h"
#include "common.h"
#include "util.h"
#include "clean.h"

/****************************
* Input : (1) unordered_set of reads, (2) hashmap of removed hits.
* Output: (1) cleamed BAM file.
*****************************/
GStr splamNHUpdate() {
    STEP_COUNTER += 1;
    GMessage("\n###########################################\n");
    GMessage("** Step %d: Updating NH tags in final clean BAM file\n", STEP_COUNTER);
    GMessage("###########################################\n");
    std::unordered_map<std::string, int> nh_hm;

    GStr NH_tag_fname = out_dir + "/NH_tag_fix.csv";
    std::ifstream ref_f(NH_tag_fname.chars());
    std::string line;
    while(getline(ref_f, line)){
        std::string read_id;
        int hits;
        std::replace(line.begin(), line.end(), ',', ' ');
        std::stringstream ss(line);
        ss >> read_id;
        ss >> hits;
        nh_hm[read_id] = hits;
    }   
    GSamReader bam_reader_nh_updater(outfname_multimapped.chars(), SAM_QNAME|SAM_FLAG|SAM_RNAME|SAM_POS|SAM_CIGAR|SAM_AUX);

    // TInputFiles final_bam_records;
    // final_bam_records.setup(VERSION, argc, argv);
    // for (int i=0; i<in_records.freaders.Count(); i++) {
    //     GStr fname = in_records.freaders[i]->fname.chars();
    //     GMessage(">> fname: %s\n", fname.chars());
    //     final_bam_records.addFile(fname.chars());
    // }
    // int num_samples=final_bam_records.start();
    // outfile_cleaned = new GSamWriter(outfname_cleaned, final_bam_records.header(), GSamFile_BAM);
    // outfile_discard = new GSamWriter(outfname_discard, final_bam_records.header(), GSamFile_BAM);

    int bam_clean_counter=0;
    GMessage("[INFO] Processing BAM file ...\n");

    progressbar bar(ALN_COUNT_NH_UPDATE);
    bar.set_opening_bracket_char("[INFO] SPLAM! Output the final clean BAM file \n\t[");
    // while ((irec=final_bam_records.next())!=NULL) {
    while ((brec=bam_reader_nh_updater.next())!=NULL) {
        bar.update();
        // brec=irec->brec;
        std::string kv = brec->name();
        kv = kv + "_" + std::to_string(brec->pairOrder());
        int new_nh = brec->tag_int("NH", 0) - nh_hm[kv];
        brec->add_int_tag("NH", new_nh);
        outfile_cleaned->write(brec);
        
        // if (!brec->hasIntrons()) {
        //     if (nh_hm.find(kv) != nh_hm.end()) {
        //         int new_nh = brec->tag_int("NH", 0) - nh_hm[kv];
        //         brec->add_int_tag("NH", new_nh);
        //     }
        //     outfile_cleaned->write(brec);
        // } else {
        //     char* seq = brec->sequence();
        //     char* cigar_seq = brec->cigar();
        //     std::string rm_rd_key = kv + "_" + seq + "_" + cigar_seq + "_" + std::to_string(brec->flags()) + "_" + std::to_string(brec->start);
        //     free(seq);
        //     free(cigar_seq);

        //     if (rm_rd_set->find(rm_rd_key) != rm_rd_set->end()) {
        //         // The aln should be removed.
        //     } else {
        //         if (nh_hm.find(kv) != nh_hm.end()) {
        //             int new_nh = brec->tag_int("NH", 0) - nh_hm[kv];
        //             brec->add_int_tag("NH", new_nh);
        //         }
        //         outfile_cleaned->write(brec);
        //     }
        // }

        // if (brec->refId()!=prev_tid || (int)brec->start>b_end) {
        //     b_start=brec->start;
        //     b_end=endpos;
        //     prev_tid=brec->refId();
        //     prev_refname=(char*)brec->refName();
        // } else { //extending current bundle
        //     if (b_end<endpos) {
        //         b_end=endpos;
        //     }
        // }
        // outfile_fix->write(brec);
        // bam_clean_counter++;
        // if (bam_clean_counter % 1000000 == 0) {
        //     GMessage("\t\t%d alignments processed.\n", bam_clean_counter);
        // }
    }
    delete outfile_cleaned;
    // final_bam_records.stop();
    GMessage("\t\t%d alignments processed.\n", bam_clean_counter);
    return outfname_cleaned;
}