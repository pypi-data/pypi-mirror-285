from PySide6.QtCore import QCoreApplication


def tr(text: str) -> str:
    return QCoreApplication.translate("@default", text, None)


def translate(context, text, disambiguation=None) -> str:
    return QCoreApplication.translate(context, text, disambiguation)
