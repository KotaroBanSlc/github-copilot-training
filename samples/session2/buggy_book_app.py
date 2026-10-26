"""漫画蔵書管理 CLI アプリ（ハンズオン⑤・⑥用題材）

使い方:
    python buggy_book_app.py list
    python buggy_book_app.py search "バトル"
    python buggy_book_app.py find "ONE PIECE"
    python buggy_book_app.py page 1
    python buggy_book_app.py remove "ONE PIECE"
    python buggy_book_app.py add 13 "新しい作品" "作者名" 2026
"""

import json
import sys
from pathlib import Path

DATA_FILE = Path(__file__).parent / "books_data.json"
PAGE_SIZE = 5


def load_books() -> list[dict]:
    """books_data.json から書籍リストを読み込む。"""
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_books(books: list[dict]) -> None:
    """書籍リストを books_data.json に書き戻す。"""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(books, f, ensure_ascii=False, indent=2)


def add_book(books: list[dict], book_id: int, title: str, author: str, year: int) -> dict:
    """書籍を追加する。"""
    new_book = {
        "id": book_id,
        "title": title,
        "author": author,
        "year": year,
        "tags": [],
    }
    books.append(new_book)
    return new_book


def remove_book(books: list[dict], title: str) -> int:
    """指定タイトル（完全一致）の書籍を削除する。削除件数を返す。"""
    before = len(books)
    books[:] = [b for b in books if b["title"] != title]
    return before - len(books)


def find_book_by_title(books: list[dict], title: str) -> dict | None:
    """タイトル（完全一致・大文字小文字無視）で書籍を検索する。なければ None。"""
    for b in books:
        if b["title"].lower() == title.lower():
            return b
    return None


def find_book_by_author(books: list[dict], author: str) -> list[dict]:
    """著者名（部分一致・大文字小文字無視）で書籍を絞り込む。"""
    a = author.lower()
    return [b for b in books if a in b["author"].lower()]


def list_books(books: list[dict]) -> None:
    """全書籍を 1 行ずつ表示する。"""
    for b in books:
        print(f"  [{b['id']:>3}] {b['title']} / {b['author']} ({b['year']})")


def show_books_paginated(books: list[dict], page: int, page_size: int = PAGE_SIZE) -> None:
    """書籍をページ番号でページネーション表示する。"""
    total_pages = (len(books) + page_size - 1) // page_size

    print(f"=== Page {page} / {total_pages} ===")
    start = (page - 1) * page_size
    end = start + page_size
    chunk = books[start:end]

    target = chunk[0] if chunk else None
    print(f"先頭タイトル: {target['title']}")

    for b in chunk:
        print(f"  [{b['id']:>3}] {b['title']} / {b['author']} ({b['year']})")


def search_books(books: list[dict], keyword: str) -> list[dict]:
    """タイトル・著者・タグの部分一致検索（大文字小文字無視）。"""
    k = keyword.lower()
    results = []
    for b in books:
        if k in b["title"].lower():
            results.append(b)
            continue
        if k in b["author"].lower():
            results.append(b)
            continue
        if any(k in t.lower() for t in b.get("tags", [])):
            results.append(b)
    return results


def main() -> int:
    """コマンドライン引数で処理を分岐する。"""
    if len(sys.argv) < 2:
        print(__doc__)
        return 0

    cmd = sys.argv[1]
    books = load_books()

    if cmd == "list":
        list_books(books)
    elif cmd == "page":
        page_num = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        show_books_paginated(books, page_num)
    elif cmd == "search":
        keyword = sys.argv[2] if len(sys.argv) > 2 else ""
        results = search_books(books, keyword)
        print(f"検索結果: {len(results)} 件")
        list_books(results)
    elif cmd == "find":
        title = sys.argv[2] if len(sys.argv) > 2 else ""
        book = find_book_by_title(books, title)
        if book:
            print(f"見つかりました: {book['title']} / {book['author']}")
        else:
            print("見つかりませんでした")
    elif cmd == "remove":
        title = sys.argv[2] if len(sys.argv) > 2 else ""
        n = remove_book(books, title)
        save_books(books)
        print(f"{n} 件削除しました")
    elif cmd == "add":
        if len(sys.argv) < 6:
            print("usage: add <id> <title> <author> <year>")
            return 1
        book_id = int(sys.argv[2])
        title = sys.argv[3]
        author = sys.argv[4]
        year = int(sys.argv[5])
        new_book = add_book(books, book_id, title, author, year)
        save_books(books)
        print(f"追加しました: {new_book}")
    else:
        print(f"unknown command: {cmd}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
