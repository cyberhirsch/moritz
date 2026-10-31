##########
Installing
##########

Download Moritz from the `releases page <https://github.com/cyberhirsch/moritz/releases>`__.

Windows
=======

``moritz-<version>-windows-x64.msi``
   Installs for your user only, no administrator rights needed, into
   ``%LOCALAPPDATA%\Programs\Moritz``, with a Start Menu entry. An older all-users install
   (0.2.0) has to be uninstalled first; the installer tells you so.

``moritz-<version>-windows-x64.zip``
   Portable: unpack anywhere and start ``moritz.exe``.

Linux and macOS
===============

Packages for Linux (``.tar.xz``) and macOS (``.dmg``) are planned for 0.3.0.

Until Moritz has an Apple developer signature, macOS will say the app "is damaged". Open it with
right-click > **Open**, or run ``xattr -cr /Applications/Moritz.app`` once in Terminal.

Settings
========

Moritz keeps its settings apart from any Blender installation, so the two never change each
other's preferences:

* Windows: ``%APPDATA%\Moritz\<version>``
* Linux: ``~/.config/moritz/<version>``
* macOS: ``~/Library/Application Support/Moritz/<version>``

On the first start the :doc:`quick_setup` asks for your keymap and names.

.. seealso:: :blender:`Blender's installation guide <getting_started/installing/index.html>`
