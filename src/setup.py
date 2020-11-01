from distutils.core import setup
import py2exe
setup(console=['dmon.py'],options={"py2exe":{"dist_dir":"dist/dmon-1.n_win"}})
