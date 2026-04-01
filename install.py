"""
tracefix/install.py

Handles writing and removing the autoload hook from site-packages.
This is what makes tracefix activate automatically on every Python run
after the first install — like a VS Code extension registering itself.
"""

import sys
import site
import shutil
import os


AUTOLOAD_FILENAME = "tracefix_autoload.py"
PTH_FILENAME = "tracefix.pth"


def _get_site_packages() -> str:
    """Return the best writable site-packages directory for this Python environment."""
    # site.getusersitepackages() is always writable without sudo
    user_site = site.getusersitepackages()
    os.makedirs(user_site, exist_ok=True)
    return user_site


def _autoload_path() -> str:
    return os.path.join(_get_site_packages(), AUTOLOAD_FILENAME)


def _pth_path() -> str:
    return os.path.join(_get_site_packages(), PTH_FILENAME)


def _tracefix_src_dir() -> str:
    """Return the directory where tracefix's own source files live (the package folder itself)."""
    return os.path.dirname(os.path.abspath(__file__))


def install():
    """
    First-run setup. Writes two files into site-packages:
      1. tracefix_autoload.py  — activates the excepthook at Python startup
      2. tracefix.pth          — adds tracefix's parent dir to sys.path so
                                 `from tracefix.hook import activate` resolves
    """
    site_packages = _get_site_packages()
    autoload_dst = _autoload_path()
    pth_dst = _pth_path()
    # The .pth must point to the PARENT of the tracefix package folder
    # so that `import tracefix` resolves correctly.
    src_dir = os.path.dirname(_tracefix_src_dir())

    # Write the .pth file so Python can find the tracefix package
    with open(pth_dst, "w") as f:
        f.write(src_dir + "\n")

    # Write the autoload shim
    autoload_src = os.path.join(_tracefix_src_dir(), "..", "tracefix_autoload.py")
    autoload_src = os.path.normpath(autoload_src)

    if os.path.exists(autoload_src) and os.path.getsize(autoload_src) > 0:
        shutil.copy2(autoload_src, autoload_dst)
    else:
        # Write it inline as a fallback (also used if autoload file is empty)
        with open(autoload_dst, "w") as f:
            f.write(
                'try:\n'
                '    from tracefix.hook import activate\n'
                '    activate()\n'
                'except Exception:\n'
                '    pass\n'
            )

    print(f"\n✅ tracefix installed successfully.")
    print(f"   Hook file : {autoload_dst}")
    print(f"   Path file : {pth_dst}")
    print(f"\n   tracefix will now auto-analyze errors in every Python session.\n")


def uninstall():
    """Remove tracefix's autoload hook and .pth file from site-packages."""
    removed = []

    for path in [_autoload_path(), _pth_path()]:
        if os.path.exists(path):
            os.remove(path)
            removed.append(path)

    if removed:
        print("\n✅ tracefix uninstalled.")
        for r in removed:
            print(f"   Removed: {r}")
        print()
    else:
        print("\n⚠️  tracefix was not installed (nothing to remove).\n")


def status():
    """Check whether tracefix is currently installed."""
    autoload = _autoload_path()
    pth = _pth_path()

    autoload_exists = os.path.exists(autoload)
    pth_exists = os.path.exists(pth)
    hook_active = sys.excepthook.__module__ is not None and "tracefix" in str(sys.excepthook)

    print("\n──────────────────────────────")
    print("  tracefix status")
    print("──────────────────────────────")
    print(f"  Autoload file : {'✅ present' if autoload_exists else '❌ not found'}")
    print(f"  Path file     : {'✅ present' if pth_exists else '❌ not found'}")
    print(f"  Hook active   : {'✅ yes' if hook_active else '❌ no (run install first)'}")
    print(f"\n  Site-packages : {_get_site_packages()}")
    print("──────────────────────────────\n")