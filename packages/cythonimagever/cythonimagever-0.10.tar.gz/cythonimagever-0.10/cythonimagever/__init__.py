try:
    from .cyimage import *

except Exception as e:
    import Cython, setuptools, platform, subprocess, os, sys, time,numpy 

    iswindows = "win" in platform.platform().lower()
    if iswindows:
        addtolist = []
    else:
        addtolist = ["&"]

    olddict = os.getcwd()
    dirname = os.path.dirname(__file__)
    os.chdir(dirname)
    compile_file = os.path.join(dirname, "cyimage_compile.py")
    subprocess._USE_VFORK = False
    subprocess._USE_POSIX_SPAWN = False
    subprocess.run(
        " ".join(
            [
                sys.executable,
                compile_file,
                "build_ext",
                "--inplace",
            ]
            + addtolist
        ),
        shell=True,
        env=os.environ,
        preexec_fn=None
        if iswindows
        else os.setpgrp
        if hasattr(os, "setpgrp")
        else None,
    )
    if not iswindows:
        time.sleep(30)
    from .cyimage import *

    os.chdir(olddict)
