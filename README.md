# ScreenConnect Client - Linux Fix (Arch and other distros)

This script patches the `ScreenConnect.ClientSetup.sh` file provided by ScreenConnect instances with the `LinuxAppSelector` option.

The function `determinePackageType` (lines 118-126) explicitly looks for `rpm`, `pkgutil` (macOS), or `dpkg` (Debian/Ubuntu).

Other distros like Arch Linux however, return nothing causing the following error:
```
InstallPackageFile: command not found
```

The `client-fix.py` file in this repo modifies the script to fallback to the "app" installer mode that installs to `~/.local/share/applications/connectwisecontrol-*`.

After this completes the ScreenConnect client should be under the Lost & Found section of app launchers and browsers should be able to launch it.

To run this script:
```bash
python ./client-fix.py ./ScreenConnect.ClientSetup.sh

# or if the ScreenConnect.ClientSetup.sh is in the same folder
python ./client-fix.py
```
