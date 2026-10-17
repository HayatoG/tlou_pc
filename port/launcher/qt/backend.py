# SPDX-License-Identifier: GPL-2.0-or-later
"""The QObject the QML screens talk to. All real work is delegated to the modules the Tk
launcher uses (tlou_run: prepare/launch/save_settings/check_game/shader_cache_size).

Unlike inFAMOUS's launcher, TLOU has no backports/advanced-tuning menu system today, so this
stays close to what the Tk launcher already offers: game folder, language, video settings,
controller dead zone, shader cache, and mods/cheats (mod_patches.py)."""
import os
import threading
from pathlib import Path

from PySide6.QtCore import Property, QObject, QUrl, Signal, Slot

from . import logic
from .logic import tlg_run
import shader_cache  # noqa: E402  (same directory as tlou_run.py, already on sys.path)

URLS = {'channel': 'https://www.youtube.com/@hayatog-dev', 'discord': 'https://discord.gg/UMkdMYZh9g',
        'sponsor': 'https://github.com/sponsors/HayatoG'}

DISPLAY_MODES = ('Windowed', 'Borderless', 'Fullscreen')


def _art(settings, name):
    """Official art from the player's own dump (sce_sys); never shipped with the port."""
    for folder in (Path(settings.get('game_dir', '')) / 'sce_sys', tlg_run.REPO_DIR / 'dump' / 'sce_sys'):
        try:
            if (folder / name).is_file():
                return folder / name
        except OSError:
            pass
    return None


def _row(rid, label='', what='', control='switch', changed=False, **extra):
    row = {'kind': 'item', 'id': rid, 'label': label, 'what': what, 'tags': [], 'shaderWarn': '',
           'changed': changed, 'control': control, 'on': False, 'options': [], 'index': 0,
           'lo': 0, 'hi': 0, 'step': 1, 'unit': '', 'value': 0, 'valueText': '', 'disabled': False,
           'decimals': 0, 'note': '', 'info': '', 'action': None}
    row.update(extra)
    return row


