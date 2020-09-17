#!/usr/bin/python

from bcc import BPF
from time import strftime

# define BPF program
bpf_text = """
#include <uapi/linux/ptrace.h>
#include <linux/sched.h>

struct data_t {
    u32 pid;
    u64 delta;
    char comm[TASK_COMM_LEN];
};

BPF_HASH(start, struct task_struct *);
BPF_PERF_OUTPUT(events);

void kprobe__io_schedule(struct pt_regs *ctx)
{
    struct task_struct * curr = (struct task_struct *)bpf_get_current_task();

    u64 time = bpf_ktime_get_ns();
    
    start.update(&curr, &time);
    //events.perf_submit(ctx, &data, sizeof(data));
}
int kretprobe__io_schedule(struct pt_regs *ctx)
{
    struct data_t data = {};
    u64 *timep, delta;
    struct task_struct * curr = (struct task_struct *)bpf_get_current_task();

    u32 pid = bpf_get_current_pid_tgid() >> 32;
    data.pid = pid;
    bpf_get_current_comm(&data.comm, sizeof(data.comm));

    timep = start.lookup(&curr);
    if(timep == 0)
        return 0;

    delta = (bpf_ktime_get_ns() - *timep);
    start.delete(&curr);
    data.delta = delta;

    events.perf_submit(ctx, &data, sizeof(data));

    return 0;
}
"""

# process event
def print_event(cpu, data, size):
    event = b["events"].event(data)

    print("%-11s %-14s %-6s %-7s" % (strftime("%H:%M:%S"), 
        event.comm.decode('utf-8', 'replace'), event.pid, event.delta))

# initialize BPF
b = BPF(text=bpf_text)
print("%-11s %-14s %-6s %-7s" % ("TIME", "COMM", "PID",
     "DELTA(ns)"))
b["events"].open_perf_buffer(print_event)
while 1:
    try:
        b.perf_buffer_poll()
    except KeyboardInterrupt:
        exit()
