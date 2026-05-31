"""Smoke test for the PySide6 Windows 11 processing layout."""

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from PySide6.QtCore import QEventLoop, QThread, QTimer  # noqa: E402
from PySide6.QtWidgets import QApplication, QScrollArea  # noqa: E402

from src.gui.modern_gui_win11 import ModelLoadingThread, StockPrepWin11App  # noqa: E402


class FakeModelManager:
    display_name = "fake"

    def cargar_modelo(self, callback=None):
        if callback:
            callback("fake progress")
        return True


def main() -> int:
    app = QApplication.instance() or QApplication([])
    window = StockPrepWin11App()
    window.resize(1200, 800)
    window.show()
    app.processEvents()

    combo_heights = {
        "model_profile_combo": window.model_profile_combo.height(),
        "processing_mode_combo": window.processing_mode_combo.height(),
    }
    for name, height in combo_heights.items():
        if height < 34:
            raise AssertionError(f"{name} is too short: {height}px")

    if window.model_profile_combo.count() < 2:
        raise AssertionError("Model selector should expose multiple profiles")

    if not window.model_profile_combo.isEnabled():
        raise AssertionError("Model selector should be enabled before loading a model")

    if not window.findChildren(QScrollArea):
        raise AssertionError("Left processing panel should live inside a scroll area")

    thread_result = []
    thread_errors = []
    loop = QEventLoop()
    thread = ModelLoadingThread(FakeModelManager())
    thread.completed.connect(lambda success: (thread_result.append(success), loop.quit()))
    thread.error.connect(lambda message: (thread_errors.append(message), loop.quit()))
    QTimer.singleShot(3000, loop.quit)
    thread.start(QThread.Priority.LowPriority)
    loop.exec()
    thread.wait(1000)
    if thread_errors:
        raise AssertionError(f"Model loading thread emitted an error: {thread_errors[0]}")
    if thread_result != [True]:
        raise AssertionError("Model loading thread did not emit completed=True")

    print(
        "layout-ok",
        f"models={window.model_profile_combo.count()}",
        f"model_combo={combo_heights['model_profile_combo']}px",
        f"mode_combo={combo_heights['processing_mode_combo']}px",
    )
    window.close()
    app.processEvents()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
