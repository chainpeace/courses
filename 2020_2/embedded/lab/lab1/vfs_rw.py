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
#include <linux/fs.h>

struct data_t {
    u32 pid;
    char comm[TASK_COMM_LEN];
    u64 cnt_r[8];
    u64 cnt_w[8];
};

BPF_HASH(data, u32, struct data_t);

static inline int trace_common(struct pt_regs *ctx, struct file * file, u32 mode)
{
    struct data_t *val, zero = {};
    u32 pid, index;
    u64 *cnt;

    pid = bpf_get_current_pid_tgid() >> 32;
    val = data.lookup_or_try_init(&pid, &zero);
    if(!val)
        return -1;

    val->pid = pid;
    bpf_get_current_comm(&val->comm, sizeof(val->comm));
    
    struct inode *f_inode = file -> f_inode;
    if(!f_inode) 
        return -1;
    cnt = mode? val->cnt_w : val->cnt_r ;
    
    switch (f_inode->i_mode & S_IFMT){
        case S_IFSOCK:
            cnt[7]++;
            break;
        case S_IFLNK:
            cnt[6]++;
            break;
        case S_IFREG:
            cnt[5]++;
            break;
        case S_IFBLK:
            cnt[4]++;
            break;
        case S_IFDIR:
            cnt[3]++;
            break;
        case S_IFCHR:
            cnt[2]++;
            break;
        case S_IFIFO:
            cnt[1]++;
            break;
        default:
            cnt[0]++;
    }
    return 0;
}

int trace_vfsread(struct pt_regs *ctx, struct file * file, 
    char __user *buf, size_t count, loff_t *pos) 
{
    return trace_common(ctx, file, 0);
}
int trace_vfsreadv(struct pt_regs *ctx, struct file *file,
    const struct iovec __user *vec, unsigned long vlen, loff_t *pos, 
    rwf_t flags)
{
    return trace_common(ctx, file, 0);
}
int trace_vfswrite(struct pt_regs *ctx, struct file *file, 
    const char __user *buf, size_t count, loff_t *pos)
{
    return trace_common(ctx, file, 1);
}
int trace_vfswritev(struct pt_regs *ctx, struct file *file,
    const struct iovec __user *vec, unsigned long vlen,
    loff_t *pos, rwf_t flags)
{
    return trace_common(ctx, file, 1);
}
"""
b = BPF(text=bpf_text)
b.attach_kprobe(event="vfs_read", fn_name="trace_vfsread")
b.attach_kprobe(event="vfs_readv", fn_name="trace_vfsreadv")
b.attach_kprobe(event="vfs_write", fn_name="trace_vfswrite")
b.attach_kprobe(event="vfs_writev", fn_name="trace_vfswritev")

# header
print("Tracing... Ctrl-C to end.")

# output
ftype_dic = {7: "socket", 6: "link", 5:"regular", 4:"blk",
    3:"dir", 2:"char", 1:"pipe",0:"unknown"}

def decode_ftype(ftype):
    return ftype_dic.get(ftype, "err")
    
def print_count():
    data = b["data"]
    print("\n%-5s %-30s %5s %10s %10s" % ("PID", "COMM", "MODE", "FILE_TYPE", "COUNT"))
    for k, v in sorted(data.items(),key=lambda data: data[1].pid):
        print("%-5s %-30s %5s %10s %10s" % (v.pid, v.comm, "", "", ""))
        for idx, cnt_r in enumerate(v.cnt_r):
            if cnt_r:
                print("%-5s %-30s %5s %10s %10s" % ("", "", "r", decode_ftype(idx), cnt_r))
        for idx, cnt_w in enumerate(v.cnt_w):
            if cnt_w:
                print("%-5s %-30s %5s %10s %10s" % ("", "", "w", decode_ftype(idx), cnt_w))
    data.clear()

while True:
    try:
        sleep(999999)
    except KeyboardInterrupt:
        signal.signal(signal.SIGINT, signal_ignore)
    print_count()
    exit()
