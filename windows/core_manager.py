"""Windows core manager with Admin UAC check, wintun.dll cwd binding, real netstat speed, and Dual-IP fetch."""
import json
import os
import re
import socket
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request
from pathlib import Path


def _resource_dir() -> Path:
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent


def is_windows_admin() -> bool:
    if sys.platform != "win32":
        return True
    try:
        import ctypes
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def relaunch_as_admin() -> bool:
    if sys.platform != "win32":
        return False
    try:
        import ctypes
        exe = sys.executable
        params = " ".join(f'"{a}"' for a in sys.argv) if not getattr(sys, "frozen", False) else ""
        ret = ctypes.windll.shell32.ShellExecuteW(None, "runas", exe, params, None, 1)
        return ret > 32
    except Exception:
        return False


def set_windows_proxy(enable: bool, proxy_addr: str = "127.0.0.1:10809") -> None:
    if sys.platform != "win32":
        return
    try:
        import ctypes
        import winreg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 1 if enable else 0)
            if enable:
                winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, proxy_addr)
                winreg.SetValueEx(key, "ProxyOverride", 0, winreg.REG_SZ, "localhost;127.*;10.*;192.168.*;<local>")
        ctypes.windll.Wininet.InternetSetOptionW(0, 39, 0, 0)
        ctypes.windll.Wininet.InternetSetOptionW(0, 37, 0, 0)
    except Exception:
        pass


def get_windows_net_bytes() -> tuple[int, int]:
    """Reads total (rx_bytes, tx_bytes) on Windows via netstat -e (zero external dependencies)."""
    try:
        flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        out = subprocess.check_output(["netstat", "-e"], text=True, errors="ignore", creationflags=flags)
        for line in out.splitlines():
            nums = re.findall(r"\b\d{4,}\b", line)
            if len(nums) >= 2:
                return int(nums[0]), int(nums[1])
    except Exception:
        pass
    return 0, 0


def measure_ping(host: str, port: int, timeout: float = 2.0) -> int | None:
    try:
        t0 = time.perf_counter()
        with socket.create_connection((host, port), timeout=timeout):
            return int((time.perf_counter() - t0) * 1000)
    except Exception:
        return None


def fetch_ip_info(via_local_proxy: bool = False) -> str:
    try:
        if via_local_proxy:
            handler = urllib.request.ProxyHandler({"http": "http://127.0.0.1:10809", "https": "http://127.0.0.1:10809"})
            opener = urllib.request.build_opener(handler)
            resp = opener.open("https://ipwho.is/", timeout=5)
        else:
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
            resp = opener.open("https://ipwho.is/", timeout=5)
        obj = json.loads(resp.read().decode("utf-8"))
        ip = obj.get("ip", "")
        cc = obj.get("country_code", "")
        city = obj.get("city", "")
        if ip:
            return f"{ip} • {city}, {cc}" if city else f"{ip} • {cc}"
    except Exception:
        pass
    return "—"


