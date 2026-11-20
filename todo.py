import argparse
import json
import logging
from datetime import datetime
from typing import Optional

DB = "todos.json"


def load_todos(path: str = DB) -> list[dict[str, object]]:
    try:
        with open(path, encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_todos(todos: list[dict[str, object]], path: str = DB) -> None:
    with open(path, "w", encoding="utf-8") as file:
        json.dump(todos, file, ensure_ascii=False)


def parse_due(value: str) -> str:
    """期限日をYYYY-MM-DD形式として検証します。"""
    try:
        due = datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as error:
        raise argparse.ArgumentTypeError("期限日はYYYY-MM-DD形式で指定してください") from error
    if due.isoformat() != value:
        raise argparse.ArgumentTypeError("期限日はYYYY-MM-DD形式で指定してください")
    return value


def add(title: str, due: Optional[str] = None) -> None:
    todos = load_todos()
    todo: dict[str, object] = {
        "id": len(todos),
        "title": title,
        "done": False,
    }
    if due is not None:
        todo["due"] = due
    todos.append(todo)
    save_todos(todos)


def done(todo_id: int) -> None:
    todos = load_todos()
    for todo in todos:
        if todo["id"] == todo_id:
            todo["done"] = True
            save_todos(todos)
            return
    raise ValueError(f"TODO ID {todo_id} が見つかりません")


def delete(todo_id: int) -> None:
    todos = load_todos()
    remaining = [todo for todo in todos if todo["id"] != todo_id]
    if len(remaining) == len(todos):
        raise ValueError(f"TODO ID {todo_id} が見つかりません")
    save_todos(remaining)


def list_todos() -> None:
    for todo in load_todos():
        due = f" (期限: {todo['due']})" if "due" in todo else ""
        logging.info(
            "%s %s %s%s",
            todo["id"],
            "[x]" if todo["done"] else "[ ]",
            todo["title"],
            due,
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)

    add_parser = commands.add_parser("add")
    add_parser.add_argument("title")
    add_parser.add_argument("--due", type=parse_due, metavar="YYYY-MM-DD")

    done_parser = commands.add_parser("done")
    done_parser.add_argument("todo_id", type=int)

    delete_parser = commands.add_parser("delete")
    delete_parser.add_argument("todo_id", type=int)

    commands.add_parser("list")
    return parser


def main(argv: Optional[list[str]] = None) -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    args = build_parser().parse_args(argv)
    if args.command == "add":
        add(args.title, args.due)
    elif args.command == "done":
        done(args.todo_id)
    elif args.command == "delete":
        delete(args.todo_id)
    elif args.command == "list":
        list_todos()


if __name__ == "__main__":
    main()
