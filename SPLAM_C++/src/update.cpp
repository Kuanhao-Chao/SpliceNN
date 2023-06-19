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
    if (verbose) {
        GMessage("\n###########################################\n");
        GMessage("** Step %d: Updating NH tags in final clean BAM file\n", STEP_COUNTER);
        GMessage("###########################################\n");
    }
    robin_hdd_rm_hit rm_hit;
    readnhHitFile(rm_hit);

        // for (auto const& x : rm_hit)
        // {
        //     std::cout << x.first  // string (key)
        //             << ':' 
        //             << x.second // string's value 
        //             << std::endl;
        // }

    int processed_aln = 0;


// // ALN summary
// int ALN_COUNT = 0;
// int ALN_COUNT_BAD = 0;
// int ALN_COUNT_GOOD = 0;
// int ALN_COUNT_GOOD_CAL = 0;

// // JUNC summary
// int JUNC_COUNT = 0;
// int JUNC_COUNT_GOOD = 0;
// int JUNC_COUNT_BAD = 0;

// // Paired
// int ALN_COUNT_SPLICED = 0;
// int ALN_COUNT_NSPLICED = 0;
// int ALN_COUNT_PAIRED = 0;
// int ALN_COUNT_SPLICED_UNIQ = 0;
// int ALN_COUNT_SPLICED_MULTI = 0;
// int ALN_COUNT_SPLICED_UNIQ_DISCARD = 0;
// int ALN_COUNT_SPLICED_MULTI_DISCARD = 0;
// int ALN_COUNT_NSPLICED_UNIQ = 0;
// int ALN_COUNT_NSPLICED_MULTI = 0;


// // Unpaired
// int ALN_COUNT_SPLICED_UNPAIR = 0;
// int ALN_COUNT_NSPLICED_UNPAIR = 0;
// int ALN_COUNT_UNPAIR = 0;
// int ALN_COUNT_SPLICED_UNIQ_UNPAIR = 0;
// int ALN_COUNT_SPLICED_MULTI_UNPAIR = 0;
// int ALN_COUNT_SPLICED_UNIQ_UNPAIR_DISCARD = 0;
// int ALN_COUNT_SPLICED_MULTI_UNPAIR_DISCARD = 0;
// int ALN_COUNT_NSPLICED_UNIQ_UNPAIR = 0;
// int ALN_COUNT_NSPLICED_MULTI_UNPAIR = 0;

    if (g_paired_removal) {
        // /*********************************
        //  * Processing multip-mapped spliced temporary alignments (paired)
        // *********************************/
        // update_NH_tag_write_alignment(outfname_s_multi_map_cleaned, processed_aln, rm_hit, ALN_COUNT_SPLICED_MULTI - ALN_COUNT_SPLICED_MULTI_DISCARD);

        // /*********************************
        //  * Processing multip-mapped non-spliced alignments (paired)
        // *********************************/
        // update_NH_tag_write_alignment(outfname_ns_multi_map, processed_aln, rm_hit, ALN_COUNT_NSPLICED_MULTI);
        // ALN_COUNT_NSPLICED_MULTI += 1;

        // /*********************************
        //  * Processing uniq-mapped non-spliced alignments (paired)
        // *********************************/
        // update_NH_tag_write_alignment(outfname_ns_uniq_map, processed_aln, rm_hit, ALN_COUNT_NSPLICED_UNIQ);
        // ALN_COUNT_NSPLICED_UNIQ += 1;

        // /*********************************
        //  * Processing multip-mapped spliced temporary alignments (unpaired)
        // *********************************/
        // update_NH_tag_write_alignment(outfname_s_multi_unpair_cleaned, processed_aln, rm_hit, ALN_COUNT_SPLICED_MULTI - ALN_COUNT_SPLICED_MULTI_DISCARD);
        // ALN_COUNT_NSPLICED_MULTI_UNPAIR += 1;

        // /*********************************
        //  * Processing multip-mapped non-spliced alignments (unpaired)
        // *********************************/
        // update_NH_tag_write_alignment(outfname_ns_multi_unpair, processed_aln, rm_hit, ALN_COUNT_NSPLICED_MULTI);
        // ALN_COUNT_NSPLICED_MULTI_UNPAIR += 1;

        // /*********************************
        //  * Processing uniq-mapped non-spliced alignments (unpaired)
        // *********************************/
        // update_NH_tag_write_alignment(outfname_ns_uniq_unpair, processed_aln, rm_hit, ALN_COUNT_NSPLICED_UNIQ);
        // ALN_COUNT_NSPLICED_UNIQ_UNPAIR += 1;

    } else {
        /*********************************
         * Processing multip-mapped spliced temporary alignments (unpaired)
        *********************************/
        update_NH_tag_write_alignment(outfname_s_multi_map_cleaned, outfile_s_multi_map_cleaned_nh_updated, processed_aln, rm_hit, ALN_COUNT_SPLICED_MULTI - ALN_COUNT_SPLICED_MULTI_DISCARD);

        /*********************************
         * Processing multip-mapped non-spliced alignments (unpaired)
        *********************************/
        update_NH_tag_write_alignment(outfname_ns_multi_map, outfile_ns_multi_map_nh_updated, processed_aln, rm_hit, ALN_COUNT_NSPLICED_MULTI);

        /*********************************
         * Processing uniq-mapped non-spliced alignments (unpaired)
        *********************************/
        // update_NH_tag_write_alignment(outfname_ns_uniq_map, processed_aln, rm_hit, ALN_COUNT_NSPLICED_UNIQ);
        // ALN_COUNT_NSPLICED_UNIQ += 1;
    }

    if (verbose) {
        GMessage("[INFO] %d alignments processed.\n", 
        ALN_COUNT_SPLICED_MULTI - ALN_COUNT_SPLICED_MULTI_DISCARD + 
        ALN_COUNT_NSPLICED_MULTI +
        ALN_COUNT_SPLICED_MULTI_UNPAIR - ALN_COUNT_SPLICED_MULTI_UNPAIR_DISCARD + 
        ALN_COUNT_NSPLICED_MULTI_UNPAIR);
    }
    return outfname_cleaned;
}

