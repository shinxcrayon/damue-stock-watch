#!/usr/bin/env python3
"""
DAMUE ONLINE STORE の商品の在庫を監視し、
売り切れ→在庫ありに変化したタイミングでLINEに通知するスクリプト。

Shopifyストアが標準で公開している商品JSONエンドポイント
(https://<store>/products/<handle>.json) を使って在庫状況を確認する。
HTMLの文言に依存しないため、デザイン変更等に強い。
"""

import json
import os
import time as time_module
import urllib.request
from datetime import datetime, time
from zoneinfo import ZoneInfo

# ==== 監視対象の設定 ====
PRODUCT_HANDLE = "5600-fog-silver"
STORE_DOMAIN = "damue.jp"
PRODUCT_JSON_URL = f"https://{STORE_DOMAIN}/products/{PRODUCT_HANDLE}.json"
PRODUCT_PAGE_URL = f"https://{STORE_DOMAIN}/products/{PRODUCT_HANDLE}"

STATE_FILE = "stock_state.json"

LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")

# ==== 監視する時間帯（日本時間） ====
# 毎週金曜 17:30〜19:00 のみ、1分おきにチェックし続ける。
JST = ZoneInfo("Asia/Tokyo")
WATCH_WEEKDAY = 4  # Python: 月=0 ... 金=4
WATCH_START = time(17, 30)
WATCH_END = time(19, 0)
CHECK_INTERVAL_SECONDS = 60


def fetch_availability() -> bool:
    """商品JSONを取得し、いずれかのバリエーションが購入可能かを返す"""
    req = urllib.request.Request(
        PRODUCT_JSON_URL,
        headers={"User-Agent": "Mozilla/5.0 (stock-watch-bot)"},
    )
    with urllib.request.urlopen(req, timeout=15) as res:
        data = json.load(res)

    variants = data.get("product", data).get("variants", [])
    if not variants:
        raise RuntimeError("商品データからvariantsが取得できませんでした")

    return any(v.get("available") for v in variants)


def load_previous_state() -> bool:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f).get("available", False)
    return False


def save_state(available: bool) -> None:
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump({"available": available}, f, ensure_ascii=False)


def send_line_broadcast(text: str) -> None:
    """LINE公式アカウントの友だち全員（＝自分だけのはず）にブロードキャスト送信"""
    if not LINE_CHANNEL_ACCESS_TOKEN:
        print("LINE_CHANNEL_ACCESS_TOKEN が設定されていないため通知をスキップします", flush=True)
        return

    url = "https://api.line.me/v2/bot/message/broadcast"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
    }
    body = json.dumps(
        {"messages": [{"type": "text", "text": text}]}
    ).encode("utf-8")

    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=15) as res:
        print(f"LINE API response status: {res.status}", flush=True)


def run_watch_loop() -> None:
    now = datetime.now(JST)

    if now.weekday() != WATCH_WEEKDAY:
        print(f"本日({now.strftime('%Y-%m-%d')})は監視対象の曜日（金曜）ではないため終了します", flush=True)
        return

    window_start_dt = datetime.combine(now.date(), WATCH_START, tzinfo=JST)
    window_end_dt = datetime.combine(now.date(), WATCH_END, tzinfo=JST)

    if now < window_start_dt:
        wait_seconds = (window_start_dt - now).total_seconds()
        print(f"監視開始（{WATCH_START.strftime('%H:%M')}）まで待機します（約{int(wait_seconds)}秒）", flush=True)
        time_module.sleep(max(0, wait_seconds))

    if datetime.now(JST) > window_end_dt:
        print("監視時間（19:00）を過ぎてしまったため終了します", flush=True)
        return

    previous = load_previous_state()
    print(
        f"監視を開始します（{WATCH_START.strftime('%H:%M')}〜{WATCH_END.strftime('%H:%M')} JST, "
        f"{CHECK_INTERVAL_SECONDS}秒間隔）",
        flush=True,
    )

    while datetime.now(JST) <= window_end_dt:
        try:
            available = fetch_availability()
        except Exception as e:
            print(f"在庫チェックに失敗しました（次のチェックでリトライします）: {e}", flush=True)
            time_module.sleep(CHECK_INTERVAL_SECONDS)
            continue

        now_str = datetime.now(JST).strftime("%H:%M:%S")
        print(f"[{now_str}] available={available} (previous={previous})", flush=True)

        if available and not previous:
            message = (
                "🎉 在庫復活しました！\n"
                "5600-Fog Silver (DAMUE)\n"
                f"{PRODUCT_PAGE_URL}\n"
                "急いでチェックしてください！"
            )
            send_line_broadcast(message)
            print("通知を送信しました", flush=True)

        previous = available
        save_state(available)
        time_module.sleep(CHECK_INTERVAL_SECONDS)

    print("監視時間が終了しました", flush=True)


def main() -> None:
    run_watch_loop()


if __name__ == "__main__":
    main()
