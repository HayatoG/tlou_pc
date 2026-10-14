#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Prepare and run The Last of Us Remastered (CUSA00552) through the native loader.

Shared by the command line (run_tlou.sh -> `tlou_run.py [seconds]`) and the launcher
window (tlou_launcher.py), so both start the game the same way:
  1. prepare.py / link_modules.py / content_profile.py build out/boot-linked.bin from the game
     folder (eboot + the game's own libc and Fios2; no console firmware module is needed);
  2. the defaults below become TLOU_* environment variables (each one validated in play);
  3. tlg-probe runs with its output in out/logs/run-<date>.log (last_run.log points to it).
"""
import datetime
import json
import os
from pathlib import Path
import subprocess
import sys

# A packaged build (PyInstaller) keeps its folders next to the executable: scripts/, out/, user/.
FROZEN = bool(getattr(sys, 'frozen', False))
PORT_DIR = Path(sys.executable).resolve().parent if FROZEN else Path(__file__).resolve().parent.parent
REPO_DIR = PORT_DIR.parent
OUT_DIR = PORT_DIR / 'out'
USER_DIR = PORT_DIR / 'user'
LOG_DIR = OUT_DIR / 'logs'
PROBE = OUT_DIR / ('tlg-probe.exe' if os.name == 'nt' else 'tlg-probe')
KEEP_LOGS = 30

# Game language: PS4 system language ids (sceSystemServiceParamGetInt LANG). The list the game
# really ships voice/text for is still to be checked against the dump.
GAME_LANGUAGES = {'en': 1, 'pt_BR': 17, 'es_LA': 20, 'fr_CA': 22}

# TLG core defaults (the reasons are in each comment; still to be validated on this game).
DEFAULT_ENV = {
    'TLOU_PIPELINE_BINARIES': '0',  # VK_KHR_pipeline_binary crashes on the NVIDIA 595 driver
    'TLOU_GC_BUDGET_MB': '3500',    # texture cache budget; 5600 exhausts 6 GB of VRAM in TLOU
    'TLOU_UPSCALER': 'off',         # native image: GoW3's temporal upscalers made it shake
    'TLOU_JITTER': '0',
    'TLOU_OBJECT_MOTION': '0',
    'TLOU_FRAME_STATS': '1',        # FPS in the log every 5 s (scripts/watch_session.sh heartbeat)
}

# The game's own modules from sce_module/, linked into the image.
MODULES = ['libc.prx', 'libSceFios2.prx']

DEFAULT_SETTINGS = {
    # Source tree: the merged game view (base 1.00 + update 1.11). Package: the player picks it.
    'game_dir': '' if FROZEN else str(REPO_DIR / 'game' / 'CUSA00552'),
    'game_language': 'pt_BR',
    'ui_language': 'auto',         # auto | pt_BR | en_US
    'show_fps': False,
    'display_mode': 'Windowed',    # Windowed | Borderless | Fullscreen (tlg.ini)
    'vsync': True,
    'vram_budget_mb': 3500,  # 5600 runs out of VRAM loading the first level (RTX 2060, 6 GB)
    'stick_deadzone': 10,    # percent; runtime_pad.c TLOU_STICK_DEADZONE
    'eager_readback': False,  # TLOU_EAGER_READBACK (off: stale EOP marker hangs the first gameplay frame): copy GPU results the game reads back at each fence
    'write_merge': False,     # TLOU_WRITE_MERGE (off with eager readback): game memcpy/memset into GPU memory without a GPU wait
    'gpu_readbacks': '2',    # 2 precise: GPU particles (smoke to drain) need it; 0 fast skips them
}


def config_path():
    base = Path(os.environ.get('APPDATA') or os.environ.get('XDG_CONFIG_HOME') or Path.home() / '.config')
    return base / 'tlou-launcher' / 'settings.json'


def load_settings():
    settings = dict(DEFAULT_SETTINGS)
    try:
        settings.update(json.loads(config_path().read_text(encoding='utf-8')))
    except (OSError, ValueError):
        pass
    return settings


def save_settings(settings):
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(settings, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def check_game(game_dir):
    """Problems that keep the game from starting, as (key, detail) pairs; empty means ready."""
    game = Path(game_dir)
    problems = []
    if not (game / 'eboot.bin').is_file():
        problems.append(('missing', 'eboot.bin'))
    for module in MODULES:
        if not (game / 'sce_module' / module).is_file():
            problems.append(('missing', f'sce_module/{module}'))
    if not PROBE.is_file():
        problems.append(('not_built', str(PROBE)))
    return problems


def update_ini(path, values):
    """Sets keys in tlg.ini (the in-game menu's file), keeping every other line."""
    lines = path.read_text(encoding='utf-8').splitlines() if path.is_file() else ['# tlg settings']
    seen = set()
    for i, line in enumerate(lines):
        key = line.split('=', 1)[0].strip()
        if key in values:
            lines[i] = f'{key}={values[key]}'
            seen.add(key)
    lines += [f'{k}={v}' for k, v in values.items() if k not in seen]
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def python_command(script):
    """How to run one of scripts/*.py: the packaged executable runs them itself (--script)."""
    if FROZEN:
        return [sys.executable, '--script', str(script)]
    return [sys.executable, str(script)]


def attach_stdio():
    """A windowed Windows executable starts without sys.stdout; inherited pipes still exist."""
    if os.name != 'nt':
        return
    import ctypes
    import msvcrt
    for name, std in (('stdout', -11), ('stderr', -12)):
        if getattr(sys, name) is not None:
            continue
        stream = None
        handle = ctypes.windll.kernel32.GetStdHandle(std)
        if handle and handle != ctypes.c_void_p(-1).value:
            try:
                stream = open(msvcrt.open_osfhandle(handle, os.O_WRONLY), 'w', encoding='utf-8',
                              errors='replace', buffering=1)
            except OSError:
                stream = None
        setattr(sys, name, stream or open(os.devnull, 'w'))


NO_WINDOW = getattr(subprocess, 'CREATE_NO_WINDOW', 0)  # no console flashing for the scripts


def run_script(argv):
    """--script <path> [args]: runs a preparation script inside the packaged executable."""
    import runpy
    attach_stdio()
    script = Path(argv[0])
    sys.argv = [str(script), *argv[1:]]
    sys.path.insert(0, str(script.parent))
    try:
        runpy.run_path(str(script), run_name='__main__')
    except SystemExit as stop:
        return stop.code if isinstance(stop.code, int) else (0 if stop.code is None else 1)
    return 0


def prepare(settings, log=print):
    """Builds out/boot-linked.bin and out/content.bin; returns the module list that was linked."""
    game = settings['game_dir']
    scripts = PORT_DIR / 'scripts'
    modules = list(MODULES)
    steps = [
        [*python_command(scripts / 'prepare.py'), game, '--out', str(OUT_DIR)],
        [*python_command(scripts / 'link_modules.py'), game, '--out', str(OUT_DIR), '--modules', *modules],
        [*python_command(scripts / 'content_profile.py'), game, '--out', str(OUT_DIR)],
    ]
    for step in steps:
        result = subprocess.run(step, cwd=str(scripts), capture_output=True, text=True,
                                creationflags=NO_WINDOW)
        if result.returncode:
            name = next(Path(arg).name for arg in step if arg.endswith('.py'))
            raise RuntimeError(f'{name}: {result.stderr.strip() or result.stdout.strip()}')
        for line in result.stdout.splitlines():
            log(line)
    isa_table(log)
    return modules


ISA_TABLE = OUT_DIR / 'isa-rewrite.bin'


def cpu_missing_sets():
    """Instruction sets `tlg-probe --cpu-features` reports missing ([] when complete). A CPU that
    lacks a set nothing can rewrite (AVX and older) stops here (exit 20) with the probe's reason."""
    try:
        result = subprocess.run([str(PROBE), '--cpu-features'], stdin=subprocess.DEVNULL, capture_output=True,
                                text=True, timeout=30, creationflags=NO_WINDOW)
    except (OSError, subprocess.SubprocessError):
        return []  # no probe yet: check_game reports it
    if result.returncode == 20:
        raise RuntimeError(result.stdout.strip() or 'this CPU cannot run the game')
    for line in result.stdout.splitlines():
        if line.startswith('CPU: missing '):
            return [name.strip() for name in line[len('CPU: missing '):].split(',') if name.strip()]
    return []


def isa_table(log=print):
    """ps4_core ISA rewrite (upstream gow3_pc #129): on a CPU without MOVBE, BMI1 or LZCNT the
    probe replaces those instructions in the image, from the table scripts/isa_rewrite.py writes
    (iced-x86). TLOU_ISA_REWRITE=1 builds it on any CPU (testing), =0 never. A failed table is
    reported and the probe then explains what is missing."""
    ISA_TABLE.unlink(missing_ok=True)  # always matches the boot-linked.bin just written
    policy = os.environ.get('TLOU_ISA_REWRITE')
    missing = cpu_missing_sets()
    if not (policy == '1' or (policy != '0' and missing)):
        return
    scripts = PORT_DIR / 'scripts'
    result = subprocess.run([*python_command(scripts / 'isa_rewrite.py'), str(OUT_DIR / 'boot-linked.bin'),
                             '--out', str(OUT_DIR)], cwd=str(scripts), capture_output=True, text=True,
                            creationflags=NO_WINDOW)
    for line in (result.stdout + result.stderr).splitlines():
        log(line)


def window_icon(settings):
    """The game's own icon0.png converted to BMP (SDL's built-in format) in out/; None if absent."""
    source = Path(settings['game_dir']) / 'sce_sys' / 'icon0.png'
    target = OUT_DIR / 'window_icon.bmp'
    try:
        # Stamped with the source's time: a different dump (or a copy keeping old times) redoes it.
        if source.is_file() and (not target.is_file() or target.stat().st_mtime != source.stat().st_mtime):
            from PIL import Image  # optional: without Pillow the window keeps the default icon
            OUT_DIR.mkdir(parents=True, exist_ok=True)
            Image.open(source).convert('RGB').resize((128, 128)).save(target)
            os.utime(target, (source.stat().st_atime, source.stat().st_mtime))
        return target if target.is_file() else None
    except Exception:
        return None


def pad_glyphs():
    """TLOU_GLYPHS for the in-game menu (xbox or nintendo button names) from the first controller
    `tlg-probe --gamepad` finds; None for PlayStation pads, none attached or when it fails.
    TLOU_GLYPHS in the environment (playstation, xbox, nintendo) skips the question."""
    if os.environ.get('TLOU_GLYPHS'):
        return None
    try:
        out = subprocess.run([str(PROBE), '--gamepad'], stdin=subprocess.DEVNULL, capture_output=True,
                             text=True, timeout=10, creationflags=NO_WINDOW).stdout
    except (OSError, subprocess.SubprocessError):
        return None
    for line in out.splitlines():
        if line.startswith('Gamepad: type='):
            kind = line.split()[1][len('type='):]
            return 'xbox' if kind.startswith('xbox') else 'nintendo' if kind.startswith(('switch', 'joycon')) else None
    return None


def build_env(settings, extra=None):
    env = dict(os.environ)
    for key, value in DEFAULT_ENV.items():
        env.setdefault(key, value)  # explicit TLOU_* in the environment always win
    env['TLOU_GC_BUDGET_MB'] = os.environ.get('TLOU_GC_BUDGET_MB', str(int(settings['vram_budget_mb'])))
    env['TLOU_READBACKS'] = os.environ.get('TLOU_READBACKS', str(settings.get('gpu_readbacks', '2')))
    env['TLOU_EAGER_READBACK'] = os.environ.get('TLOU_EAGER_READBACK', '1' if settings.get('eager_readback', False) else '0')
    env['TLOU_WRITE_MERGE'] = os.environ.get('TLOU_WRITE_MERGE', '1' if settings.get('write_merge', False) else '0')
    env['TLOU_STICK_DEADZONE'] = os.environ.get('TLOU_STICK_DEADZONE', f"{int(settings.get('stick_deadzone', 10)) / 100:.2f}")
    env['TLOU_LANGUAGE'] = os.environ.get('TLOU_LANGUAGE', str(GAME_LANGUAGES.get(settings['game_language'], 1)))
    if settings.get('ui_language', 'auto') != 'auto':
        env['TLOU_UI_LANG'] = settings['ui_language']
    env['TLOU_CONFIG'] = str(USER_DIR / 'tlg.ini')
    # Window name, app id (matches tlou-pc.desktop for Alt+Tab and the dock) and icon.
    env.setdefault('TLOU_APP_NAME', 'The Last of Us Remastered')
    env.setdefault('TLOU_APP_ID', 'tlou-pc')
    icon = window_icon(settings)
    if icon:
        env.setdefault('TLOU_WINDOW_ICON', str(icon))
    glyphs = pad_glyphs()
    if glyphs:
        env.setdefault('TLOU_GLYPHS', glyphs)
    restart = f'"{sys.executable}" --play' if FROZEN else f'"{sys.executable}" "{Path(__file__).resolve()}"'
    env.setdefault('TLOU_RESTART_COMMAND', restart)
    # Linux package: the libraries built with the port (SDL3, FFmpeg, ...) are in out/lib.
    bundled = OUT_DIR / 'lib'
    if os.name != 'nt' and bundled.is_dir():
        env['LD_LIBRARY_PATH'] = os.pathsep.join(filter(None, [str(bundled), os.environ.get('LD_LIBRARY_PATH')]))
    if extra:
        env.update(extra)
    return env


def new_log():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log = LOG_DIR / f'run-{datetime.datetime.now():%Y%m%d-%H%M%S}.log'
    latest = OUT_DIR / 'last_run.log'
    try:
        if latest.is_symlink() or latest.exists():
            latest.unlink()
        latest.symlink_to(log)
    except OSError:
        pass
    for old in sorted(LOG_DIR.glob('run-*.log'), reverse=True)[KEEP_LOGS:]:
        old.unlink(missing_ok=True)
    return log


def launch(settings, seconds=0, extra_env=None):
    """Writes the in-game settings, starts the game; returns (process, log path).
    The process's combined output is a text pipe; the caller copies it to the log."""
    USER_DIR.mkdir(parents=True, exist_ok=True)
    update_ini(USER_DIR / 'tlg.ini', {
        'display_mode': settings['display_mode'],
        'vsync': int(bool(settings['vsync'])),
        'show_fps': int(bool(settings['show_fps'])),
    })
    log = new_log()
    cmd = [str(PROBE), str(OUT_DIR / 'boot-linked.bin'), '--app0', settings['game_dir'],
           '--user', str(USER_DIR), '--content-profile', str(OUT_DIR / 'content.bin'),
           '--timeout', str(int(seconds))]
    if ISA_TABLE.is_file():
        cmd += ['--isa-rewrite', str(ISA_TABLE)]
    process = subprocess.Popen(cmd, cwd=str(USER_DIR), env=build_env(settings, extra_env),
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                               encoding='utf-8', errors='replace', bufsize=1)
    return process, log


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    attach_stdio()
    seconds = int(argv[0]) if argv and argv[0].isdigit() else 0
    settings = load_settings()
    if os.environ.get('TLOU_GAME_DIR'):
        settings['game_dir'] = os.environ['TLOU_GAME_DIR']
    problems = check_game(settings['game_dir'])
    if problems:
        for kind, detail in problems:
            print(f'{"Compile primeiro" if kind == "not_built" else "Faltando"}: {detail}', file=sys.stderr)
        return 1
    prepare(settings, log=lambda line: None)
    process, log = launch(settings, seconds)
    print(f'Rodando (log: {log})', flush=True)
    with open(log, 'w', encoding='utf-8') as out:
        for line in process.stdout:
            sys.stdout.write(line)
            out.write(line)
            out.flush()
    return process.wait()


if __name__ == '__main__':
    sys.exit(main())
