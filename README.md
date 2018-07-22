# Theory of operation

Read the virtual mappings out of `/proc/pid/smaps`. Then read the corresponding physical mappings out of `/proc/pid/pagemap` and physical page flags out of `/proc/kpageflags`. Prints statistics and optionally list all physical page ranges. Only works for regular data pages, swapped or file mapped pages are ignored.

# Usage
```
syntax: ./pagestat.py [-a] [-m] [PID]

    -a    List all memory segments (default shows only the largest)
    -m    List all physical page mappings
```

# Example

```
./pagestat.py 14341
SEGMENT: 7f4fc6e00000-7f5237e00000 rw-p 00000000 00:00 0

  SMAPS PROPERTY                  VALUE
    Size                            10485760000
    KernelPageSize                  4096
    MMUPageSize                     4096
    Rss                             10485760000
    Pss                             10485760000
    Shared_Clean                    0
    Shared_Dirty                    0
    Private_Clean                   0
    Private_Dirty                   10485760000
    Referenced                      10485760000
    Anonymous                       10485760000
    LazyFree                        0
    AnonHugePages                   6861881344
    ShmemPmdMapped                  0
    Shared_Hugetlb                  0
    Private_Hugetlb                 0
    Swap                            0
    SwapPss                         0
    Locked                          10485760000
    VmFlags                         rd wr mr mw me dc ac dd hg mg

  NUM_PAGES       PAGE_SIZE       TOTAL_USAGE     PAGE_SIZE_PERCENT
    3272            2 MiB           6544 MiB        65.4 %
    884736          4 KiB           3456 MiB        34.6 %
```
