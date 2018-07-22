#!/usr/bin/python

import re
import struct
import collections
import sys


address_pattern = re.compile(r'^([0-9a-f]+)-([0-9a-f]+)\s+')
value_pattern = re.compile(r'(^\w+):\s+(.*)$')
kb_pattern = re.compile(r'(\d+) kB')

def parse_smaps(file):
    entries = { }

    for line in file:
        line = line.rstrip()

        match = address_pattern.match(line)

        if match:
            begin = int(match.group(1), 16)
            end = int(match.group(2), 16)
            entries[begin, end, line] = entry = { }
            continue
        
        match = value_pattern.match(line)

        if match:
            key, value = match.group(1), match.group(2)
            match = kb_pattern.match(value)
            if match: value = int(match.group(1)) * 1024
            entry[key] = value
            continue
    
    return entries


def sequential_group_reduce(data, grouping_predicate, reducing_func):
    groups = []
    group = []
    
    for value in data:
        if len(group) == 0:
            group.append(value)
            continue
        
        if grouping_predicate(group, value):
            group.append(value)
        else:
            groups.append(reducing_func(group))
            group = [value]
    
    if len(group):
        groups.append(reducing_func(group))

    return groups


def ppfn_sequential_pages(ppfn_list):
    return sequential_group_reduce(sorted(ppfn_list),
                                   lambda group, value: value == group[0] + len(group),
                                   lambda group: (group[0], len(group)))


def ppfn_compound_pages(ppfn_list, ppfn_flags):
    return sequential_group_reduce([(ppfn, ppfn_flags[ppfn]) for ppfn in sorted(ppfn_list)],
                                   lambda group, value: (group[0][1] & 0x8000 != 0) and (value[1] & 0x10000 != 0),
                                   lambda group: (group[0][0], len(group)))

def ppfn_summarize_pages(ppfn_pages):
    return sequential_group_reduce(sorted(ppfn_pages, key = lambda x: x[0]),
                                   lambda group, value: (group[0][1] == value[1]) and (group[-1][0] + group[-1][1] == value[0]),
                                   lambda group: (group[0][0], group[0][1], len(group)))

def size_format(value):
    if value > 1048576: return "%.7g MiB" % (value / 1048576)
    else: return "%.6g KiB" % (value / 1024)



def syntax():
    print("syntax: %s [-a] [-m] [PID]" % sys.argv[0])
    print()
    print("    -a    List all memory segments (default shows only the largest)")
    print("    -m    List all physical page mappings")
    exit(1)

opt_all = False
opt_mappings = False
pid = None

for arg in sys.argv[1:]:
    if arg == "-a": opt_all = True
    elif arg == "-m": opt_mappings = True
    elif pid == None:
        try: pid = int(arg)
        except ValueError: syntax()
    else: syntax()

if pid == None: syntax()

smaps_file = open("/proc/%d/smaps" % pid, "r")
pagemap_file = open("/proc/%d/pagemap" % pid, "rb")
kpageflags_file = open("/proc/kpageflags", "rb")

smaps_entries = parse_smaps(smaps_file)

for (begin, end, line), values in sorted(smaps_entries.items(), key = lambda x: -x[1]["Size"]):
    vpfn_begin = begin // 4096
    vpfn_count = (end - begin) // 4096    

    pagemap_file.seek(vpfn_begin * 8)
    pagemap_data = pagemap_file.read(vpfn_count * 8)
    assert len(pagemap_data) == vpfn_count * 8

    ppfn_list = []

    for index in range(vpfn_count):
        vpfn_index = index + vpfn_begin
        pagemap_entry, = struct.unpack("=Q", pagemap_data[index*8:index*8+8])

        if pagemap_entry & 0xE000000000000000 == 0x8000000000000000: # present = 1, swap = 0, file/shared = 0            
            ppfn_list.append(pagemap_entry & 0x003FFFFFFFFFFFFF)

    ppfn_ranges = ppfn_sequential_pages(ppfn_list)

    ppfn_flags = { }

    for ppfn_begin, ppfn_count in ppfn_ranges:
        kpageflags_file.seek(ppfn_begin * 8)
        kpageflags_data = kpageflags_file.read(ppfn_count * 8)
        assert len(kpageflags_data) == ppfn_count * 8

        for index in range(ppfn_count):
            ppfn_flags[index + ppfn_begin] = struct.unpack("=Q", kpageflags_data[index*8:index*8+8])[0]
        
    ppfn_pages = ppfn_compound_pages(ppfn_list, ppfn_flags)

    ppfn_summary = ppfn_summarize_pages(ppfn_pages)

    pt_summary = collections.defaultdict(int)
    pt_total_size = 0

    for ppfn, size, count in ppfn_summary:
        pt_summary[size] += count
        pt_total_size += count * size * 4096

    if pt_total_size == 0:
        continue

    print("SEGMENT: %s" % line)
    print()
    print("  SMAPS PROPERTY                  VALUE")

    for key, value in values.items():        
        print("    %-29s   %s" % (key, value))

    print()
    print("  NUM_PAGES       PAGE_SIZE       TOTAL_USAGE     PAGE_SIZE_PERCENT")

    for size, count in pt_summary.items():
        print("    %-13s   %-13s   %-13s   %-13s" % (
              "%d" % count,
              size_format(size * 4096),
              size_format(size * count * 4096),
              "%0.1f %%" % (size * count * 4096 * 100 / pt_total_size)))
    
    print()

    if opt_mappings:
        print("  PHYS_ADDR       PHYS_LENGTH     PAGE_SIZE       PAGE_COUNT")

        for ppfn, size, count in ppfn_summary:
            print("    %-13s   %-13s   %-13s   %-13s" % (
                "%X" % (ppfn * 4096),
                size_format(size * count * 4096),
                size_format(size * 4096),
                "%d" % count))

        print()

    if opt_all == False: break