void readnhHitFile(robin_hdd_rm_hit& rm_hit) {
    GStr NH_tag_fname = out_dir + "/TMP/NH_tag_fix.csv";
    std::ifstream ref_f(NH_tag_fname.chars());
    std::string line;
    while(getline(ref_f, line)){
        std::string read_id;
        int hits;
        std::replace(line.begin(), line.end(), ',', ' ');
        std::stringstream ss(line);
        ss >> read_id;
        ss >> hits;
        rm_hit[read_id] = hits;
    }   
}

void update_NH_tag_write_alignment(GStr infname, GSamWriter *outfile, int& processed_aln, robin_hdd_rm_hit rm_hit, int bar_num) {
    GSamReader reader(infname.chars(), SAM_QNAME|SAM_FLAG|SAM_RNAME|SAM_POS|SAM_CIGAR|SAM_AUX);

    progressbar bar(bar_num);
    bar.set_opening_bracket_char("[INFO] SPLAM! Processing multi-mapped spliced alignments\n\t[");

    while ((brec=reader.next())!=NULL) {
        processed_aln += 1;
        if (verbose) {
            bar.update();
        }
        std::string kv = brec->name();
        kv = kv + "_" + std::to_string(brec->pairOrder());
        // GMessage("kv: %s\n", kv.c_str());
        if (rm_hit.find(kv) != rm_hit.end()) {
            // GMessage("\nkv: %s\n", kv.c_str());
            // GMessage("rm_hit[kv]: %d\n", rm_hit[kv]);
            // GMessage("Before update NH tag: %d\n", brec->tag_int("NH", 0));
            int new_nh = brec->tag_int("NH", 0) - rm_hit[kv];
            brec->add_int_tag("NH", new_nh);
            // GMessage("After update NH tag: %d\n", brec->tag_int("NH", 0));
        }
        int tmp = 0;
        keepAlignment(outfile, brec, tmp);
    }
    reader.bclose();
    delete outfile;
    GMessage("\n");
}