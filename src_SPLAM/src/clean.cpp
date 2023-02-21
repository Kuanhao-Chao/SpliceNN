#include "clean.h"
#include "common.h"
#include "junc.h"
#include "junc_func.h"
#include "util.h"
#include "extract.h"
#include "predict.h"
// #include "progressbar.h"
#include <progressbar/progressbar.hpp>

#include <unordered_set>
#include <fstream>
#include <sstream>
#include <filesystem>
#include <unordered_map>
#include <htslib/htslib/faidx.h>
#include <Python.h>
#include <gclib/GStr.h>

void splamClean(int argc, char* argv[]) {
    GStr outfname_junc_score = splamPredict();

    /*********************************************
     * Step 4: SPLAM filtering out reads.
    *********************************************/
    // GMessage("> outfname_discard: %s\n", outfname_discard.chars());
    // GMessage("> outfname_cleaned: %s\n", outfname_cleaned.chars());
    // GMessage("> outfname_spliced: %s\n", outfname_spliced.chars());
    // GMessage("> outfname_nspliced: %s\n", outfname_nspliced.chars());

    GMessage("\n###########################################\n");
    GMessage("## Step 4: SPLAM filtering out reads\n");
    GMessage("###########################################\n\n");
    robin_hdd_hm rm_rd_hm;
    std::unordered_set<std::string> rm_rd_set;

    GMessage(">> rm_rd_set size %d\n", rm_rd_set.size());
    GStr outfname_spliced_good = filterSpurJuncs(outfname_junc_score, rm_rd_hm, rm_rd_set);
    GMessage(">> rm_rd_set size %d\n", rm_rd_set.size());

    delete outfile_discard;
    delete outfile_cleaned;
}


void loadBed(GStr inbedname, std::unordered_set<std::string> &rm_juncs) {
    std::ifstream bed_f(inbedname);
    std::string line;
    int bed_counter = 0;
    while (getline(bed_f, line)) {
        bed_counter ++;
        GStr gline = line.c_str();
        GVec<GStr> junc;
        int cnt = 0;
        while (cnt < 7) {
            GStr tmp = gline.split("\t");
            junc.Add(gline);
            gline=tmp;
            cnt++;
        }
        // GStr chr_str(chrname);
        if (junc[6].asDouble() <= threshold) {

            char* chrname =junc[0].detach();
            char* strand =junc[5].detach();
            // CJunc j(junc[1].asInt()+1, junc[2].asInt(), *junc[5].detach(), chr_str);
            std::string j = std::to_string(junc[1].asInt()) + "_" + std::to_string(junc[2].asInt()) + "_" + strand + "_" + chrname;
            rm_juncs.insert(j);
        }
    }
}


GStr filterSpurJuncs(GStr outfname_junc_score, robin_hdd_hm &rm_rd_hm, std::unordered_set<std::string> &rm_rd_set) {
    GStr outfname_spliced_good;
    // GSamWriter* outfile_spliced_good = NULL;
    outfname_spliced_good = out_dir + "/TMP/spliced_good.bam";

    // outfile_spliced_good = new GSamWriter(outfname_spliced_good, in_records.header(), GSamFile_BAM);

    GSamReader bam_reader_spliced(outfname_spliced.chars(), SAM_QNAME|SAM_FLAG|SAM_RNAME|SAM_POS|SAM_CIGAR|SAM_AUX);

    std::unordered_set<std::string> rm_juncs;
    GMessage("Before rm_juncs.size()  %d\n", rm_juncs.size());
    loadBed(outfname_junc_score, rm_juncs);
    GMessage("After rm_juncs.size()  %d\n", rm_juncs.size());

    int counter = 0, prev_tid=-1;
    GStr prev_refname;
    std::vector<std::pair<float,uint64_t>> bsam(2048*1024,{0,1}); // number of samples. 1st - current average; 2nd - total number of values
    int b_end=0, b_start=0;
    progressbar bar(ALN_COUNT_SPLICED);
    bar.set_opening_bracket_char("[INFO] SPLAM! Removing junctions with low scores \n\t[");

    while ((brec=bam_reader_spliced.next())!=NULL) {
        bar.update();

        uint32_t dupcount=0;
        int endpos=brec->end;
        int r_exon_count = brec->exons.Count();
        bool spur = false;
        // r_exon_count
        if (r_exon_count > 1) {
            GMessage("cigar: %s\n", brec->cigar());
            for (int e=1; e<2; e++) {
	            char strand = brec->spliceStrand();
                std::string jnew_sub = std::to_string(brec->exons[e-1].end) + "_" + std::to_string(brec->exons[e].start-1) + "_" + strand + "_" + brec->refName();
                if (rm_juncs.find(jnew_sub) != rm_juncs.end()) {

                    spur = true;
                    GMessage("jnew_sub: %s\n", jnew_sub.c_str());

                    break;
                }
            }
        }
        if (spur) {
            // std::cout << "~~ SPLAM!" << std::endl;
            std::string kv = brec->name();
            kv = kv + "_" + std::to_string(brec->pairOrder());
            if (rm_rd_hm.find(kv) == rm_rd_hm.end()) {
                rm_rd_hm[kv] = 1;
            } else {
                rm_rd_hm[kv]++;
            }
            char* seq = brec->sequence();
            char* cigar_seq = brec->cigar();

            kv = kv + "_" + seq + "_" + cigar_seq + "_" + std::to_string(brec->flags()) + "_" + std::to_string(brec->start);
            rm_rd_set.insert(kv);
            outfile_discard->write(brec);
            ALN_COUNT_BAD++;
            free(seq);
            free(cigar_seq);
        } else {
            outfile_cleaned->write(brec);
            ALN_COUNT_GOOD++;
        }
    }
    bam_reader_spliced.bclose();
    GMessage("\n");
    ALN_COUNT_GOOD += ALN_COUNT_NSPLICED;
    GMessage("[INFO] %d spurious alignments were removed.\n", ALN_COUNT_BAD);


    // Writing out auxiliary file 
    std::ofstream NH_tag_f;
    GStr NH_tag_fname = out_dir + "/NH_tag_fix.csv";
    NH_tag_f.open(NH_tag_fname.chars());   
    for (auto ele : rm_rd_hm) {
        NH_tag_f << ele.first << ","  << ele.second  << std::endl;
    }
    NH_tag_f.close();

    return outfname_spliced_good;
}