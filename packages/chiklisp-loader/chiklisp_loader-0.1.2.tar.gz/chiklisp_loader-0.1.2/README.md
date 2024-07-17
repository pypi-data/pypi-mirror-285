# chiklisp_loader

This tiny wheel exports `load_program`, which is used to load [chiklisp](https://chiklisp.com/) programs from resources included with python wheels.

Chiklisp `.clsp` files are compiled into `.hex` output. Only `.hex` output files need to be included in binary wheels

When `load_program` is called, it tries to import `chiklisp_builder`. If it fails, it assumes this is running at deploy time: any `.clsp` files are ignored, and the corresponding program is loaded from the `.hex` file.
