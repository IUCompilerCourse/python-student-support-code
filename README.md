# python-student-support-code

Support code for students (Python version).

The `runtime.c` file needs to be compiled by doing the following
```
   gcc -c -g -std=c99 runtime.c
```
This will produce a file named `runtime.o`. The -g flag is to tell the
compiler to produce debug information that you may need to use
the gdb (or lldb) debugger.

On a Mac with an M1 (ARM) processor, use the `-arch x86_64` flag to
compile the runtime:
```
   gcc -c -g -std=c99 -arch x86_64 runtime.c
```

# Using the Racket x86 interpreter (TODO)
