/*
 * Copyright (C) 2004-2021 Intel Corporation.
 * SPDX-License-Identifier: MIT
 */
 
// ADAPTED FROM proccount.cpp example
//
// This tool counts the number of times a routine is executed and
// the number of instructions executed in a routine
//
 
#include <cstdlib>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <string.h>
#include <vector>
#include "pin.H"
#include "xed-iformfl-enum.h"
using std::cerr;
using std::dec;
using std::endl;
using std::hex;
using std::ofstream;
using std::setw;
using std::string;
using std::vector;
 
ofstream outFile;
ofstream traceFile;
 
// Holds instruction count for a single procedure
typedef struct RtnCount
{
    string _name;
    string _image;
    ADDRINT _address;
    RTN _rtn;
    UINT64 _rtnCount;
    struct RtnCount* _next;
} RTN_COUNT;
 
// Linked list of instruction counts for each routine
RTN_COUNT* RtnList = 0;

std::vector<UINT32> handler_idx_trace;
 
// This function is called before every instruction is executed
VOID docount(UINT64* counter) { (*counter)++; }

UINT32 fn_name_to_handler_idx(const char* str) {
    // str is always "vm_aluXXX_rrr_generated" or "vm_alu1_rrr"
    // skip vm_alu prefix
    str += 6;
    UINT32 value = 0;
    // convert alu number by finding '_' char and c
    size_t len = strchr(str, '_') - str;
    switch(len) {
        case 3: value += (str[len-3] - '0') * 100;
        case 2: value += (str[len-2] - '0') * 10;
        case 1: value += (str[len-1] - '0');
                return value;
        default:
            return 0;
    }
}


VOID rtn_docount(RTN_COUNT* rc) {
    (rc->_rtnCount)++;
    UINT32 handler_idx = fn_name_to_handler_idx(rc->_name.c_str());
    handler_idx_trace.push_back(handler_idx);
}

 
const char* StripPath(const char* path)
{
    const char* file = strrchr(path, '/');
    if (file)
        return file + 1;
    else
        return path;
}
 

// Pin calls this function every time a new rtn is executed
VOID Routine(RTN rtn, VOID* v)
{
    // skip all images != main executable
    if (RTN_Name(rtn).rfind("vm_alu", 0) != 0) {
        return;
    }

    // skip all names
    // Allocate a counter for this routine
    RTN_COUNT* rc = new RTN_COUNT;
 
    // The RTN goes away when the image is unloaded, so save it now
    // because we need it in the fini
    rc->_name     = RTN_Name(rtn);
    // cerr << "Routine: " << rc->_name << endl;
    rc->_image    = StripPath(IMG_Name(SEC_Img(RTN_Sec(rtn))).c_str());
    rc->_address  = RTN_Address(rtn);
    rc->_rtnCount = 0;
 
    // Add to list of routines
    rc->_next = RtnList;
    RtnList   = rc;
 
    RTN_Open(rtn);
 
    // Insert a call at the entry point of a routine to increment the call count
    RTN_InsertCall(rtn, IPOINT_BEFORE, (AFUNPTR)rtn_docount, IARG_PTR, rc, IARG_END);
 
    RTN_Close(rtn);
}
 
// This function is called when the application exits
// It prints the name and count for each procedure
VOID Fini(INT32 code, VOID* v)
{
    outFile << setw(23) << "Procedure"
            << " " << setw(25) << "Image"
            << " " << setw(18) << "Address"
            << " " << setw(12) << "Calls" << endl;
 
    for (RTN_COUNT* rc = RtnList; rc; rc = rc->_next)
    {
        outFile << setw(23) << rc->_name << " " << setw(25) << rc->_image << " " << setw(18) << hex << rc->_address << dec
                << " " << setw(12) << rc->_rtnCount << endl;
    }

    // Print trace
    traceFile << "[";
    if (handler_idx_trace.empty()) {
        traceFile << "]" << endl;
        return;
    }
    traceFile << handler_idx_trace[0];
    for (size_t i = 1; i < handler_idx_trace.size(); ++i) {
        traceFile << ", " << handler_idx_trace[i];
    }
    traceFile << "]" << endl;
}
 
/* ===================================================================== */
/* Print Help Message                                                    */
/* ===================================================================== */
 
INT32 Usage()
{
    cerr << "This Pintool counts the number of times a routine is executed" << endl;
    cerr << "and the number of instructions executed in a routine" << endl;
    cerr << endl << KNOB_BASE::StringKnobSummary() << endl;
    return -1;
}
 
/* ===================================================================== */
/* Main                                                                  */
/* ===================================================================== */
 
int main(int argc, char* argv[])
{
    // Initialize symbol table code, needed for rtn instrumentation
    PIN_InitSymbols();

    outFile.open(getenv("FN_STATS_FILE"));
    traceFile.open(getenv("FN_TRACE_FILE"));
 
    // Initialize pin
    if (PIN_Init(argc, argv)) return Usage();
 
    // Register Routine to be called to instrument rtn
    RTN_AddInstrumentFunction(Routine, 0);
 
    // Register Fini to be called when the application exits
    PIN_AddFiniFunction(Fini, 0);

    handler_idx_trace.reserve(4096);
 
    // Start the program, never returns
    PIN_StartProgram();
 
    return 0;
}
