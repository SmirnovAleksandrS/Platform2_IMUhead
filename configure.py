#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json, os, re, subprocess, sys
from typing import Any, Dict, List, Optional

ROOT  = os.path.dirname(os.path.abspath(__file__))
LOCK  = os.path.join(ROOT, "submodules_list.json")
LOCAL = os.path.join(ROOT, ".submodules_local.json")
GEN   = os.path.join(ROOT, "generated")
MK    = os.path.join(GEN, "third_party.mk")

# ---- makefile tail: aggregate & dedup (simple Inc/Src, non-recursive) ----
AGGREGATE_TAIL = r"""
# ---- aggregate fix & dedup (auto-appended by configure.py) ----
# Если export.mk не добавил пути/файлы, возьмём верхние Inc/Src
ifneq ($(strip $(INNER_PROTO_DIR)),)
  C_INCLUDES += -I$(INNER_PROTO_DIR)/Inc
  C_SOURCES  += $(wildcard $(INNER_PROTO_DIR)/Src/*.c) \
                $(wildcard $(INNER_PROTO_DIR)/Src/*.s) \
                $(wildcard $(INNER_PROTO_DIR)/Src/*.S)
endif

ifneq ($(strip $(MPU9250_LIB_DIR)),)
  C_INCLUDES += -I$(MPU9250_LIB_DIR)/Inc
  C_SOURCES  += $(wildcard $(MPU9250_LIB_DIR)/Src/*.c) \
                $(wildcard $(MPU9250_LIB_DIR)/Src/*.s) \
                $(wildcard $(MPU9250_LIB_DIR)/Src/*.S)
endif

ifneq ($(strip $(QMC5883_LIB_DIR)),)
  C_INCLUDES += -I$(QMC5883_LIB_DIR)/Inc
  C_SOURCES  += $(wildcard $(QMC5883_LIB_DIR)/Src/*.c) \
                $(wildcard $(QMC5883_LIB_DIR)/Src/*.s) \
                $(wildcard $(QMC5883_LIB_DIR)/Src/*.S)
endif

# Дедупликация (убираем повторы)
C_INCLUDES := $(sort $(C_INCLUDES))
C_SOURCES  := $(sort $(C_SOURCES))

# Отладка (можно закомментировать)
$(info [AGG] C_INCLUDES=$(C_INCLUDES))
$(info [AGG] C_SOURCES=$(C_SOURCES))
"""

def sh(cmd: List[str], cwd: Optional[str] = None) -> str:
    print("$", " ".join(cmd))
    return subprocess.check_output(cmd, cwd=cwd, text=True, stderr=subprocess.STDOUT).strip()

def ensure_dir(p: str) -> None:
    os.makedirs(p, exist_ok=True)

def abort(msg: str, code: int = 1) -> None:
    print(f"[error] {msg}")
    sys.exit(code)

def load_json(path: str, default: Any) -> Any:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return default
    except json.JSONDecodeError as e:
        abort(f"JSON error in {path}: {e}")

def sanitize_name(name: str) -> str:
    return re.sub(r"[^A-Z0-9_]", "_", (name or "").upper())

def is_abs_local_url(url: str) -> bool:
    return bool(url and (url.startswith(("local:", "path:", "file://")) or url.startswith("/")))

def url_to_local_path(url: str) -> str:
    if url.startswith("file://"): return url[len("file://"):]
    if url.startswith(("local:", "path:")): return url.split(":",1)[1]
    return url

def git_current_commit(cwd: str) -> str:
    try:
        return sh(["git", "rev-parse", "HEAD"], cwd=cwd)
    except subprocess.CalledProcessError:
        return ""

def git_ref_exists(cwd: str, ref: str) -> bool:
    try:
        sh(["git", "show-ref", "--verify", "--quiet", ref], cwd=cwd)
        return True
    except subprocess.CalledProcessError:
        return False

def clone_or_checkout(url: str, rev: str, dst: str) -> None:
    """Обновляет/клонирует репозиторий в dst и жёстко чекаутит rev."""
    ensure_dir(os.path.dirname(dst))

    if os.path.isdir(os.path.join(dst, ".git")):
        # Уже git — обновляем
        before = git_current_commit(dst)
        try:
            sh(["git", "fetch", "--tags", "--force", "--prune", "origin"], cwd=dst)
        except subprocess.CalledProcessError as e:
            print(e.output)

        target = rev
        if git_ref_exists(dst, f"refs/remotes/origin/{rev}"):
            target = f"origin/{rev}"
        elif git_ref_exists(dst, f"refs/tags/{rev}"):
            target = f"refs/tags/{rev}"

        sh(["git", "checkout", "--force", target], cwd=dst)
        sh(["git", "reset", "--hard"], cwd=dst)

        after = git_current_commit(dst)
        if before != after:
            print(f"[update] {os.path.basename(dst)}: {before[:8]} -> {after[:8]}")
        else:
            print(f"[up-to-date] {os.path.basename(dst)} @ {after[:8]}")
        return

    # Не git — клонируем
    try:
        sh(["git", "clone", "--depth", "1", "--branch", rev, url, dst])
    except subprocess.CalledProcessError:
        # rev может быть SHA — fallback-схема
        sh(["git", "clone", "--filter=blob:none", "--no-checkout", url, dst])
        sh(["git", "fetch", "--tags", "--force", "origin"], cwd=dst)
        if git_ref_exists(dst, f"refs/remotes/origin/{rev}"):
            sh(["git", "checkout", f"origin/{rev}"], cwd=dst)
        elif git_ref_exists(dst, f"refs/tags/{rev}"):
            sh(["git", "checkout", f"refs/tags/{rev}"], cwd=dst)
        else:
            sh(["git", "checkout", rev], cwd=dst)

