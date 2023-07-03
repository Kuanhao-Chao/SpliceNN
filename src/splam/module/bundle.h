/*  bundle.h -- 

    Copyright (C) 2023 Kuan-Hao Chao

    Author: Kuan-Hao Chao <kuanhao.chao@gmail.com> */
#ifndef _BUNDLE_H_
#define _BUNDLE_H_

#include "gclib/GStr.h"
#include "gclib/GList.hh"
#include "GSam.h"

struct CReadAln:public GSeg {
	//DEBUG ONLY:
	GSamRecord brec;
	int pair_idx;     // keeps index for the pair of the alignment.
	// GVec<GSeg> segs; //"exons"

	CReadAln(GSamRecord* bamrec): 
			GSeg(bamrec->start, bamrec->end), brec(NULL), pair_idx(-1) {
		this->brec = (*bamrec);
	}
	
	// CReadAln(CReadAln &rd):GSeg(rd.start,rd.end) { // copy contructor
	// 	pair_idx=rd.pair_idx;
	// 	GSamRecord brec_tmp = GSamRecord(rd.brec);
	// 	brec = &brec_tmp;
	// }

	~CReadAln() { 
		// GMessage("CReadAln destructor called\n");
		// delete brec;
	}
};

// bundle data structure, holds all data needed for
// infering transcripts from a bundle
enum BundleStatus {
	BUNDLE_STATUS_CLEAR=0, //available for loading/prepping
	BUNDLE_STATUS_LOADING, //being prepared by the main thread (there can be only one)
	BUNDLE_STATUS_READY //ready to be processed, or being processed
};

// bundle data structure, holds all input data parsed from BAM file
struct BundleData {
	BundleStatus status;
	int idx; //index in the main bundles array
	int start;
	int end;
	GStr refseq; //reference sequence name

	BundleData():status(BUNDLE_STATUS_CLEAR), idx(0), start(0), end(0), refseq() {
	}

	void getReady(int currentstart, int currentend) {
		//this is only called when the bundle is valid and ready to be processed
		start=currentstart;
		end=currentend;
		//tag all these guides
		status=BUNDLE_STATUS_READY;
	}

	void Clear() {
		start=0;
		end=0;
		status=BUNDLE_STATUS_CLEAR;
	}

	~BundleData() {
		Clear();
	}
};


#endif