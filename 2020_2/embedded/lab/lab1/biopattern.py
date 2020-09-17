#!/usr/bin/python

from bcc import BPF
from time import strftime, sleep
import signal

# signal handler
def signal_ignore(signal, frame):
    print()

# load BPF program
bpf_text="""
#include <uapi/linux/ptrace.h>
#include <linux/blk-mq.h>
#include <linux/genhd.h>

struct data_t {

    char disk_name[DISK_NAME_LEN];
    u64 seq_r;
    u64 seq_w;
    u64 rand_r;
    u64 rand_w;
    u64 prev_OP;
    u64 prev_sec;
    u64 prev_len;
    
};
struct e_data_t {

    char disk_name[DISK_NAME_LEN];
    char comm[TASK_COMM_LEN];
    u32 OP;
    u32 seq;
    u64 sector;
    u64 len;

};

BPF_PERF_OUTPUT(events);
BPF_HASH(data, struct gendisk *, struct data_t);

static inline int is_OP_RW(struct request *rq){
    u32 OP;
    OP = (rq->cmd_flags) & REQ_OP_MASK;
    if(OP == REQ_OP_WRITE)
        return 1;
    if(OP == REQ_OP_READ)
        return 0;
    return -1;
}

static inline void set_event_data(struct e_data_t * edata, struct request *rq, u32 seq){
    bpf_probe_read_kernel_str(edata->disk_name, DISK_NAME_LEN, rq->rq_disk->disk_name);
    bpf_get_current_comm(edata->comm, sizeof(edata->comm));
    edata->sector = rq->__sector;
    edata->len = rq->__data_len;
    edata->OP = is_OP_RW(rq);
    edata->seq = seq;

        
}

static inline int is_seq(struct data_t *data, struct request *rq){

    u64 p_sec, sec, p_len, len;

    p_sec = (u64) data->prev_sec;
    sec = (u64) rq->__sector;
    p_len = (u64) data->prev_len;
    len = (u64) rq->__data_len;

    if(p_sec == sec){
        return 1;
    }
    if((p_sec < sec) && (p_sec + p_len/512 >= sec)){
        return 1;
    }
    if((p_sec > sec) && (sec + len/512 >= p_sec)){
        return 1;
    }
    return 0;
}

int count_rq_pattern(struct pt_regs *ctx, struct request *rq)
{
    struct data_t *val, zero = {};
    struct e_data_t edata = {};
    u32 OP, prev_OP, seq;

    struct gendisk *disk = rq->rq_disk;
    if(!disk)
        return -1;

    val = data.lookup_or_try_init(&disk, &zero);
    if(!val)
        return -1;

    bpf_probe_read_kernel_str(val->disk_name, DISK_NAME_LEN, disk->disk_name);
    
    OP = is_OP_RW(rq);
    if(OP != 0 && OP != 1)
        return -1;
    
    if(!val->prev_OP){
        val->prev_sec = rq->__sector;
        val->prev_len = rq->__data_len;
        val->prev_OP = OP;

        if(OP == 1)
            (val->seq_w)++;
        if(OP == 0)
            (val->seq_r)++;

        set_event_data(&edata, rq, 1);      
        events.perf_submit(ctx, &edata, sizeof(edata));

        
        return 0;
    }

    prev_OP = val->prev_OP;
    if(OP != prev_OP){
        if(OP == 1)
            (val->rand_w)++;
        if(OP == 0)
            (val->rand_r)++;
        //val->prev_rq = rq;
        val->prev_sec = rq->__sector;
        val->prev_len = rq->__data_len;
        val->prev_OP = OP;

        set_event_data(&edata, rq, 0);

        events.perf_submit(ctx, &edata, sizeof(edata));
        
        return 0;

    }
    
    seq = is_seq(val, rq);
    if(OP == 1){
        if(seq == 1){
            val->seq_w++;
        } else {
            val->rand_w++;
        }
    }
    if(OP == 0){
        if(seq == 1){
            val->seq_r++;
        } else {
            val->rand_r++;
        }
    }
        
    val->prev_sec = rq->__sector;
    val->prev_len = rq->__data_len;
    val->prev_OP = OP;  

    set_event_data(&edata, rq, seq);

    events.perf_submit(ctx, &edata, sizeof(edata));

    return 0;
}

"""
b = BPF(text=bpf_text)
b.attach_kprobe(event="blk_mq_start_request", fn_name="count_rq_pattern")

# header
print("Tracing... Ctrl-C to end.")

# output
def print_count():
    data = b["data"]
    print("\n%-30s %-10s %-10s %-10s %-10s" % ( 
        "DEV_NAME",  "SEQ_READ", "RAND_READ", 
        "SEQ_WRITE", "RAND_WRITE"))
    for k, v in data.items():
        print("%-30s %-10s %-10s %-10s %-10s" 
            % ( v.disk_name, v.seq_r, v.rand_r, v.seq_w, v.rand_w))
    data.clear()

def print_event(cpu ,data, size):
    event = b["events"].event(data)
    print("%-10s %-30s %-30s %-6s %-5s %-10d %-10d" % (
        strftime("%H:%M:%S"), event.disk_name.decode('utf-8', 'replace'), 
        event.comm.decode('utf-8', 'replace'),
        event.OP == 0 and "read" or "write",
        event.seq == 1 and "SEQ" or "RAND", 
        event.sector, event.len))

b["events"].open_perf_buffer(print_event)
print("\n%-10s %-30s %-30s %-6s %-5s %-10s %-10s" % ("TIME", "DEV_NAME", "PROCESS", 
    "OP", "MODE", "SECTOR", "LEN"))
while True:
    try:
        b.perf_buffer_poll()
    except KeyboardInterrupt:
        signal.signal(signal.SIGINT, signal_ignore)
        print_count()
        exit()
    
