from typing import Text


def escape_query(query: Text) -> Text:
    q = (
        query.replace('"', "")
        .replace("'", "")
        .replace("《", " ")
        .replace("》", " ")
        .strip()
    )
    if not q:
        raise ValueError("Query is empty")
    return q


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


def filter_out_urls(url: Text) -> bool:
    return (
        "open.spotify.com" in url
        or "www.tiktok.com" in url
        or "tunebat.com" in url
        or "quizlet.com" in url
        or "taobao.com" in url
        or "douyin.com" in url
        or "pinduoduo.com" in url
        or "xiaohongshu.com" in url
        or "jd.com" in url
        or "tmall.com" in url
        or "1688.com" in url
        or "smzdm.com" in url
        or "meituan.com" in url
        or "dianping.com" in url
        or "vip.com" in url
        or "vmall.com" in url
        or "suning.com" in url
        or "dangdang.com" in url
        or "arco.org.tw" in url
        or "www.cs.cmu.edu" in url
        or "www.oldies.com" in url
        or "www.hitfm.com.tw" in url
        or "eodg.atm.ox.ac.uk" in url
        or "rss.lizhi.fm" in url
        or "/rss/" in url
    )
