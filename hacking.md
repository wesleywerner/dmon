# HACKING

Notes for developing and packaging Dmon.

# BASELINES

Generate a new baseline by giving the `--average --format=dump` options. The entry can be added to the `baselines.py` source file. Pull requests are welcome.

# RELEASE STEPS

1. update __version__ in `dmon.py`
2. git commit && git tag "1.n" && git push && git push origin "1.n"

# FREEZING

Install py2exe via `pip install py2exe` or install it manually as per below.

**initial windows setup**

1. Install [winpython](http://winpython.github.io/) - python 2.7
2. Download [py2exe](http://py2exe.org/), extract it into `python\Lib`

**packaging**

1. Run `python setup.py py2exe` from `src`
2. Rename the `dist/dmon-1.n_win` directory to match the built version
3. `zip` the directory

# BYTE-ORDER FIX IN OMG

The wad headers reported incorrectly on *nix systems due to it assuming a little-endian byte-order in the c types struct data.
I forced little-endian order by prefixing the struct format with "<", resolving the issue.
See https://docs.python.org/2/library/struct.html#struct-alignment
and https://stackoverflow.com/a/36085069
