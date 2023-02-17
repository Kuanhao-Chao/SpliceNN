#ifndef _COMMON_H_
#define _COMMON_H_

#include "var.h"
#include "tmerge.h"
#include <gclib/GStr.h>

extern TInputFiles in_records;
extern TInputRecord* irec;

extern CommandMode COMMAND_MODE;

extern GStr infname_model_name;
extern GStr infname_reffa;
extern GStr infname_bam;

extern GStr out_dir;
extern GStr outfname_junction;

extern bool verbose;
extern float threshold;

extern GSamRecord* brec;
extern GSamWriter* outfile_discard;
extern GSamWriter* outfile_spliced;
extern GSamWriter* outfile_cleaned;
extern FILE* joutf;

#endif /* TIEBRUSH_TMERGE_H_ */