# hacking notes

# byte-order fix in omg

The wad headers reported incorrectly on *nix systems due to it assuming a little-endian byte-order in the c types struct data.
I forced little-endian order by prefixing the struct format with "<", resolving the issue.
See https://docs.python.org/2/library/struct.html#struct-alignment
and https://stackoverflow.com/a/36085069
