from typing import Text


def escape_query(query: Text) -> Text:
    return query.replace("《", " ").replace("》", " ").strip()


def filter_out_extensions(
    url: Text,
    *,
    exclude_docs: bool = True,
    exclude_image: bool = True,
    exclude_audio: bool = True,
    exclude_video: bool = True,
    exclude_archive: bool = True,
    exclude_executable: bool = True,
    exclude_other: bool = True
) -> bool:
    if exclude_docs and url.endswith(
        (".pdf", ".docx", ".doc", ".pptx", ".xlsx", ".xls", ".ppt")
    ):
        return True
    if exclude_image and url.endswith(
        (".img", ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp")
    ):
        return True
    if exclude_audio and url.endswith((".mp3", ".wav", ".aac", ".flac", ".m4a")):
        return True
    if exclude_video and url.endswith((".mp4", ".avi", ".mov", ".wmv", ".flv", ".mkv")):
        return True
    if exclude_archive and url.endswith(
        (".rar", ".zip", ".7z", ".iso", ".dmg", ".pkg", ".deb", ".rpm", ".msi")
    ):
        return True
    if exclude_executable and url.endswith((".exe", ".app")):
        return True
    if exclude_other and url.endswith((".xml",)):
        return True
    return False
