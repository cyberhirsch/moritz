##########
moritz-cli
##########

``moritz-cli`` sits next to ``moritz.exe`` and runs Moritz commands from a terminal or script:

.. code-block:: none

   moritz-cli info scene.blend
   moritz-cli convert scene.blend scene.glb
   moritz-cli render scene.blend -o frame_####.png --frames 1-24
   moritz-cli run script.py
   moritz-cli command list
   moritz-cli command run create type=Teapot parameters={"Radius":2} --connect

Commands: ``info``, ``open``, ``render``, ``convert``, ``run``, ``test``, ``command list``,
``command run``, ``serve``.

* Without ``--connect`` each command runs in a background Moritz.
* With ``--connect`` it runs in the open Moritz (enable Moritz MCP in Preferences first, see
  :doc:`mcp`).
* ``--json`` prints JSON for scripts.

The commands are the same as Moritz MCP's.

.. seealso:: :blender:`Blender's command line <advanced/command_line/index.html>`
