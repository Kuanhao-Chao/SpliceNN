#include "extract.h"
#include "common.h"
#include "extract.h"
#include "junc_func.h"
#include "util.h"
#include <filesystem>
#include <iostream>
#include <unordered_map>
#include <gclib/GBase.h>

void splamJExtract() {
    int num_samples=in_records.start();
    GMessage("[INFO] Extracting junctions ...\n");
    GMessage("[INFO] Number of samples\t: %d\n", num_samples);
    GMessage("[INFO] Output directory\t\t: %s\n", out_dir.chars());
    GMessage("[INFO] Output Junction file\t: %s\n", outfname_junction.chars());

    //  Creating directories for bed & fasta files.
    // GStr bed_dir(out_dir+"/bed");
    // std::filesystem::create_directories(bed_dir.chars());

    std::unordered_map<std::string, int> chrs = get_hg38_chrom_size("HISAT2");

    // Creating the output junction bed file
    if (!outfname_junction.is_empty()) {
        if (strcmp(outfname_junction.substr(outfname_junction.length()-4, 4).chars(), ".bed")!=0) {
            outfname_junction.append(".bed");
        }
        joutf = fopen(outfname_junction.chars(), "w");
        if (joutf==NULL) GError("Error creating file %s\n", outfname_junction.chars());
        // fprintf(joutf, "track name=junctions\n");
    }

    // Reading BAM file.
    int counter = 0;
    int prev_tid=-1;
    GStr prev_refname;
    GVec<uint64_t> bcov(2048*1024);
    std::vector<std::pair<float,uint64_t>> bsam(2048*1024,{0,1}); // number of samples. 1st - current average; 2nd - total number of values
    int b_end=0;
    int b_start=0;

    while ((irec=in_records.next())!=NULL) {
        brec=irec->brec;
        uint32_t dupcount=0;
        std::vector<int> cur_samples;
        int endpos=brec->end;

        // std::cout << brec->refId() << std::endl;
        // printf(">> %s \n", brec->refId());
        if (brec->refId()!=prev_tid || (int)brec->start>b_end) {
            if (joutf) {
                flushJuncs(joutf);
            } // TODO: write the last column to 3 dec places
            b_start=brec->start;
            b_end=endpos;
            prev_tid=brec->refId();
            prev_refname=(char*)brec->refName();
        } else { //extending current bundle
            if (b_end<endpos) {
                b_end=endpos;
                bcov.setCount(b_end-b_start+1, (int)0);
            }
        }
        int accYC = 0;
        accYC = brec->tag_int("YC", 1);
        if (joutf && brec->exons.Count()>1) {
            addJunction(*brec, accYC, prev_refname);
        }
    }
    flushJuncs(joutf);
    fclose(joutf);

    GMessage("[INFO] SPLAM! Total number of junctions: %d\n", juncCount);	
}
