#ifndef _JUNC_FUNC_H
#define _JUNC_FUNC_H

#include <iostream>
#include <cstdlib>
#include <vector>
#include <gclib/GStr.h>
#include <string>

#include "common.h"
#include "GSam.h"
#include "junc.h"

extern int juncCount;
extern GArray<CJunc> junctions;

void addJunction(GSamRecord& r, int dupcount, GStr ref);

void writeJuncs(FILE* f);

void flushJuncs(FILE* f);

#endif