#ifndef PROFILER_H
#define PROFILER_H
#include "perf_event.h"

//-------------------------------------
// Macros
//-------------------------------------
#define u64				unsigned long long
#define u32				unsigned int
#define HW				PERF_TYPE_HARDWARE
#define SW				PERF_TYPE_SOFTWARE
#define RAW				PERF_TYPE_RAW
#define CACHE			PERF_TYPE_HW_CACHE
#define PCHW(x)			PERF_COUNT_HW_##x
#define PCSW(x)			PERF_COUNT_SW_##x
#define C(x)			PERF_COUNT_HW_CACHE_##x
#define OP(x)			PERF_COUNT_HW_CACHE_OP_##x
#define R(x)			PERF_COUNT_HW_CACHE_RESULT_##x
#define PCC(c,op,r)		((c) | ((op) << 8) | ((r) << 16))
#define PF(x)			PERF_FORMAT_##x
#define MAX_EVENTS      4
#define PREFIX			"PROFILER"
#define __NR_perf_event_open	364

//-------------------------------------
// Struct: event_info
//-------------------------------------
struct event_info {
	u32 type;
	u64 config;
	char *name;
};


extern struct event_info g_event_info_table[50];
extern int g_num_events;
extern int g_events[MAX_EVENTS];

//-------------------------------------
// PMU Events
//-------------------------------------

#define        PMNC_SW_INCR       			0x00
#define        IFETCH_MISS        			0x01
#define        ITLB_MISS        			0x02
#define        DCACHE_REFILL         		0x03
#define        DCACHE_ACCESS         		0x04
#define        DTLB_REFILL         			0x05
#define        DREAD         				0x06
#define        DWRITE         				0x07
#define        INSTR_EXECUTED         		0x08
#define        EXC_TAKEN         			0x09
#define        EXC_EXECUTED         		0x0A
#define        CID_WRITE        			0x0B
#define        PC_WRITE         			0x0C
#define        PC_IMM_BRANCH         		0x0D
#define        PC_PROC_RETURN         		0x0E
#define        UNALIGNED_ACCESS         	0x0F
#define        PC_BRANCH_MIS_PRED         	0x10
#define        CPU_CYCLES         			0x11
#define        PC_BRANCH_MIS_USED         	0x12
#define        WRITE_BUFFER_FULL         	0x40
#define        L2_STORE_MERGED         		0x41
#define        L2_STORE_BUFF         		0x42
#define        L2_ACCESS         			0x43
#define        L2_CACHE_MISS         		0x44
#define        AXI_READ_CYCLES         		0x45
#define        AXI_WRITE_CYCLES         	0x46
#define        MEMORY_REPLAY         		0x47
#define        UNALIGNED_ACCESS_REPLAY      0x48
#define        L1_DATA_MISS         		0x49
#define        L1_INST_MISS         		0x4A
#define        L1_DATA_COLORING         	0x4B
#define        L1_NEON_DATA         		0x4C
#define        L1_NEON_CACH_DATA         	0x4D
#define        L2_NEON         				0x4E
#define        L2_NEON_HIT         			0x4F
#define        L1_INST         				0x50
#define        PC_RETURN_MIS_PRED         	0x51
#define        PC_BRANCH_FAILED         	0x52
#define        PC_BRANCH_TAKEN         		0x53
#define        PC_BRANCH_EXECUTED         	0x54
#define        OP_EXECUTED         			0x55
#define        CYCLES_INST_STALL         	0x56
#define        CYCLES_INST         			0x57
#define        CYCLES_NEON_DATA_STALL       0x58
#define        CYCLES_NEON_INST_STALL       0x59
#define        NEON_CYCLES         			0x5A
#define        PMU0_EVENTS        			0x70
#define        PMU1_EVENTS         			0x71
#define        PMU_EVENTS         			0x72
//-------------------------------------
// Functions
//-------------------------------------
int init_monitoring(int num_events, ...);
int start_monitoring();
int end_monitoring();
int print_monitored_values();
int release_monitoring();

#endif
