# HACKING

Notes for developing and packaging Dmon.

# BASELINES

Generate a new baseline by giving the `--average --format=dump` options. The entry can be added to the `baselines.py` source file. Pull requests are welcome.

# RELEASE STEPS

1. update __version__ in `dmon.py`
2. git commit && git tag "1.n" && git push && git push origin "1.n"

# FREEZING

Install py2exe via the command below. If using WinPython open the `WinPython Command Prompt` which should have `pip` in its path.

```
pip install py2exe
```

To make a Windows binary:

1. Run `python setup.py py2exe` from `src`
2. Rename the `dist/dmon-1.n_win` directory to match the built version
3. `zip` the directory