class Backend(QObject):
    langChanged = Signal()
    stateChanged = Signal()
    gameDirChanged = Signal()
    logChanged = Signal()
    chipsChanged = Signal()
    gpuFound = Signal(object)
    lineReceived = Signal(str)
    finished = Signal(int)
    modsChanged = Signal()
    graphicsChanged = Signal()
    controlsChanged = Signal()

    def __init__(self, settings=None, translator=None, probes=None):
        """probes: optional dict of callables replacing the slow/hardware ones (tests, screenshots)."""
        super().__init__()
        self.settings = tlg_run.load_settings() if settings is None else settings
        self.t_ = translator or logic.Translator(self.settings)
        self.probes = probes or {}
        self.fonts = ('sans-serif', 'sans-serif')  # app.py puts the loaded families here
        self._gpu = 'checking'
        self._chips, self._ready = [], False
        self._play_state = 'idle'
        self._log = []
        self._news = []
        self._message = ''
        self.process = None
        self.gpuFound.connect(self._on_gpu)
        self.lineReceived.connect(self._on_line)
        self.finished.connect(self._on_finished)
        self.refresh()

    # -- fonts (set by app.py) -----------------------------------------------------------------
    @Property(str, constant=True)
    def fontDisplay(self):
        return self.fonts[0]

    @Property(str, constant=True)
    def fontText(self):
        return self.fonts[1]

    @Property(bool, constant=True)
    def reducedMotion(self):
        return bool(os.environ.get('TLOU_QT_REDUCED_MOTION'))

    @Property(bool, constant=True)
    def logShown(self):
        return False

    # -- helpers --------------------------------------------------------------------------------
    def probe(self, name, default):
        return self.probes[name]() if name in self.probes else default()

    def start_probes(self):
        """GPU/Vulkan detection runs off the UI thread."""
        def work():
            self.gpuFound.emit(self.probe('gpu', logic.detect_gpu))
        threading.Thread(target=work, daemon=True).start()

    def _on_gpu(self, gpu):
        self._gpu = gpu
        self.refresh()

    def refresh(self):
        problems = self.probe('problems', lambda: tlg_run.check_game(self.settings.get('game_dir', '')))
        cache = self.probes['cache']() if 'cache' in self.probes else None
        self._chips, self._ready = logic.compute_chips(self.settings, self.t_, gpu=self._gpu,
                                                        problems=problems, cache_bytes=cache)
        self._news = self.probe('news', lambda: logic.news(self.t_, self.t_.pt()))
        self.chipsChanged.emit()
        self.stateChanged.emit()
        self.gameDirChanged.emit()
        self.graphicsChanged.emit()
        self.controlsChanged.emit()

    def shutdown(self):
        if self.process:
            try:
                self.process.terminate()
            except Exception:
                pass

    # -- text -------------------------------------------------------------------------------------
    @Slot(str, result=str)
    def t(self, key):
        return self.t_(key)

    @Slot(str, 'QVariantMap', result=str)
    def tf(self, key, args):
        return self.t_(key, **args)

    @Property(str, notify=langChanged)
    def lang(self):
        return 'pt_BR' if self.t_.pt() else 'en_US'

    @Slot(str)
    def setLang(self, lang):
        self.settings['ui_language'] = lang
        tlg_run.save_settings(self.settings)
        self.langChanged.emit()
        self.refresh()

    # -- home state -------------------------------------------------------------------------------
    @Property('QVariantList', notify=chipsChanged)
    def chips(self):
        return self._chips

    @Property(str, notify=stateChanged)
    def statusTitle(self):
        return self.t_('status_ready' if self._ready else 'status_attention')

    @Property('QVariantList', notify=stateChanged)
    def newsLines(self):
        return self._news

    @Property(str, notify=stateChanged)
    def version(self):
        return self.probe('version', logic.release_version)

    @Property(str, notify=stateChanged)
    def heroKicker(self):
        serial = shader_cache_title(self.settings) or 'CUSA00552'
        return self.t_('hero_kicker', serial=serial)

    @Property(str, notify=stateChanged)
    def playSubtitle(self):
        if self._play_state == 'launching':
            return self.t_('play_launching')
        if self._play_state == 'running':
            return self.t_('play_running')
        if not self.canPlay:
            return self.t_('play_blocked')
        return self.t_('play_new')

    @Property(bool, notify=stateChanged)
    def canPlay(self):
        return self._ready and self._play_state == 'idle'

    @Property(str, notify=stateChanged)
    def playState(self):
        return self._play_state

    @Property(bool, notify=stateChanged)
    def showFirstRun(self):
        try:
            return not tlg_run.shader_cache_size(self.settings) if 'cache' not in self.probes else not self.probes['cache']()
        except Exception:
            return False

    @Property(str, notify=gameDirChanged)
    def gameDir(self):
        return self.settings.get('game_dir', '')

    @Property(str, notify=gameDirChanged)
    def artSource(self):
        """pic1.png of the player's own dump (never shipped); empty when absent."""
        for name in ('pic1.png', 'pic0.png'):
            path = _art(self.settings, name)
            if path:
                return QUrl.fromLocalFile(str(path)).toString()
        return ''

    @Property(str, notify=logChanged)
    def logText(self):
        return '\n'.join(self._log[-400:])

    @Property(str, notify=stateChanged)
    def notice(self):
        return self._message

    # -- game folder ------------------------------------------------------------------------------
    @Slot(str)
    def chooseFolder(self, url):
        path = QUrl(url).toLocalFile() if url.startswith('file:') else url
        if not path:
            return
        problems = tlg_run.check_game(path) if 'problems' not in self.probes else []
        game_problems = [p for p in problems if p[0] != 'not_built']
        if game_problems:
            self._message = self.t_('folder_rejected', why=logic.game_problem_text(self.t_, game_problems))
        else:
            self.settings['game_dir'] = path
            tlg_run.save_settings(self.settings)
            self._message = self.t_('folder_saved')
        self.refresh()

    @Slot()
    def clearNotice(self):
        self._message = ''
        self.stateChanged.emit()

    @Slot(str)
    def openUrl(self, name):
        import webbrowser
        webbrowser.open(URLS[name])

    # -- game language (voice and text) ------------------------------------------------------------
    @Property('QVariantList', notify=gameDirChanged)
    def gameLanguageOptions(self):
        return [{'value': k, 'label': logic.GAME_LANGUAGE_NAMES.get(k, k)} for k in tlg_run.GAME_LANGUAGES]

    @Property(int, notify=gameDirChanged)
    def gameLanguageIndex(self):
        keys = list(tlg_run.GAME_LANGUAGES)
        current = self.settings.get('game_language', 'pt_BR')
        return keys.index(current) if current in keys else 0

    @Slot(str)
    def setGameLanguage(self, key):
        self.settings['game_language'] = key
        tlg_run.save_settings(self.settings)
        self.gameDirChanged.emit()

    # -- play (same path as the Tk launcher: prepare() then launch()) -------------------------------
    @Slot()
    def play(self):
        if self._play_state != 'idle' or not self._ready:
            return
        tlg_run.save_settings(self.settings)
        self._play_state = 'launching'
        self._log = [self.t_('preparing')]
        self.logChanged.emit()
        self.stateChanged.emit()
        threading.Thread(target=self._run_game, daemon=True).start()

    def _run_game(self):
        try:
            tlg_run.prepare(self.settings, log=lambda line: self.lineReceived.emit(line))
            self.process, log = tlg_run.launch(self.settings)
        except Exception as error:  # shown to the player; the launcher keeps running
            self.lineReceived.emit(str(error))
            self.finished.emit(-1000)
            return
        self.lineReceived.emit(f"{self.t_('running')} {log}")
        self._play_state = 'running'
        self.stateChanged.emit()
        with open(log, 'w', encoding='utf-8') as out:
            for line in self.process.stdout:
                out.write(line)
                out.flush()
                self.lineReceived.emit(line.rstrip('\n'))
        code = self.process.wait()
        self.process = None
        self.finished.emit(code)

    def _on_line(self, line):
        self._log.append(line)
        del self._log[:-2000]
        self.logChanged.emit()

    def _on_finished(self, code):
        self._play_state = 'idle'
        if code != -1000:
            self._log.append(self.t_('ended' if code in (0, -15) else 'crashed', code=code))
            self.logChanged.emit()
        self.refresh()

    # -- graphics ---------------------------------------------------------------------------------
    @Property('QVariantList', notify=graphicsChanged)
    def graphicsRows(self):
        s, d = self.settings, tlg_run.DEFAULT_SETTINGS
        t = self.t_
        rows = [{'kind': 'header', 'id': 'hdr-image', 'title': t('gfx_sec_image'), 'note': ''},
                _row('display_mode', t('display_mode'), '', 'combo',
                     s.get('display_mode') != d['display_mode'],
                     options=[{'value': m, 'label': t(m)} for m in DISPLAY_MODES],
                     index=DISPLAY_MODES.index(s.get('display_mode', 'Windowed'))
                     if s.get('display_mode') in DISPLAY_MODES else 0),
                _row('vsync', t('vsync'), '', 'switch', s.get('vsync') != d['vsync'], on=bool(s.get('vsync'))),
                _row('show_fps', t('show_fps'), '', 'switch', s.get('show_fps') != d['show_fps'],
                     on=bool(s.get('show_fps'))),
                {'kind': 'header', 'id': 'hdr-gpu', 'title': t('gfx_sec_gpu'), 'note': ''},
                _row('gpu_readbacks', t('gpu_readbacks'), t('gfx_what_gpu_readbacks'), 'combo',
                     s.get('gpu_readbacks') != d['gpu_readbacks'],
                     options=[{'value': v, 'label': t('readbacks_' + v)} for v in ('0', '1', '2')],
                     index=('0', '1', '2').index(str(s.get('gpu_readbacks', '2')))
                     if str(s.get('gpu_readbacks')) in ('0', '1', '2') else 2),
                _row('eager_readback', t('eager_readback'), t('gfx_what_eager_readback'), 'switch',
                     s.get('eager_readback') != d['eager_readback'], on=bool(s.get('eager_readback'))),
                _row('write_merge', t('write_merge'), t('gfx_what_write_merge'), 'switch',
                     s.get('write_merge') != d['write_merge'], on=bool(s.get('write_merge'))),
                {'kind': 'header', 'id': 'hdr-vram', 'title': t('gfx_sec_vram'), 'note': ''},
                _row('vram_budget_mb', t('vram'), t('vram_hint'), 'slider',
                     int(s.get('vram_budget_mb', 0)) != d['vram_budget_mb'], lo=1500, hi=24000, step=100,
                     value=int(s.get('vram_budget_mb', d['vram_budget_mb'])),
                     valueText=f"{int(s.get('vram_budget_mb', d['vram_budget_mb']))} MB")]
        return rows

    @Slot(str, str)
    def setGraphics(self, rid, value):
        s = self.settings
        if rid == 'display_mode':
            s[rid] = value
        elif rid in ('vsync', 'show_fps', 'eager_readback', 'write_merge'):
            s[rid] = value == '1'
        elif rid == 'gpu_readbacks':
            s[rid] = value
        elif rid == 'vram_budget_mb':
            s[rid] = min(max(int(float(value)), 1500), 24000)
        else:
            return
        tlg_run.save_settings(s)
        self.graphicsChanged.emit()
        self.stateChanged.emit()

    @Property(bool, notify=stateChanged)
    def canClear(self):
        try:
            return bool(tlg_run.shader_cache_size(self.settings)) and self._play_state == 'idle'
        except Exception:
            return False

    @Slot()
    def clearCache(self):
        if self._play_state != 'idle':
            return
        try:
            freed, failures = tlg_run.clear_shader_cache(self.settings)
            human = shader_cache.human_size(freed)
            self._message = (self.t_('clear_cache_failed', size=human, count=len(failures)) if failures
                             else self.t_('clear_cache_done', size=human))
        except Exception as error:
            self._message = str(error)
        self.refresh()

    # -- controls (stick dead zone; everything else is the same as every other port's) --------------
    @Property('QVariantList', notify=controlsChanged)
    def controlsRows(self):
        s, d, t = self.settings, tlg_run.DEFAULT_SETTINGS, self.t_
        zone = int(s.get('stick_deadzone', d['stick_deadzone']))
        return [_row('stick_deadzone', t('deadzone'), t('deadzone_hint'), 'slider',
                     zone != d['stick_deadzone'], lo=0, hi=40, step=1, unit='%', value=zone,
                     valueText=f'{zone}%')]

    @Slot(str, str)
    def setControls(self, rid, value):
        if rid == 'stick_deadzone':
            self.settings['stick_deadzone'] = min(max(int(float(value)), 0), 40)
            tlg_run.save_settings(self.settings)
            self.controlsChanged.emit()

    # -- mods/cheats -----------------------------------------------------------------------------
    @Property('QVariantList', notify=modsChanged)
    def modsModel(self):
        """Every shadPS4/GoldHEN cheat XML found in the mods folder for this game's version,
        with its current enabled state. Nothing here has any effect until turned on."""
        try:
            mods = tlg_run.list_mods(self.settings)
        except Exception:
            mods = []
        return [{'key': key, 'name': name or key, 'note': note or '', 'on': bool(enabled)}
                for key, name, note, enabled in mods]

    @Slot(str, bool)
    def setModEnabled(self, key, enabled):
        tlg_run.set_mod_enabled(key, enabled)
        self.modsChanged.emit()

    @Slot()
    def refreshMods(self):
        self.modsChanged.emit()

    @Slot()
    def openModsFolder(self):
        from PySide6.QtGui import QDesktopServices
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(tlg_run.mods_dir())))


def shader_cache_title(settings):
    try:
        return shader_cache.title_id(settings.get('game_dir', ''))
    except Exception:
        return None