class CoreProcessManager:
    def __init__(self, on_log):
        self.on_log = on_log
        self.proc: subprocess.Popen | None = None
        self.aux_proc: subprocess.Popen | None = None
        self.cfg_file: Path | None = None
        self.aux_cfg_file: Path | None = None
        self.last_lines: list[str] = []
        self.aux_lines: list[str] = []

    def find_binary(self, core: str) -> Path | None:
        exe = "xray.exe" if core == "xray" else "sing-box.exe"
        for c in (_resource_dir() / "cores" / exe, Path.cwd() / "cores" / exe):
            if c.exists():
                return c
        return None

    def _wait_port(self, proc: subprocess.Popen, port: int, steps: int = 30) -> bool:
        for _ in range(steps):
            if proc.poll() is not None:
                return False
            try:
                with socket.create_connection(("127.0.0.1", port), timeout=0.1):
                    return True
            except Exception:
                time.sleep(0.1)
        return proc.poll() is None

    def start(
        self,
        core: str,
        config_json: str,
        use_system_proxy: bool = False,
        aux_xray_config: str | None = None,
    ) -> bool:
        self.stop()
        if sys.platform == "win32":
            for proc_name in ("sing-box.exe", "xray.exe"):
                try:
                    subprocess.run(
                        ["taskkill", "/F", "/IM", proc_name, "/T"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        creationflags=subprocess.CREATE_NO_WINDOW,
                    )
                except Exception:
                    pass

        self.last_lines = []
        self.aux_lines = []
        creation_flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0

        # Optional auxiliary Xray process (for XHTTP profiles chained behind sing-box Wintun TUN)
        if aux_xray_config:
            xray_bin = self.find_binary("xray")
            if not xray_bin:
                self.on_log("[ERROR] Не найден cores/xray.exe для XHTTP-цепочки.")
                return False
            fd_a, path_a = tempfile.mkstemp(prefix="albinvpn_xray_aux_", suffix=".json")
            os.close(fd_a)
            self.aux_cfg_file = Path(path_a)
            self.aux_cfg_file.write_text(aux_xray_config, encoding="utf-8")
            try:
                self.aux_proc = subprocess.Popen(
                    [str(xray_bin), "run", "-c", str(self.aux_cfg_file)],
                    cwd=str(xray_bin.parent),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    creationflags=creation_flags,
                )
                threading.Thread(target=self._read_logs, args=(self.aux_proc, True), daemon=True).start()
                if not self._wait_port(self.aux_proc, 10808, steps=25):
                    self.on_log(f"[ERROR] Вспомогательное ядро xray не запустилось (код {self.aux_proc.returncode}).")
                    self.stop()
                    return False
                self.on_log("[xray] Локальный XHTTP-транспорт готов (127.0.0.1:10808).")
            except Exception as exc:
                self.on_log(f"[ERROR] Ошибка запуска xray: {exc}")
                self.stop()
                return False

        binary = self.find_binary(core)
        if not binary:
            self.on_log(f"[ERROR] Не найден cores/{'xray.exe' if core == 'xray' else 'sing-box.exe'}. Запустите download_cores.ps1")
            self.stop()
            return False

        fd, path = tempfile.mkstemp(prefix=f"albinvpn_{core}_", suffix=".json")
        os.close(fd)
        self.cfg_file = Path(path)
        self.cfg_file.write_text(config_json, encoding="utf-8")

        cmd = [str(binary), "run", "-c", str(self.cfg_file)]
        try:
            self.proc = subprocess.Popen(
                cmd,
                cwd=str(binary.parent),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                creationflags=creation_flags,
            )
            threading.Thread(target=self._read_logs, args=(self.proc, False), daemon=True).start()
            if not self._wait_port(self.proc, 10809, steps=30):
                self.on_log(f"[ERROR] Ядро {core} завершилось (код {self.proc.returncode}).")
                self.stop()
                return False
            if use_system_proxy:
                set_windows_proxy(True, "127.0.0.1:10809")
                self.on_log("[Proxy] Системный прокси Windows включён (127.0.0.1:10809).")
            self.on_log(f"[{core}] Туннель запущен: {binary.name}")
            return True
        except Exception as exc:
            self.on_log(f"[ERROR] Ошибка запуска {core}: {exc}")
            self.stop()
            return False

    def _read_logs(self, proc: subprocess.Popen, is_aux: bool = False) -> None:
        if not proc or not proc.stdout:
            return
        for line in proc.stdout:
            s = re.sub(r"\x1b\[[0-9;]*m", "", line.rstrip())
            if is_aux:
                self.aux_lines = (self.aux_lines + [s])[-10:]
            else:
                self.last_lines = (self.last_lines + [s])[-10:]
            self.on_log(s)

    def stop(self) -> None:
        set_windows_proxy(False)
        for p in (self.proc, self.aux_proc):
            if p and p.poll() is None:
                p.terminate()
                try:
                    p.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    p.kill()
        self.proc = None
        self.aux_proc = None
        for f in (self.cfg_file, self.aux_cfg_file):
            if f and f.exists():
                try:
                    f.unlink()
                except Exception:
                    pass
        self.cfg_file = None
        self.aux_cfg_file = None
