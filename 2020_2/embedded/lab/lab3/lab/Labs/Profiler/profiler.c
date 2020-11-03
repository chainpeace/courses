#include <stdio.h> 
#include <stdlib.h>
#include <unistd.h>		//close()
#include <malloc.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include "perf_event.h"
#include "profiler.h"
#include <asm/unistd.h>
#include <stdarg.h>
#include <sys/syscall.h>
//-------------------------------------
// Global variables
//-------------------------------------
int g_num_events = 0;
int g_fd_clock;
int g_fd[4] = {0,};
int g_events[MAX_EVENTS];

struct event_info g_event_info_table[50] = 
{
	{RAW, PMNC_SW_INCR, "PMNC_SW_INCR"}, 
	{RAW, IFETCH_MISS, "IFETCH_MISS"}, 
	{RAW, ITLB_MISS, "ITLB_MISS"}, 
	{RAW, DCACHE_REFILL, "DCACHE_REFILL"}, 
	{RAW, DCACHE_ACCESS, "DCACHE_ACCESS"}, 
	{RAW, DTLB_REFILL, "DTLB_REFILL"}, 
	{RAW, DREAD, "DREAD"}, 
	{RAW, DWRITE, "DWRITE"}, 
	{RAW, INSTR_EXECUTED, "INSTR_EXECUTED"}, 
	{RAW, EXC_TAKEN, "EXC_TAKEN"}, 
	{RAW, EXC_EXECUTED, "EXC_EXECUTED"}, 
	{RAW, CID_WRITE, "CID_WRITE"}, 
	{RAW, PC_WRITE, "PC_WRITE"}, 
	{RAW, PC_IMM_BRANCH, "PC_IMM_BRANCH"}, 
	{RAW, PC_PROC_RETURN, "PC_PROC_RETURN"}, 
	{RAW, UNALIGNED_ACCESS, "UNALIGNED_ACCESS"}, 
	{RAW, PC_BRANCH_MIS_PRED, "PC_BRANCH_MIS_PRED"}, 
	{RAW, CPU_CYCLES, "CPU_CYCLES"}, 
	{RAW, PC_BRANCH_MIS_USED, "PC_BRANCH_MIS_USED"}, 
	{RAW, WRITE_BUFFER_FULL, "WRITE_BUFFER_FULL"}, 
	{RAW, L2_STORE_MERGED, "L2_STORE_MERGED"}, 
	{RAW, L2_STORE_BUFF, "L2_STORE_BUFF"}, 
	{RAW, L2_ACCESS, "L2_ACCESS"}, 
	{RAW, L2_CACHE_MISS, "L2_CACHE_MISS"}, 
	{RAW, AXI_READ_CYCLES, "AXI_READ_CYCLES"}, 
	{RAW, AXI_WRITE_CYCLES, "AXI_WRITE_CYCLES"}, 
	{RAW, MEMORY_REPLAY, "MEMORY_REPLAY"}, 
	{RAW, UNALIGNED_ACCESS_REPLAY, "UNALIGNED_ACCESS_REPLAY"}, 
	{RAW, L1_DATA_MISS, "L1_DATA_MISS"}, 
	{RAW, L1_INST_MISS, "L1_INST_MISS"}, 
	{RAW, L1_DATA_COLORING, "L1_DATA_COLORING"}, 
	{RAW, L1_NEON_DATA, "L1_NEON_DATA"}, 
	{RAW, L1_NEON_CACH_DATA, "L1_NEON_CACH_DATA"}, 
	{RAW, L2_NEON, "L2_NEON"}, 
	{RAW, L2_NEON_HIT, "L2_NEON_HIT"}, 
	{RAW, L1_INST, "L1_INST"}, 
	{RAW, PC_RETURN_MIS_PRED, "PC_RETURN_MIS_PRED"}, 
	{RAW, PC_BRANCH_FAILED, "PC_BRANCH_FAILED"}, 
	{RAW, PC_BRANCH_TAKEN, "PC_BRANCH_TAKEN"}, 
	{RAW, PC_BRANCH_EXECUTED, "PC_BRANCH_EXECUTED"}, 
	{RAW, OP_EXECUTED, "OP_EXECUTED"}, 
	{RAW, CYCLES_INST_STALL, "CYCLES_INST_STALL"}, 
	{RAW, CYCLES_INST, "CYCLES_INST"}, 
	{RAW, CYCLES_NEON_DATA_STALL, "CYCLES_NEON_DATA_STALL"}, 
	{RAW, CYCLES_NEON_INST_STALL, "CYCLES_NEON_INST_STALL"}, 
	{RAW, NEON_CYCLES, "NEON_CYCLES"}, 
	{RAW, PMU0_EVENTS, "PMU0_EVENTS"}, 
	{RAW, PMU1_EVENTS, "PMU1_EVENTS"}, 
	{RAW, PMU_EVENTS, "PMU_EVENTS"},
	{-1, -1, NULL}
};

//-------------------------------------
//
// Function: perf_event_open()
//
//-------------------------------------
static long perf_event_open(struct perf_event_attr *hw_event, pid_t pid, int cpu, int group_fd, unsigned long flags)
{
	int ret;

	ret = syscall(__NR_perf_event_open, hw_event, pid, cpu, group_fd, flags);
	return ret;
}

