#include "util.h"

#include "junc.h"
#include "common.h"
#include <string>
#include <iostream>
#include <htslib/htslib/hts.h>
#include <unordered_map>
#include <fstream>
#include <sstream>

std::string get_full_path(std::string fname){
    const char *cur_path = fname.c_str();
    char *actualpath;


    actualpath = realpath(cur_path, NULL);
    if (actualpath != NULL){
        return std::string(actualpath);
        free(actualpath);
    }
    else{
        std::cerr<<"could not resolve path: "<<fname<<std::endl;
        exit(-1);
    }
}

static unsigned char comp_base[256] = {
  0,   1,   2,   3,   4,   5,   6,   7,   8,   9,  10,  11,  12,  13,  14,  15,
 16,  17,  18,  19,  20,  21,  22,  23,  24,  25,  26,  27,  28,  29,  30,  31,
 32, '!', '"', '#', '$', '%', '&', '\'','(', ')', '*', '+', ',', '-', '.', '/',
'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ':', ';', '<', '=', '>', '?',
'@', 'T', 'V', 'G', 'H', 'E', 'F', 'C', 'D', 'I', 'J', 'M', 'L', 'K', 'N', 'O',
'P', 'Q', 'Y', 'S', 'A', 'A', 'B', 'W', 'X', 'R', 'Z', '[', '\\',']', '^', '_',
'`', 't', 'v', 'g', 'h', 'e', 'f', 'c', 'd', 'i', 'j', 'm', 'l', 'k', 'n', 'o',
'p', 'q', 'y', 's', 'a', 'a', 'b', 'w', 'x', 'r', 'z', '{', '|', '}', '~', 127,
128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143,
144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159,
160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175,
176, 177, 178, 179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191,
192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207,
208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223,
224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239,
240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255,
};

void reverse_complement(char *str, const hts_pos_t len) {
    char c;
    hts_pos_t i = 0, j = len - 1;

    while (i <= j) {
        c = str[i];
        str[i] = comp_base[(unsigned char)str[j]];
        str[j] = comp_base[(unsigned char)c];
        i++;
        j--;
    }
}











wchar_t *GetWC(const char *c)
{
    const size_t cSize = strlen(c)+1;
    wchar_t* wc = new wchar_t[cSize];
    mbstowcs (wc, c, cSize);

    return wc;
}
int usage(){ 
    // GMessage("splam v{}\n\n", VERSION);

    if (COMMAND_MODE == J_EXTRACT) {
        GMessage(
        "Usage:  splam j-extract [arguments] BAM-file(s) \n\n");
        GMessage(
        "Required argument:\n"
        "\t-r / --ref\t\tPath to the reference file (FASTA)\n"
        "\t-o / --output\t\tPath to the output directory\n\n"
        );

    } else if (COMMAND_MODE == PREDICT) {
        GMessage(
        "Usage:  splam predict [arguments] Junction-BED-file \n\n");
        GMessage(
        "Required argument:\n"
        // "\t-j / --junction\t\tPath to the splice junctions file (BED)\n"
        "\t-m / --model\t\tPath to the SPLAM model (PT)\n"
        "\t-r / --ref\t\tPath to the reference file (FASTA)\n"
        "\t-o / --output\t\tPath to the output directory\n\n"
        );
        // GMessage(
        // "Optional argument:\n");

    } else if (COMMAND_MODE == CLEAN) {
        GMessage(
        "Usage:  splam clean [arguments] BAM-file \n\n");
        GMessage(
        "Required argument:\n"
        // "\t-b / --bam\t\tPath to the alignment file (BAM)\n"
        "\t-m / --model\t\tPath to the SPLAM model (PT)\n"
        "\t-r / --ref\t\tPath to the reference file (FASTA)\n"
        "\t-o / --output\t\tPath to the output directory\n\n"
        );
        // GMessage(
        // "Optional argument:\n");
    } else {
        GMessage(
        "Usage:  splam -h|--help or \n"
        "        splam -v|--version or \n"
        "        splam -c|--cite or \n"
        "        splam <COMMAND> [-h | options]\n\n");
        GMessage("Commands:\n");
        GMessage("     j-extract    : extract junctions from a BAM file / a list of BAM files.\n");
        GMessage("     predict      : score junctions\n");
        GMessage("     clean        : clean up a BAM file\n");
    }


//   std::cout << helpMsg.str();
  return 0;
}

std::unordered_map<std::string, int> get_hg38_chrom_size(std::string target) {
    std::unordered_map<std::string, int> chrs;
    std::string ref_file;
    if (target == "STAR") {
        ref_file = "./hg38_chrom_size_refseq.tsv";
    } else {
        ref_file = "./hg38_chrom_size.tsv";
    }
    std::ifstream ref_f(ref_file);
    std::string line;
    while(getline(ref_f, line)){
        std::string chromosome;
        int len;
        std::replace(line.begin(), line.end(), '\t', ' ');
        std::stringstream ss(line);
        ss >> chromosome;
        ss >> len;
        chrs[chromosome] = len;
    }   
    // for (auto i : chrs) {
    //   std::cout << i.first << " ---- " << i.second << std::endl;
    // }
    return chrs;
}



void flushBrec(GVec<GSamRecord*> &pbrecs, std::unordered_map<std::string, int> &hits, GSamWriter* outfile_cleaned) {
    if (pbrecs.Count()==0) return;
    for (int i=0; i < pbrecs.Count(); i++) {
        std::string kv = pbrecs[i]->name();

        std::cout << "kv: " << kv << std::endl;
        std::string tmp = std::to_string(pbrecs[i]->pairOrder());
        kv += ";";
        kv += tmp;
        if (hits.find(kv) != hits.end()) {
            std::cout << "Update NH tage!!" << std::endl;
            int new_nh = pbrecs[i]->tag_int("NH", 0) - hits[kv];
            pbrecs[i]->add_int_tag("NH", new_nh);
        }
// using GArray
//        CRead tmp(pbrecs[i]->pairOrder(), pbrecs[i]->name());
//        int idx;
//        if (spur_reads.Found(tmp, idx)) {
//            int new_nh = pbrecs[i]->tag_int("NH", 0) - spur_reads[idx].spurCnt;
//            pbrecs[i]->add_int_tag("NH", new_nh);
//        }
// for testing
       if (!strcmp(pbrecs[i]->name(), "ERR188044.24337229")) {
           std::cout << pbrecs[i]->tag_int("NH", 0) << std::endl;
       }
        outfile_cleaned->write(pbrecs[i]);
    }
}