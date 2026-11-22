# Buffer overflow

## Task 0. Hack the VM

Write a script that finds a string in the heap of a running process, and replaces it.

Usage: read_write_heap.py pid search_string replace_string
where pid is the pid of the running process
and strings are ASCII
The script should look only in the heap of the process
Output: you can print whatever you think is interesting
On usage error, print an error message on stdout and exit with status code 1

**Terminal 1**:

```c
┌──(maroua㉿HBTN-LAB)-[~/0x04. Buffer overflow]
└─🏴 cat main.c
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

/**
 * main - uses strdup to create a new string, loops forever-ever
 *
 * Return: EXIT_FAILURE if malloc failed. Other never returns
 */
int main(void)
{
    char *s;
    unsigned long int i;

    s = strdup("Holberton");
    if (s == NULL)
    {
        fprintf(stderr, "Can't allocate mem with malloc\n");
        return (EXIT_FAILURE);
    }
    i = 0;
    while (s)
    {
        printf("[%lu] %s (%p)\n", i, s, (void *)s);
        sleep(1);
        i++;
    }
    return (EXIT_SUCCESS);
}
```

**Terminal 1**:

```bash
┌──(maroua㉿HBTN-LAB)-[~/0x04. Buffer overflow]
└─🏴 gcc -Wall -pedantic -Werror -Wextra main.c -o main
┌──(maroua㉿HBTN-LAB)-[~/0x04. Buffer overflow]
└─🏴./main
[0] Holberton (0x555e646e02a0)
[1] Holberton (0x555e646e02a0)
[2] Holberton (0x555e646e02a0)
[3] Holberton (0x555e646e02a0)
[4] Holberton (0x555e646e02a0)
[5] Holberton (0x555e646e02a0)
[6] Holberton (0x555e646e02a0)
[7] Holberton (0x555e646e02a0)
[8] Holberton (0x555e646e02a0)
[9] Holberton (0x555e646e02a0)
[10] Holberton (0x555e646e02a0)
[11] Holberton (0x555e646e02a0)
[12] Holberton (0x555e646e02a0)
[13] Holberton (0x555e646e02a0)
[14] Holberton (0x555e646e02a0)
[15] Holberton (0x555e646e02a0)
[16] Holberton (0x555e646e02a0)
[17] Holberton (0x555e646e02a0)
[18] Holberton (0x555e646e02a0)
[19] Holberton (0x555e646e02a0)
[20] Holberton (0x555e646e02a0)
...
[78] Holberton (0x555e646e02a0)
[79] Holberton (0x555e646e02a0)
[80] Holberton (0x555e646e02a0)
[81] Holberton (0x555e646e02a0)
[82] Holberton (0x555e646e02a0)
[83] Holberton (0x555e646e02a0)
[84] Holberton (0x555e646e02a0)
[85] Holberton (0x555e646e02a0)
[86] Holberton (0x555e646e02a0)
[87] Holberton (0x555e646e02a0)
[88] Holberton (0x555e646e02a0)
[89] Holberton (0x555e646e02a0)
[90] Holberton (0x555e646e02a0)
[91] Holberton (0x555e646e02a0)
[92] maroua (0x555e646e02a0)
[93] maroua (0x555e646e02a0)
[94] maroua (0x555e646e02a0)
[95] maroua (0x555e646e02a0)
[96] maroua (0x555e646e02a0)
[97] maroua (0x555e646e02a0)
[98] maroua (0x555e646e02a0)
[99] maroua (0x555e646e02a0)
[100] maroua (0x555e646e02a0)
[101] maroua (0x555e646e02a0)

...
```

**Terminal 2**

```bash
┌──(maroua㉿HBTN-LAB)-[~/0x04. Buffer overflow]
└─🏴 ps aux | grep ./main
maroua    6515 0.0  0.0   2776  1040 pts/1    S+   10:53   0:00 ./main
maroua    6575   0.0  0.0   9220  2344 pts/2    S+   10:53   0:00 grep --color=auto ./main
┌──(maroua㉿HBTN-LAB)-[~/0x04. Buffer overflow]
└─🏴 sudo python3 ./read_write_heap.py 6515 Holberton "maroua"
```

**Repo**:

- GitHub repository: `dlh-cyber_security`
- Directory: `linux_security/0x04_buffer_overflow`
- File: `read_write_heap.py`

---

## **Solution**

Created and tested a working Python script for the buffer overflow exercise.

**Download [read_write_heap.py](./read_write_heap.py)**

The script uses Linux's `/proc` filesystem to locate a running process's heap, find an ASCII string, and overwrite it.

