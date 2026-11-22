#!/usr/bin/python3
"""
read_write_heap.py - finds a string in the heap of a running process
and replaces it with another string of the same length.

Usage: read_write_heap.py pid search_string replace_string
"""
import sys
import os


def error_exit(message):
    """Print an error message and exit with status code 1"""
    print(message)
    sys.exit(1)


def get_heap_range(pid):
    """Parse /proc/[pid]/maps to find the [heap] region's start/end addr"""
    maps_path = "/proc/{}/maps".format(pid)
    try:
        with open(maps_path, "r") as maps_file:
            for line in maps_file:
                if "[heap]" in line:
                    addr_range = line.split()[0]
                    start_str, end_str = addr_range.split("-")
                    return int(start_str, 16), int(end_str, 16)
    except FileNotFoundError:
        error_exit("Error: no process found with pid {}".format(pid))
    except PermissionError:
        error_exit(
            "Error: permission denied reading maps of pid {}".format(pid)
        )
    return None, None


def read_write_heap(pid, search_string, replace_string):
    """Search the heap of pid for search_string and replace it in place"""
    start, end = get_heap_range(pid)
    if start is None:
        error_exit("Error: no heap region found for pid {}".format(pid))

    search_bytes = search_string.encode("ascii")
    replace_bytes = replace_string.encode("ascii")

    if len(replace_bytes) > len(search_bytes):
        error_exit(
            "Error: replace_string must not be longer than search_string"
        )

    padding_needed = len(search_bytes) - len(replace_bytes)
    padded_replace_bytes = replace_bytes + b"\x00" * padding_needed

    mem_path = "/proc/{}/mem".format(pid)
    try:
        with open(mem_path, "r+b") as mem_file:
            mem_file.seek(start)
            heap_data = mem_file.read(end - start)

            offset = heap_data.find(search_bytes)
            if offset == -1:
                error_exit(
                    "Error: string '{}' not found in heap of pid {}"
                    .format(search_string, pid)
                )

            found_addr = start + offset
            mem_file.seek(found_addr)
            mem_file.write(padded_replace_bytes)

            if padding_needed > 0:
                print("[+] Found '{}' at address {}"
                      .format(search_string, hex(found_addr)))
                print("[+] Replaced with '{}' at address {}"
                      .format(replace_string, hex(found_addr)))
    except FileNotFoundError:
        error_exit("Error: no process found with pid {}".format(pid))
    except PermissionError:
        error_exit(
            "Error: permission denied accessing memory of pid {} "
            "(try running as root)".format(pid)
        )
    except OSError as os_error:
        error_exit("Error: {}".format(os_error))


def main():
    """Parse arguments and run the heap search/replace"""
    if len(sys.argv) != 4:
        error_exit(
            "Usage: {} pid search_string replace_string".format(sys.argv[0])
        )

    pid_arg, search_string, replace_string = sys.argv[1:4]

    if not pid_arg.isdigit():
        error_exit("Error: pid must be a positive integer")

    pid = int(pid_arg)

    if not os.path.isdir("/proc/{}".format(pid)):
        error_exit("Error: no process found with pid {}".format(pid))

    read_write_heap(pid, search_string, replace_string)


if __name__ == "__main__":
    main()
