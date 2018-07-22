# Theory of operation

Read the virtual mappings out of `/proc/pid/smaps`. Then read the corresponding physical mappings out of `/proc/pid/pagemap` and physical page flags out of `/proc/kpageflags`. Prints statistics and optionally list all physical page ranges. Only works for regular data pages, swapped or file mapped pages are ignored.

# Usage
```
syntax: ./pagestat.py [-a] [-m] [PID]

    -a    List all memory segments (default shows only the largest)
    -m    List all physical page mappings
```

# Example

QEMU with THP (default config) with fragmented memory:
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

QEMU with 1G static hugepages:
```
./pagestat.py -m 15626
SEGMENT: 7f6f00000000-7f7000000000 rw-p 00000000 00:2b 19096                      /dev/hugepages/libvirt/qemu/4-mordor/qemu_back_mem.pc.ram.vrCDvT (deleted)

  SMAPS PROPERTY                  VALUE
    Size                            4294967296
    KernelPageSize                  1073741824
    MMUPageSize                     1073741824
    Rss                             0
    Pss                             0
    Shared_Clean                    0
    Shared_Dirty                    0
    Private_Clean                   0
    Private_Dirty                   0
    Referenced                      0
    Anonymous                       0
    LazyFree                        0
    AnonHugePages                   0
    ShmemPmdMapped                  0
    Shared_Hugetlb                  0
    Private_Hugetlb                 4294967296
    Swap                            0
    SwapPss                         0
    Locked                          0
    VmFlags                         rd wr mr mw me dc de ht dd hg

  NUM_PAGES       PAGE_SIZE       TOTAL_USAGE     PAGE_SIZE_PERCENT
    4               1024 MiB        4096 MiB        100.0 %

  PHYS_ADDR       PHYS_LENGTH     PAGE_SIZE       PAGE_COUNT
    300000000       4096 MiB        1024 MiB        4
```

QEMU with 2M static hugepages:
```./pagestat.py -m 2440
SEGMENT: 7ff00be00000-7ff10be00000 rw-p 00000000 00:2b 18936                      /dev/hugepages/libvirt/qemu/2-mordor/qemu_back_mem.pc.ram.oDAqHr (deleted)

  SMAPS PROPERTY                  VALUE
    Size                            4294967296
    KernelPageSize                  2097152
    MMUPageSize                     2097152
    Rss                             0
    Pss                             0
    Shared_Clean                    0
    Shared_Dirty                    0
    Private_Clean                   0
    Private_Dirty                   0
    Referenced                      0
    Anonymous                       0
    LazyFree                        0
    AnonHugePages                   0
    ShmemPmdMapped                  0
    Shared_Hugetlb                  0
    Private_Hugetlb                 4294967296
    Swap                            0
    SwapPss                         0
    Locked                          0
    VmFlags                         rd wr mr mw me dc de ht dd hg

  NUM_PAGES       PAGE_SIZE       TOTAL_USAGE     PAGE_SIZE_PERCENT
    2048            2 MiB           4096 MiB        100.0 %

  PHYS_ADDR       PHYS_LENGTH     PAGE_SIZE       PAGE_COUNT
    30AC00000       3972 MiB        2 MiB           1986
    404800000       124 MiB         2 MiB           62
```