static long perf_ioctl(int fd, unsigned long cmd, unsigned long arg)
{
	int ret;
	if ((ret = ioctl(fd, cmd, arg)) < 0) {
		switch (cmd) {
			case PERF_EVENT_IOC_ENABLE:
				printf("[%s] Can not enable counter\n", PREFIX);
				exit(EXIT_FAILURE);
			case PERF_EVENT_IOC_DISABLE:
				printf("[%s] Can not disable counter\n", PREFIX);
				exit(EXIT_FAILURE);
			case PERF_EVENT_IOC_RESET:
				printf("[%s] Can not reset counter\n", PREFIX);
				exit(EXIT_FAILURE);
			default:
				printf("[%s] Unknown ioctl error\n", PREFIX);
				exit(EXIT_FAILURE);
		}
	}
	return ret;
}

//-------------------------------------
//
// Function: check_error()
//
//-------------------------------------
int check_error()
{
	int i;
	for (i = 0; i < g_num_events; i++) {
		if (g_fd[i]== 0)
		{
			printf ("[%s] Perf event not open\n", PREFIX);
			exit(EXIT_FAILURE);
		}
	}

	if (g_num_events == 0)
	{
		printf ("[%s] Specify at least one PMU event\n", PREFIX);
		exit(EXIT_FAILURE);
	}

	return 1;
}

//-------------------------------------
//
// Function: pmu_info *get_pmu_info(int ev) 
//
//-------------------------------------
struct event_info *get_event_info(int ev)
{
	int i;
	for (i=0; g_event_info_table[i].config != -1; i++) {
		if (g_event_info_table[i].config == ev)
			return &g_event_info_table[i];
	}	

	return NULL;
}

//-------------------------------------
//
// Function: init_monitoring(int ev)
//
//-------------------------------------
int init_monitoring(int num_events, ...)
{
	struct event_info *event = NULL;
	struct perf_event_attr pe;
    va_list list;
    int ev;
    
    //add cpu clock event
	int i = 0;

	memset(&pe, 0, sizeof(struct perf_event_attr));
	pe.type = PERF_TYPE_SOFTWARE;
	pe.size = sizeof(struct perf_event_attr);
	pe.config = PERF_COUNT_SW_CPU_CLOCK;
	pe.disabled = 1;

	g_fd_clock = perf_event_open(&pe, 0, -1, -1, 0);

	if (g_fd_clock < 0) {
		printf ("[%s] perf_event_open() failed\n", PREFIX);
		exit(EXIT_FAILURE);
	}
    
    
	if (g_num_events + num_events > MAX_EVENTS)
	{
		printf ("[%s] Cannot add events more than four\n", PREFIX);
		exit(EXIT_FAILURE);
	}
    



    va_start(list, num_events);

    for (i = 0 ; i < num_events ; i++) 
    {     
        ev = va_arg(list, int);
        event = get_event_info(ev);
        if (event == NULL)
        {
            printf ("[%s] Invalid event: %d\n", PREFIX, ev);
            exit(EXIT_FAILURE);
        }

        memset(&pe, 0, sizeof(struct perf_event_attr));
        pe.type = event->type;
        pe.size = sizeof(struct perf_event_attr);
        pe.config = event->config;
        pe.disabled = 1;

        g_fd[g_num_events] = perf_event_open(&pe, 0, -1, -1, 0);


        if (g_fd[g_num_events] < 0) {
            printf ("[%s] perf_event_open() failed\n", PREFIX);
			exit(EXIT_FAILURE);
        }
        g_events[g_num_events++] = ev;
    }
    va_end(list);

	return 1;
}

//-------------------------------------
//
// Function: start_monitoring()
//
//-------------------------------------
int start_monitoring()
{
	int i;

	check_error();

	perf_ioctl(g_fd_clock, PERF_EVENT_IOC_RESET, 0);
	perf_ioctl(g_fd_clock, PERF_EVENT_IOC_ENABLE, 0);
	for (i = 0; i < g_num_events; i++) {
		perf_ioctl(g_fd[i], PERF_EVENT_IOC_RESET, 0);
		perf_ioctl(g_fd[i], PERF_EVENT_IOC_ENABLE,0);
	}

	return 1;
}

//-------------------------------------
//
// Function: end_monitoring()
//
//-------------------------------------
int end_monitoring()
{
	int i;

	check_error();

	perf_ioctl(g_fd_clock, PERF_EVENT_IOC_DISABLE, 0);
	for (i = 0; i < g_num_events; i++) {
		perf_ioctl(g_fd[i], PERF_EVENT_IOC_DISABLE, 0);
	}

	return 1;
}

//-------------------------------------
//
// Function: print_monitored_values()
//
//-------------------------------------
int print_monitored_values()
{
	u64 ccnt;
	u64 value = 0;
	struct event_info *event;
	int i;

	check_error();

	printf ("[%s] Profiling Results...\n", PREFIX);

	read(g_fd_clock, &ccnt, sizeof(u64));	
	printf("\t%s: %llu\n", "cpu-clock", ccnt);

	for (i = 0; i < g_num_events; i++)
	{
		event = get_event_info(g_events[i]);
		if (!event) {
			printf("[%s] Invalid event: %d\n", PREFIX, g_events[i]);
			exit(EXIT_FAILURE);
		}
		read(g_fd[i], &value, sizeof(u64)); 
		printf("\tPMU[%d] (%s): %llu\n", i, event->name, value);
	}

	return 1;
}

//-------------------------------------
//
// Function: release_monitoring()
//
//-------------------------------------
int release_monitoring()
{
	int i;
	
	check_error();

	close(g_fd_clock);
	for (i = 0; i < g_num_events; i++) {
		close(g_fd[i]);
	}

	printf ("[%s] Profiler released...\n", PREFIX);

	return 1;
}

