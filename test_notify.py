#!/usr/bin/env python3
"""
LINE通知が正しく届くかを確認するためのテストスクリプト。
在庫状況に関係なく、実行すると必ずテストメッセージを送信する。
"""

import json
import os
import urllib.request

LINE_CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")


def send_line_broadcast(text: str) -> None:
    if not LINE_CHANNEL_ACCESS_TOKEN:
        print("LINE_CHANNEL_ACCESS_TOKEN が設定されていません", flush=True)
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


def main() -> None:
    send_line_broadcast(
        "✅ テスト通知です。\nこのメッセージが届いていれば、DAMUE在庫通知Botの設定は正しく完了しています。"
    )
    print("テストメッセージを送信しました", flush=True)


if __name__ == "__main__":
    main()
