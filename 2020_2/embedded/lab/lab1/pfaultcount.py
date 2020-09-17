#!/usr/bin/python

from bcc import BPF
from time import sleep, strftime
import signal


# signal handler
def signal_ignore(signal, frame):
    print()

bpf_text = """
#include <uapi/linux/ptrace.h>
#include <linux/mm.h>

struct key_t {
    char filename[30];
};

BPF_HASH(data, struct key_t);

void kprobe__handle_mm_fault(struct pt_regs *ctx, struct vm_area_struct *vma, 
    unsigned long address, unsigned int flags)
{
       
    struct file *file = vma->vm_file;
    struct key_t key = {};
    u64 *val, zero = 0;
    int ret;
    
    if(!file)
        return;

    ret = bpf_probe_read_kernel_str(&key.filename, 30, file->f_path.dentry->d_name.name);
    if(ret < 0)
        return;
    
    val = data.lookup_or_try_init(&key, &zero);
    data.increment(key);
    
}
"""

bpf = BPF(text=bpf_text)

def print_count():
    data = bpf["data"]
    print()
    print("%-30s %8s" % ("File name", "COUNT"))
        
    for k, v in sorted(data.items(),key=lambda data: -data[1].value)[:30]:
        print(("%-30s %8s") % (k.filename, v.value))
    print("")
    data.clear()

print("Tracing page faults, printing top 30 files... Ctrl+C to quit.")

while True:
    try:
        sleep(999999)
    except KeyboardInterrupt:
        signal.signal(signal.SIGINT, signal_ignore)
   
    print_count()
    exit()