def normalize_libs(raw_libs: Any) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    if isinstance(raw_libs, list):
        for v in raw_libs:
            if isinstance(v, dict):
                x = dict(v)
                if "name" not in x: abort(f"lib entry missing 'name': {x}")
                x["key"] = sanitize_name(x["name"])
                out.append(x)
        return out
    if isinstance(raw_libs, dict):
        for k, v in raw_libs.items():
            if isinstance(v, dict):
                x = dict(v)
                x.setdefault("name", k)
                x["key"] = sanitize_name(k)
                out.append(x)
        return out
    return out

def validate_lib_entry(item: Dict[str, Any]) -> None:
    for key in ("name", "url", "rev", "dst"):
        if key not in item: abort(f"lib entry missing '{key}': {item}")
    if not item["name"]: abort("lib 'name' must be non-empty")
    if not item["dst"]:  abort(f"lib '{item['name']}' has empty 'dst'")

def resolve_override(item: Dict[str, Any], overrides: Dict[str, str]) -> Optional[str]:
    raw_name = str(item["name"])
    var_name = sanitize_name(raw_name)
    dict_key = item.get("key", var_name)
    cand = overrides.get(raw_name) or overrides.get(var_name) or overrides.get(dict_key)
    if not cand: return None
    p = os.path.abspath(cand)
    if not os.path.isdir(p):
        abort(f"[override] {raw_name}: directory not found: {p}")
    return p

def main() -> None:
    data = load_json(LOCK, {})
    libs_raw = data.get("libs")
    libs = normalize_libs(libs_raw)
    if not libs:
        abort("submodules_list.json: expected non-empty 'libs' array or object")

    overrides = load_json(LOCAL, {}).get("overrides", {})
    if overrides:
        print(f"[info] overrides loaded: {', '.join(overrides.keys())}")
    else:
        print("[info] no overrides file or overrides empty")

    ensure_dir(GEN)
    lines = ["# Auto-generated by configure.py; do not edit\n"]
    seen = set()

    for item in libs:
        validate_lib_entry(item)
        raw_name = str(item["name"])
        var_name = sanitize_name(raw_name)
        if var_name in seen:
            abort(f"Duplicate library name after sanitization: {var_name}")
        seen.add(var_name)

        url = str(item["url"])
        rev = str(item["rev"])
        dst_rel = str(item["dst"])
        dst = os.path.join(ROOT, dst_rel)

        ov_dir = resolve_override(item, overrides)
        local_path = os.path.abspath(url_to_local_path(url)) if is_abs_local_url(url) else None
        dst_has_git = os.path.isdir(os.path.join(dst, ".git"))
        dst_has_export = os.path.isfile(os.path.join(dst, "export.mk"))
        is_vendored_copy = (dst_has_export and not dst_has_git)

        if ov_dir:
            print(f"[override] {raw_name} -> {ov_dir}")
            libdir = ov_dir
        elif local_path:
            print(f"[local-url] {raw_name} -> {local_path}")
            if not os.path.isdir(local_path):
                abort(f"[local-url] path not found: {local_path}")
            libdir = local_path
        elif dst_has_git:
            print(f"[update] {raw_name} @ {rev}")
            clone_or_checkout(url, rev, dst)  # обновим существующий репо
            libdir = dst
        elif is_vendored_copy:
            print(f"[vendored] {raw_name} -> {dst} (export.mk found; no .git, skip fetch)")
            libdir = dst
        else:
            print(f"[fetch] {raw_name} @ {rev}")
            clone_or_checkout(url, rev, dst)
            libdir = dst

        # Мягкое предупреждение
        exp = os.path.join(libdir, "export.mk")
        if not os.path.isfile(exp):
            print(f"[warn] {raw_name}: {exp} not found (build may miss files)")

        lines.append(f'{var_name}_DIR := {libdir}\n')
        lines.append(f'-include $({var_name}_DIR)/export.mk\n')

    # ---- пишем third_party.mk ----
    with open(MK, "w", encoding="utf-8") as f:
        f.writelines(lines)
        f.write(AGGREGATE_TAIL)
    print(f"Wrote {MK}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        abort("interrupted by user", 130)
