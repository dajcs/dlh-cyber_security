#!/usr/bin/env python3
"""Find and replace one NUL-terminated ASCII string in a process's heap."""

import os
import sys


CHUNK_SIZE = 64 * 1024


def usage_error(message):
    print(f"Error: {message}")
    print(f"Usage: {sys.argv[0]} pid search_string replace_string")
    return 1


def heap_regions(pid):
    """Yield the readable/writable [heap] mappings from /proc/PID/maps."""
    with open(f"/proc/{pid}/maps", "r", encoding="ascii") as maps:
        for line in maps:
            parts = line.split()
            if len(parts) >= 6 and parts[-1] == "[heap]":
                address_range, permissions = parts[0], parts[1]
                if "r" not in permissions or "w" not in permissions:
                    continue
                start, end = (int(addr, 16) for addr in address_range.split("-"))
                yield start, end


def find_in_region(mem_fd, start, end, needle):
    """Scan in chunks, keeping an overlap for matches across chunk boundaries."""
    overlap = b""
    position = start

    while position < end:
        count = min(CHUNK_SIZE, end - position)
        data = os.pread(mem_fd, count, position)
        if not data:
            raise OSError("Could not read the complete heap region")

        block = overlap + data
        index = block.find(needle)
        if index != -1:
            return position - len(overlap) + index

        overlap = block[-(len(needle) - 1):] if len(needle) > 1 else b""
        position += len(data)

    return None


def main(args):
    if len(args) != 3:
        return usage_error("Expected exactly three arguments")

    pid_text, search_text, replace_text = args

    try:
        pid = int(pid_text)
        if pid <= 0:
            raise ValueError
    except ValueError:
        return usage_error("PID must be a positive integer")

    if not search_text or "\0" in search_text or "\0" in replace_text:
        return usage_error("Search must be nonempty; strings cannot contain NUL")

    try:
        search = search_text.encode("ascii")
        replacement = replace_text.encode("ascii")
    except UnicodeEncodeError:
        return usage_error("Both strings must contain only ASCII characters")

    if len(replacement) > len(search):
        return usage_error("Replacement cannot be longer than the original string")

    # The C program stores strings terminated by a NUL byte.
    needle = search + b"\0"
    new_value = replacement + b"\0"

    try:
        regions = list(heap_regions(pid))
        if not regions:
            print("Error: No readable/writable [heap] mapping found")
            return 1

        with open(f"/proc/{pid}/mem", "r+b", buffering=0) as mem:
            for start, end in regions:
                address = find_in_region(mem.fileno(), start, end, needle)
                if address is not None:
                    bytes_written = os.pwrite(mem.fileno(), new_value, address)
                    if bytes_written != len(new_value):
                        raise OSError("Incomplete write to process memory")

                    print(f"Heap range: {start:#x}-{end:#x}")
                    print(f"Found {search_text!r} at {address:#x}")
                    print(f"Replaced with {replace_text!r}")
                    return 0

        print(f"String {search_text!r} not found in the heap of PID {pid}")
        return 1

    except OSError as exc:
        print(f"Error accessing process {pid}: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
