---
name: "CamelCase変数名"
description: "sales_report.pyで変数を追加・変更するときの命名規則。ハンズオン⑤で、instructionsの反映を確認するために使う。"
applyTo: "**/sales_report.py"
---

# 変数名の規則（ハンズオン⑤）

この演習では、instructionsがAIの編集に反映されるかを確認するため、Pythonの一般的な慣例（PEP 8のスネークケース）とは異なる規則を使います。`sales_report.py`では、PEP 8や既存コードの書き方より、この規則を優先してください。

- 新しく追加する変数名は、lowerCamelCaseで書きます。対象は、ローカル変数、ループ変数、関数の引数です。
  - 良い例：`regionTotals`、`topRegionName`、`salesRecords`
  - 避ける例：`region_totals`、`top_region_name`、`RegionTotals`
- 1語の変数名は、すべて小文字で書きます（例：`total`）。
- 関数名と定数名は対象外です。既存のコードに合わせ、関数名はスネークケース、定数名は大文字のスネークケースで書きます。
- 既存の変数名と関数名は、依頼がない限り変更しません。
- 辞書のキーなど、データの項目名（例：`"unit_price"`）は変更しません。
- 編集後の報告では、新しく追加した変数名を一覧で示します。
