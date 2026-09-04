#!/usr/bin/env python3
"""
在庫判定ロジックそのものが正しいかを確認するテスト。

実際のサイトにはアクセスせず、Shopifyの商品JSONを模したサンプルデータを
自分で用意して、check_stock.py と同じ判定ロジックに通す。
「在庫あり」パターンと「在庫なし」パターンの両方が正しく判定できるかを確認する。
"""


def is_any_variant_available(data: dict) -> bool:
    """check_stock.py の fetch_availability() と全く同じ判定ロジック"""
    variants = data.get("product", data).get("variants", [])
    return any(v.get("available") for v in variants)


def main() -> None:
    # パターン1: 全バリエーションが売り切れ（在庫なし）
    sold_out_sample = {
        "product": {
            "variants": [
                {"id": 1, "title": "Default", "available": False},
            ]
        }
    }

    # パターン2: バリエーションのうち1つでも購入可能（在庫あり）
    in_stock_sample = {
        "product": {
            "variants": [
                {"id": 1, "title": "Default", "available": True},
            ]
        }
    }

    # パターン3: 複数バリエーションのうち一部だけ在庫あり
    partial_stock_sample = {
        "product": {
            "variants": [
                {"id": 1, "title": "S", "available": False},
                {"id": 2, "title": "M", "available": True},
                {"id": 3, "title": "L", "available": False},
            ]
        }
    }

    results = [
        ("売り切れパターン", sold_out_sample, False),
        ("在庫ありパターン", in_stock_sample, True),
        ("一部在庫ありパターン", partial_stock_sample, True),
    ]

    all_passed = True
    for label, sample, expected in results:
        actual = is_any_variant_available(sample)
        status = "OK" if actual == expected else "NG"
        if actual != expected:
            all_passed = False
        print(f"[{status}] {label}: 判定結果={actual} (期待値={expected})", flush=True)

    print("", flush=True)
    if all_passed:
        print("✅ すべてのパターンで判定ロジックは正しく動作しています。", flush=True)
    else:
        print("❌ 判定ロジックに問題があります。check_stock.py を確認してください。", flush=True)


if __name__ == "__main__":
    main()
