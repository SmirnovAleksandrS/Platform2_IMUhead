#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import sys
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
MAKEFILE = os.path.join(ROOT, "STM32Make.make")

def run_build():
    cmd = ["make", "-rR", "-j16", "-f", MAKEFILE, "all"]
    print(">>> Запуск сборки:", " ".join(cmd))
    try:
        subprocess.check_call(cmd, cwd=ROOT)
        print(">>> Сборка завершена успешно ✅")
    except subprocess.CalledProcessError as e:
        print(f">>> Ошибка при сборке (код {e.returncode}) ❌")
        sys.exit(e.returncode)

if __name__ == "__main__":
    run_build()
