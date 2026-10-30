@echo off
echo Starting Moritz with the Vulkan backend

"%~dp0\blender" --gpu-backend vulkan
