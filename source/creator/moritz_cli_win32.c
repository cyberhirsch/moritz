/* SPDX-FileCopyrightText: 2026 Moritz Authors
 *
 * SPDX-License-Identifier: GPL-2.0-or-later */

/** \file
 * \ingroup creator
 *
 * moritz-cli.exe: runs `<version>\scripts\modules\moritz_cli.py` with Moritz's own Python
 * (`<version>\python\bin\python.exe`), passing the command line on, and returns its exit code.
 * The command line tool itself is Python; this only gives it a name next to moritz.exe.
 */

#ifdef WIN32_LEAN_AND_MEAN
#  undef WIN32_LEAN_AND_MEAN
#endif
#include <Windows.h>
#include <strsafe.h>
#include <wchar.h>

#include <PathCch.h>

/** The command line after the program name. */
static const wchar_t *arguments_after_program(const wchar_t *cmd)
{
  if (*cmd == L'"') {
    cmd++;
    while (*cmd && *cmd != L'"') {
      cmd++;
    }
    if (*cmd) {
      cmd++;
    }
  }
  else {
    while (*cmd && *cmd != L' ' && *cmd != L'\t') {
      cmd++;
    }
  }
  while (*cmd == L' ' || *cmd == L'\t') {
    cmd++;
  }
  return cmd;
}

int wmain(void)
{
  wchar_t folder[MAX_PATH];
  if (!GetModuleFileNameW(NULL, folder, MAX_PATH) || FAILED(PathCchRemoveFileSpec(folder, MAX_PATH))) {
    fwprintf(stderr, L"moritz-cli: can't find its own folder\n");
    return 1;
  }

  wchar_t python[MAX_PATH];
  wchar_t script[MAX_PATH];
  StringCchPrintfW(python, MAX_PATH, L"%s\\%s\\python\\bin\\python.exe", folder, MORITZ_VERSION_DIR);
  StringCchPrintfW(script, MAX_PATH, L"%s\\%s\\scripts\\modules\\moritz_cli.py", folder, MORITZ_VERSION_DIR);
  if (GetFileAttributesW(python) == INVALID_FILE_ATTRIBUTES) {
    fwprintf(stderr, L"moritz-cli: Moritz's Python is missing: %s\n", python);
    return 1;
  }

  const wchar_t *args = arguments_after_program(GetCommandLineW());
  const size_t length = wcslen(python) + wcslen(script) + wcslen(args) + 32;
  wchar_t *command = (wchar_t *)HeapAlloc(GetProcessHeap(), 0, length * sizeof(wchar_t));
  if (command == NULL) {
    return 1;
  }
  /* -I: isolated from the user's Python (PYTHONPATH, user site-packages). */
  StringCchPrintfW(command, length, L"\"%s\" -I \"%s\" %s", python, script, args);

  STARTUPINFOW startup = {0};
  startup.cb = sizeof(startup);
  PROCESS_INFORMATION process = {0};
  if (!CreateProcessW(python, command, NULL, NULL, TRUE, 0, NULL, NULL, &startup, &process)) {
    fwprintf(stderr, L"moritz-cli: can't start %s (error %lu)\n", python, GetLastError());
    HeapFree(GetProcessHeap(), 0, command);
    return 1;
  }
  HeapFree(GetProcessHeap(), 0, command);

  WaitForSingleObject(process.hProcess, INFINITE);
  DWORD exit_code = 1;
  GetExitCodeProcess(process.hProcess, &exit_code);
  CloseHandle(process.hProcess);
  CloseHandle(process.hThread);
  return (int)exit_code;
}
