"""從台電開放資料抓每日電力供需與備轉容量率（可重現、免金鑰）。

資料來自政府資料開放平臺（data.gov.tw）指向的台電 CSV：
  19995  台灣電力公司過去電力供需資訊  —— 每日尖峰負載、備轉率、風力、太陽能、各機組
  24945  台灣電力公司近三年每日尖峰備轉容量率 —— 每日備轉率（較長，無再生分項）

下載網址從 data.gov.tw 的 dataset API 動態取得（resourceDownloadUrl），
避免寫死；若 API 變動，末端有已知的直接網址當備援。
"""
from __future__ import annotations

import io
import time
import urllib.request
from pathlib import Path

DATASETS = {
    "supply_demand": 19995,   # 每日供需 + 風力/太陽能（2025 起）
    "reserve_margin": 24945,  # 每日備轉率（2023 起，序列較長）
}
# 已知直接網址（API 掛掉時的備援）
FALLBACK = {
    19995: "https://service.taipower.com.tw/data/opendata/apply/file/d006005/001.csv",
    24945: "https://service.taipower.com.tw/data/opendata/apply/file/d006004/001.csv",
}
GOV_API = "https://data.gov.tw/api/v2/rest/dataset/{}"


def _resource_url(dataset_id: int, timeout: int) -> str:
    """從 data.gov.tw 取第一個資源的下載網址；失敗則用備援。"""
    try:
        import json
        raw = urllib.request.urlopen(GOV_API.format(dataset_id), timeout=timeout).read()
        dist = json.loads(raw)["result"]["distribution"]
        for r in dist:
            u = r.get("resourceDownloadUrl")
            if u:
                return u
    except Exception:  # noqa: BLE001 — 動態 API 不穩，落回備援即可
        pass
    return FALLBACK[dataset_id]


def fetch_csv(dataset_id: int, cache_dir: Path, timeout: int = 40, retries: int = 3):
    """抓某資料集的 CSV（帶快取與重試），回傳本地檔路徑。"""
    import pandas as pd
    cache_dir.mkdir(parents=True, exist_ok=True)
    out = cache_dir / f"taipower_{dataset_id}.csv"
    if out.exists():
        return out
    url = _resource_url(dataset_id, timeout)
    last = None
    for attempt in range(1, retries + 1):
        try:
            raw = urllib.request.urlopen(url, timeout=timeout).read()
            # 驗證能被 pandas 解析（抓錯頁面會在這裡爆）
            pd.read_csv(io.BytesIO(raw), encoding="utf-8-sig", nrows=5)
            out.write_bytes(raw)
            return out
        except Exception as exc:  # noqa: BLE001
            last = f"{type(exc).__name__}: {exc}"
            if attempt < retries:
                time.sleep(3 * attempt)
    raise RuntimeError(f"抓取 {dataset_id} 失敗：{last}")


def fetch_all(cache_dir: str = "data") -> dict:
    """抓齊本專案需要的資料集，回傳 {name: path}。"""
    cd = Path(cache_dir)
    return {name: fetch_csv(ds_id, cd) for name, ds_id in DATASETS.items()}


if __name__ == "__main__":
    for name, path in fetch_all().items():
        print(f"{name:14s} -> {path}")
