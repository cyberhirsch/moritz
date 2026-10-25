# SPDX-FileCopyrightText: 2026 Moritz Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later

"""Build a Windows installer (MSI) for a built Moritz with WiX 5.

    python moritz/tools/make_msi.py <bin/Release> [<Maximize repo>] [<out dir>]

Needs the WiX .NET tool (`dotnet tool install --global wix`) with the UI extension
(`wix extension add --global WixToolset.UI.wixext`). The program folder is staged the same way
as the portable zip (Maximize copied in as real files, no debug symbols or build tools), then
installed to Program Files\\Moritz for all users, with a Start Menu shortcut.

Moritz has its own upgrade code, so it installs next to Blender and never replaces it. It
registers no file types: .blend files keep opening in (and showing the icon of) Blender.
"""

import os
import shutil
import subprocess
import sys
import tempfile

from make_portable_zip import SKIP_NAMES, SKIP_SUFFIXES, _is_junction, version

# Fixed forever: Windows matches installed and new versions of Moritz by it.
UPGRADE_CODE = "6F1E2C7A-3D5B-4E8F-9A21-4D0C7B5E9A13"
SHORTCUT_GUID = "B3A7D0E2-5C41-4F9B-8E6D-2A7C1F0B9D54"

SOURCE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def stage_tree(src, dst, skip_dirs=()):
    for dirpath, dirnames, filenames in os.walk(src):
        dirnames[:] = [d for d in dirnames
                       if not os.path.islink(os.path.join(dirpath, d)) and
                       not _is_junction(os.path.join(dirpath, d)) and
                       os.path.join(dirpath, d) not in skip_dirs and d != "__pycache__"]
        target = os.path.join(dst, os.path.relpath(dirpath, src))
        os.makedirs(target, exist_ok=True)
        for name in filenames:
            if not (name.endswith(SKIP_SUFFIXES) or name in SKIP_NAMES):
                shutil.copy2(os.path.join(dirpath, name), os.path.join(target, name))


def rtf(text):
    body = text.replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}")
    body = "\\par\n".join(body.splitlines())
    return "{\\rtf1\\ansi\\deff0{\\fonttbl{\\f0 Segoe UI;}}\\fs16\n" + body + "\n}"


WXS = r'''<Wix xmlns="http://wixtoolset.org/schemas/v4/wxs"
     xmlns:ui="http://wixtoolset.org/schemas/v4/wxs/ui">
  <Package Name="Moritz {ver}" Manufacturer="Moritz" Version="{msi_ver}" Language="1033"
           UpgradeCode="{upgrade}" Scope="perMachine" Compressed="yes">
    <MajorUpgrade AllowSameVersionUpgrades="yes"
                  DowngradeErrorMessage="A newer Moritz is already installed." />
    <MediaTemplate EmbedCab="yes" CompressionLevel="high" />

    <Icon Id="moritz.ico" SourceFile="{icon}" />
    <Property Id="ARPPRODUCTICON" Value="moritz.ico" />
    <WixVariable Id="WixUILicenseRtf" Value="{license}" />
    <ui:WixUI Id="WixUI_InstallDir" InstallDirectory="INSTALLFOLDER" />

    <StandardDirectory Id="ProgramFiles64Folder">
      <Directory Id="INSTALLFOLDER" Name="Moritz" />
    </StandardDirectory>

    <ComponentGroup Id="Program" Directory="INSTALLFOLDER">
      <Files Include="!(bindpath.stage)\**" />
    </ComponentGroup>

    <StandardDirectory Id="ProgramMenuFolder">
      <Component Id="StartMenuShortcut" Guid="{shortcut_guid}">
        <Shortcut Id="MoritzShortcut" Name="Moritz" Target="[INSTALLFOLDER]moritz-launcher.exe"
                  WorkingDirectory="INSTALLFOLDER" Icon="moritz.ico" />
        <RegistryValue Root="HKLM" Key="Software\Moritz" Name="InstallDir" Type="string"
                       Value="[INSTALLFOLDER]" KeyPath="yes" />
      </Component>
    </StandardDirectory>

    <Feature Id="Main" Title="Moritz" AllowAbsent="no">
      <ComponentGroupRef Id="Program" />
      <ComponentRef Id="StartMenuShortcut" />
    </Feature>
  </Package>
</Wix>
'''


def main():
    release = os.path.abspath(sys.argv[1])
    maximize = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else None
    out_dir = os.path.abspath(sys.argv[3]) if len(sys.argv) > 3 else os.getcwd()
    ver = version(release)
    out = os.path.join(out_dir, "moritz-{}-windows-x64.msi".format(ver))

    work = tempfile.mkdtemp(prefix="moritz_msi_")
    try:
        stage = os.path.join(work, "stage")
        stage_tree(release, stage, skip_dirs=(os.path.join(release, "portable"),))
        if maximize:
            stage_tree(os.path.join(maximize, "maximize"),
                       os.path.join(stage, ver, "scripts", "addons_core", "maximize"))

        license_rtf = os.path.join(work, "license.rtf")
        with open(os.path.join(SOURCE, "release", "license", "spdx", "GPL-3.0-or-later.txt"),
                  encoding="utf-8") as f:
            text = f.read()
        with open(license_rtf, "w", encoding="ascii", errors="replace") as f:
            f.write(rtf(text))

        wxs = os.path.join(work, "moritz.wxs")
        with open(wxs, "w", encoding="utf-8") as f:
            f.write(WXS.format(ver=ver, msi_ver=ver + ".0", upgrade=UPGRADE_CODE,
                               shortcut_guid=SHORTCUT_GUID, license=license_rtf,
                               icon=os.path.join(SOURCE, "release", "windows", "icons",
                                                 "winblender.ico")))
        subprocess.run(["wix", "build", "-arch", "x64", "-ext", "WixToolset.UI.wixext",
                        "-bindpath", "stage=" + stage, "-o", out, wxs], check=True)
    finally:
        shutil.rmtree(work, ignore_errors=True)
    print(out, round(os.path.getsize(out) / 1e6), "MB")


if __name__ == "__main__":
    main()
