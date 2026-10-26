"""ユーザーごとの月次売上集計レポートを生成するスクリプト。

実行すると、ユーザー別のランキングとサマリを標準出力に表示し、
同じ内容を report_output.json に書き出します。
"""

import json
from datetime import datetime
from pathlib import Path

DATA = [
    {"user_id": "u001", "name": "Alice", "month": "2026-01", "amount": 50000, "category": "subscription"},
    {"user_id": "u001", "name": "Alice", "month": "2026-02", "amount": 50000, "category": "subscription"},
    {"user_id": "u001", "name": "Alice", "month": "2026-03", "amount": 120000, "category": "addon"},
    {"user_id": "u002", "name": "Bob", "month": "2026-01", "amount": 30000, "category": "subscription"},
    {"user_id": "u002", "name": "Bob", "month": "2026-02", "amount": 30000, "category": "subscription"},
    {"user_id": "u003", "name": "Charlie", "month": "2026-01", "amount": 80000, "category": "subscription"},
    {"user_id": "u003", "name": "Charlie", "month": "2026-02", "amount": 80000, "category": "subscription"},
    {"user_id": "u003", "name": "Charlie", "month": "2026-03", "amount": 150000, "category": "addon"},
    {"user_id": "u003", "name": "Charlie", "month": "2026-04", "amount": 80000, "category": "subscription"},
    {"user_id": "u004", "name": "Diana", "month": "2026-01", "amount": 250000, "category": "enterprise"},
    {"user_id": "u004", "name": "Diana", "month": "2026-02", "amount": 250000, "category": "enterprise"},
    {"user_id": "u004", "name": "Diana", "month": "2026-03", "amount": 250000, "category": "enterprise"},
    {"user_id": "u005", "name": "Eve", "month": "2026-02", "amount": 45000, "category": "subscription"},
    {"user_id": "u005", "name": "Eve", "month": "2026-03", "amount": 45000, "category": "subscription"},
]

OUT = []


def do_it(d):
    # ユーザーごと集計
    u = {}
    for x in d:
        if x["user_id"] not in u:
            u[x["user_id"]] = {"name": x["name"], "months": {}, "categories": {}, "total": 0, "tax_total": 0, "active_months": 0}
        m = x["month"]
        if m not in u[x["user_id"]]["months"]:
            u[x["user_id"]]["months"][m] = 0
            u[x["user_id"]]["active_months"] = u[x["user_id"]]["active_months"] + 1
        u[x["user_id"]]["months"][m] = u[x["user_id"]]["months"][m] + x["amount"]
        c = x["category"]
        if c not in u[x["user_id"]]["categories"]:
            u[x["user_id"]]["categories"][c] = 0
        u[x["user_id"]]["categories"][c] = u[x["user_id"]]["categories"][c] + x["amount"]
        u[x["user_id"]]["total"] = u[x["user_id"]]["total"] + x["amount"]
        u[x["user_id"]]["tax_total"] = u[x["user_id"]]["tax_total"] + int(x["amount"] * 10 / 100)

    # ボーナス対象判定
    for k, v in u.items():
        if v["total"] >= 100000:
            v["bonus_eligible"] = True
            v["bonus"] = int(v["total"] * 5 / 100)
        else:
            v["bonus_eligible"] = False
            v["bonus"] = 0
        # 平均月次（active_months ベース）
        if v["active_months"] > 0:
            v["avg_monthly"] = int(v["total"] / v["active_months"])
        else:
            v["avg_monthly"] = 0
        # 年間予測（active_months から 12 ヶ月推定）
        if v["active_months"] > 0:
            v["annual_forecast"] = int(v["total"] * 12 / v["active_months"])
        else:
            v["annual_forecast"] = 0

    # ランキング作成
    rk = sorted(u.items(), key=lambda kv: kv[1]["total"], reverse=True)

    # 出力フォーマット
    for i, (k, v) in enumerate(rk):
        line = "[" + str(i + 1) + "] " + v["name"] + " (id=" + k + ")"
        line = line + " total=" + str(v["total"])
        line = line + " tax=" + str(v["tax_total"])
        line = line + " avg=" + str(v["avg_monthly"])
        line = line + " forecast=" + str(v["annual_forecast"])
        if v["bonus_eligible"]:
            line = line + " BONUS=" + str(v["bonus"])
        OUT.append(line)

    # サマリ計算
    s = 0
    sb = 0
    cnt = 0
    for k, v in u.items():
        s = s + v["total"]
        if v["bonus_eligible"]:
            sb = sb + v["bonus"]
            cnt = cnt + 1
    OUT.append("---")
    OUT.append("[SUMMARY] total_revenue=" + str(s) + " total_bonus=" + str(sb) + " bonus_users=" + str(cnt))
    OUT.append("[SUMMARY] tax_rate=10% bonus_threshold=100000 bonus_rate=5%")

    # 出力フォーマット（同じことをもう一度、JSON 用に）
    j = {}
    for k, v in u.items():
        line2 = v["name"] + " total=" + str(v["total"]) + " tax=" + str(v["tax_total"])
        if v["bonus_eligible"]:
            line2 = line2 + " BONUS=" + str(v["bonus"])
        j[k] = {"summary": line2, "raw": v}
    return OUT, j


def handle_data():
    o, j = do_it(DATA)
    for line in o:
        print(line)
    p = Path(__file__).parent / "report_output.json"
    with open(p, "w", encoding="utf-8") as f:
        json.dump(j, f, ensure_ascii=False, indent=2)
    print("written:", p)


if __name__ == "__main__":
    handle_data()
