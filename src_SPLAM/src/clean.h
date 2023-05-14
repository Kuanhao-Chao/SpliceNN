#ifndef _CLEAN_H_
#define _CLEAN_H_

#include <gclib/GStr.h>
#include <gclib/GHashMap.hh>
#include "junc.h"
#include "bundle.h"
#include "common.h"
#include <robin_hood/robin_hood.h>
#include <string>
#include <unordered_set>

GStr splamClean();
GStr filterSpurJuncs(GStr outfname_junc_score);
void loadBed(GStr inbedname, robin_hdd_string &spur_juncs);
void processBundle(BundleData* bundle, GList<CReadAln>& readlist, robin_hdd_string& rm_juncs, robin_hdd_rm_hit& rm_hit, int& bundle_counter);
void processRead(int currentstart, int currentend, GList<CReadAln>& readlist, BundleData& bdata, GHash<int>& hashread, CReadAln* alndata);
void noMoreBundles();
void removeAlignment(GSamWriter* outfile_target, GSamRecord* brec, robin_hdd_rm_hit& rm_hit, bool add_hit);
void removeAlignment_se(GSamWriter* outfile_target, GSamRecord* brec, robin_hdd_rm_hit& rm_hit);
void keepAlignment(GSamWriter* outfile_target, GSamRecord* brec);
GStr writenhHitFile(robin_hdd_rm_hit& rm_hit);
bool alignmentAssessment(GSamRecord* brec, robin_hdd_string &rm_juncs);
// std::string get_global_removed_algns_key(GSamRecord* brec);
std::string get_global_removed_mate_algns_key(GSamRecord* brec);
void update_flag_paired_remove_both(GSamRecord* brec_1, GSamRecord* brec_2);
void update_flag_paired_remove_one(GSamRecord* removed, GSamRecord* kept);
void update_flag_unpair_remove(GSamRecord* removed);
void update_flag_unpair_kept(GSamRecord* kept);
#endif