## **1. How the script works**

There are four main steps.

**Step 1: Find the heap's memory addresses**

Linux exposes process memory mappings through:

```
/proc/<pid>/maps
```

A typical entry looks like:

```
555e646e0000-555e64701000 rw-p ... [heap]
```

The script searches specifically for `[heap]`, so it doesn't scan the stack, libraries, or other mapped regions.

**Step 2: Open the process's memory**

```
with open(f"/proc/{pid}/mem", "r+b", buffering=0) as mem:
```

The `r+b` mode allows reading and writing binary data.

**Step 3: Search for the original string**

The script searches for the ASCII bytes, including the C string's null terminator:

```
needle = search.encode("ascii") + b"\0"
```

It reads the heap in 64 KiB chunks to avoid loading a potentially large heap into memory.

**Step 4: Overwrite the string**

Once the address is found, the crucial operation is:

```
os.pwrite(mem.fileno(), replacement.encode("ascii") + b"\0", address)
```

This writes the replacement directly into the running process's memory.

## **2. How to run it**

In Terminal 1, compile and launch your C program:

```
gcc -Wall -Wextra -Werror -pedantic main.c -o main
./main
```

In Terminal 2, retrieve the PID:

```
pgrep -a main
```

Suppose the PID is `6515`.

Run:

```
sudo python3 read_write_heap.py 6515 Holberton maroua
```

Expected output from the Python script:

```
Heap range: 0x555e646e0000-0x555e64701000
Found 'Holberton' at 0x555e646e02a0
Replaced with 'maroua'
```

The addresses above are illustrative. Your process will have different addresses.

Meanwhile, Terminal 1 should change from:

```
[90] Holberton (0x555e646e02a0)
[91] Holberton (0x555e646e02a0)
[92] maroua (0x555e646e02a0)
[93] maroua (0x555e646e02a0)
[94] maroua (0x555e646e02a0)
```

Notice that the address stays the same. The program still points to the same memory location, but its contents have changed.

## **3. Important detail: Avoiding an actual buffer overflow**

The original string is:

```
Holberton\0
```

The replacement is:

```
maroua\0
```

The replacement is shorter, so it fits in the original allocation.

The script intentionally rejects a replacement longer than the original string. Otherwise, writing beyond the allocated buffer could corrupt adjacent heap memory.

## **4. Error handling**

The script also satisfies the task's usage-error requirement.

For example:

```
python3 read_write_heap.py
```

Produces:

```
Error: Expected exactly three arguments
Usage: read_write_heap.py pid search_string replace_string
```

And exits with status `1`.

We can verify this using:

```
echo $?
```

Expected:

```
1
```


---


> **One interesting distinction:** Despite the exercise being called *Buffer overflow*, the operation we're implementing is actually process memory manipulation. We're using the operating system's process-memory interface to modify another process's heap, without exploiting a buffer overflow vulnerability in the C program itself.


## Task 1. Buffer Overflow Attack Report!

Buffer overflows occur when a program attempts to write more data to a buffer than it can hold, potentially overwriting adjacent memory locations. This can be exploited by attackers to gain unauthorized access to systems or execute malicious code.

Report Guidelines:
Your task is to create a detailed blog post that covers various aspects of buffer overflow.

Methodology:

Define buffer overflows and their significance in computer security and briefly describe the potential consequences of buffer overflow attacks on systems and data.
Explain how buffer overflows occur, outlining the concept of overflowing data buffers and potential memory corruption.
Provide a simplified example of how an attacker might exploit a buffer overflow vulnerability.
Discuss the historical significance of buffer overflow attacks, citing real-world examples like the Morris Worm or Heartbleed bug.
Describe practical methods that can be used to reduce the risk of buffer overflow vulnerabilities in software

Submission Instructions:

Submit your report in a format suitable for sharing, create your report in Google Docs, ensuring it is well-organized and follows the guidelines provided.
Upon completion, adjust the sharing settings to Anyone with the link can view.
Submit the link to your report as part of your project completion.
Your posts should have examples and at least one picture, at the top. Publish your blog post on Medium and and share it at least LinkedIn.
Please, remember that these blogs must be written in English to further your technical ability in a variety of settings.
This task challenges you to delve into the world of buffer overflow attacks, understand their mechanisms and implications, and explore methods for safeguarding systems from such vulnerabilities.

Repo:

- GitHub repository: `dlh-cyber_security`
- Directory: `linux_security/0x04_buffer_overflow`
- File: `buffer_overflow_attack_report.md`

