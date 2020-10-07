#!/usr/bin/python

#
# Tool for tracking page fault delay
#

from bcc import BPF
from time import sleep, strftime
import signal
# import argparse


# signal handler
def signal_ignore(signal, frame):
    print()

bpf_text = """
#include <uapi/linux/ptrace.h>
#include <linux/mm.h>
#include <asm/page_types.h>

struct data_t {
    u32 pid;
    u64 delay;  // from prev probe to now
    u64 address;
    char comm[TASK_COMM_LEN];
    char func_stat[30];
};
struct entry_t{
    u64 prev_page;
};

BPF_HASH(delay, struct task_struct *); //for delay time
BPF_HASH(entry, struct task_struct *, struct entry_t); //for io flow
BPF_PERF_OUTPUT(events);

//trace handle_mm_fault
void kprobe__handle_mm_fault(struct pt_regs *ctx, struct vm_area_struct *vma, 
    unsigned long address,unsigned int flags){

    struct data_t data = {.func_stat = "handle_mm_fault start"};
    struct entry_t *val, zero = {};
    struct task_struct * curr = (struct task_struct *)bpf_get_current_task();
    
    u64 page_address = address & PAGE_MASK;
    
    //get process info
    u32 pid = bpf_get_current_pid_tgid() >> 32;
    data.pid = pid;
    bpf_get_current_comm(&data.comm, sizeof(data.comm));
    
    data.address = page_address;
    data.delay = 0;
    
    u64 time = bpf_ktime_get_ns();
    
    val = entry.lookup_or_try_init(&curr, &zero);
    if(val == 0)
        return;
    if(val->prev_page != page_address){
        
        zero.prev_page = page_address;
        delay.update(&curr, &time);
        entry.update(&curr, &zero);

    } else{
        u64 *delayp;

        delayp = delay.lookup(&curr);

        if(delayp == 0)
            return;

        data.delay = time - *delayp;
        delay.update(&curr, &time);
    }

    events.perf_submit(ctx, &data, sizeof(data));
}

int kretprobe__handle_mm_fault(struct pt_regs *ctx){

    struct data_t data = {.func_stat = "handle_mm_fault finish"};
    u64 *delayp, time;

    struct task_struct * curr = (struct task_struct *)bpf_get_current_task();

    //get process info
    u32 pid = bpf_get_current_pid_tgid() >> 32;
    data.pid = pid;
    bpf_get_current_comm(&data.comm, sizeof(data.comm));

    //calulate delta
    time = bpf_ktime_get_ns();
    delayp = delay.lookup(&curr);

    if(delayp == 0)
        return 0;

    data.delay = time - *delayp;
  
    events.perf_submit(ctx, &data, sizeof(data));
    return 0;

}

//trace filemap_fault
void kprobe__filemap_fault(struct pt_regs *ctx, struct vm_fault *vmf){

    struct data_t data = {.func_stat = "filemap_fault start"};
    u64 *delayp, time;

    //get process info
    u32 pid = bpf_get_current_pid_tgid() >> 32;
    data.pid = pid;
    bpf_get_current_comm(&data.comm, sizeof(data.comm));
    
    data.address = vmf->address;
    
    struct task_struct * curr = (struct task_struct *)bpf_get_current_task();
    
    //calulate delta
    time = bpf_ktime_get_ns();
    delayp = delay.lookup(&curr);

    if(delayp == 0)
        return;

    data.delay = time - *delayp;
    delay.update(&curr, &time);

    events.perf_submit(ctx, &data, sizeof(data));
}

int kretprobe__filemap_fault(struct pt_regs *ctx){

    struct data_t data = {.func_stat = "filemap_fault finish"};
    u64 *delayp, time;

    struct task_struct * curr = (struct task_struct *)bpf_get_current_task();

    //get process info
    u32 pid = bpf_get_current_pid_tgid() >> 32;
    data.pid = pid;
    bpf_get_current_comm(&data.comm, sizeof(data.comm));

    //calulate delta
    time = bpf_ktime_get_ns();
    delayp = delay.lookup(&curr);

    if(delayp == 0)
        return 0;

    data.delay = time - *delayp;
    delay.update(&curr, &time);
    
    events.perf_submit(ctx, &data, sizeof(data));
    return 0;
}
void kprobe__blk_start_plug(struct pt_regs *ctx, struct blk_plug *plug){

    struct data_t data = {.func_stat = "blk_start_plug"};
    u64 *delayp, time;

    struct task_struct * curr = (struct task_struct *)bpf_get_current_task();

    //get process info
    u32 pid = bpf_get_current_pid_tgid() >> 32;
    data.pid = pid;
    bpf_get_current_comm(&data.comm, sizeof(data.comm));

    //calulate delta
    time = bpf_ktime_get_ns();
    delayp = delay.lookup(&curr);

    if(delayp == 0)
        return;

    data.delay = time - *delayp;
    delay.update(&curr, &time);
    
    events.perf_submit(ctx, &data, sizeof(data));
}
void kprobe__submit_bio(struct pt_regs *ctx, struct bio *bio){

    struct data_t data = {.func_stat = "submit_bio"};
    u64 *delayp, time;

    struct task_struct * curr = (struct task_struct *)bpf_get_current_task();

    //get process info
    u32 pid = bpf_get_current_pid_tgid() >> 32;
    data.pid = pid;
    bpf_get_current_comm(&data.comm, sizeof(data.comm));

    //calulate delta
    time = bpf_ktime_get_ns();
    delayp = delay.lookup(&curr);

    if(delayp == 0)
        return;

    data.delay = time - *delayp;
    delay.update(&curr, &time);
    
    events.perf_submit(ctx, &data, sizeof(data));
}

void kprobe__blk_finish_plug(struct pt_regs *ctx, struct blk_plug *plug){

    struct data_t data = {.func_stat = "blk_finish_plug"};
    u64 *delayp, time;

    struct task_struct * curr = (struct task_struct *)bpf_get_current_task();

    //get process info
    u32 pid = bpf_get_current_pid_tgid() >> 32;
    data.pid = pid;
    bpf_get_current_comm(&data.comm, sizeof(data.comm));

    //calulate delta
    time = bpf_ktime_get_ns();
    delayp = delay.lookup(&curr);

    if(delayp == 0)
        return;

    data.delay = time - *delayp;
    delay.update(&curr, &time);
    
    events.perf_submit(ctx, &data, sizeof(data));
}



//trace io_schedule
void kprobe__io_schedule(struct pt_regs *ctx)
{
struct data_t data = {.func_stat = "io_schedule start"};
    u64 *delayp, time;

    struct task_struct * curr = (struct task_struct *)bpf_get_current_task();

    //get process info
    u32 pid = bpf_get_current_pid_tgid() >> 32;
    data.pid = pid;
    bpf_get_current_comm(&data.comm, sizeof(data.comm));

    //calulate delta
    time = bpf_ktime_get_ns();
    delayp = delay.lookup(&curr);

    if(delayp == 0)
        return;

    data.delay = time - *delayp;
    delay.update(&curr, &time);
    
    events.perf_submit(ctx, &data, sizeof(data));
}

int kretprobe__io_schedule(struct pt_regs *ctx)
{
    struct data_t data = {.func_stat = "io_schedule finish"};
    u64 *delayp, time;

    struct task_struct * curr = (struct task_struct *)bpf_get_current_task();

    //get process info
    u32 pid = bpf_get_current_pid_tgid() >> 32;
    data.pid = pid;
    bpf_get_current_comm(&data.comm, sizeof(data.comm));

    //calulate delta
    time = bpf_ktime_get_ns();
    delayp = delay.lookup(&curr);

    if(delayp == 0)
        return 0;

    data.delay = time - *delayp;
    delay.update(&curr, &time);
    
    events.perf_submit(ctx, &data, sizeof(data));

    return 0;
}
"""

# filter comm
bpf = BPF(text=bpf_text)

def print_event(cpu, data, size):
    event = bpf["events"].event(data)

    print("%-11s %-14s %-6s %-7s %-30s %-10x" % (strftime("%H:%M:%S"), 
        event.comm.decode('utf-8', 'replace'), event.pid, event.delay, 
        event.func_stat.decode('utf-8', 'replace'), event.address))

print("%-11s %-14s %-6s %-7s %-30s %-10s" % ("TIME", "COMM", "PID",
     "DELAY", "STATUS", "address"))

bpf["events"].open_perf_buffer(print_event)
while 1:
    try:
        bpf.perf_buffer_poll()
    except KeyboardInterrupt:
        exit()
