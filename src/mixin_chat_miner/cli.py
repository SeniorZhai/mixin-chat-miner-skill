#!/usr/bin/env python3
import unicodedata
from typing import Optional
from .db import get_connection, list_conversations, search_conversations, get_messages, get_conversation_info
from .snapshot import save_snapshot, generate_snapshot_filename


def terminal_text(value) -> str:
    """Render untrusted text without terminal control characters."""
    return "".join(
        character
        if unicodedata.category(character) not in {"Cc", "Cf"}
        else character.encode("unicode_escape").decode("ascii")
        for character in str(value)
    )


def print_banner():
    """Print the application banner."""
    print("=" * 60)
    print("Mixin Chat Miner")
    print("Analyze your Mixin chat history")
    print("=" * 60)


def select_conversation(conn) -> Optional[str]:
    """Let user select a conversation."""
    print("\n📋 可用对话列表:")
    print("-" * 40)

    conversations = list_conversations(conn, limit=20)
    for i, conv in enumerate(conversations, 1):
        name = conv['name'] or "未命名对话"
        count = conv['message_count']
        print(f"{i:2}. {terminal_text(name)} ({count} 条消息)")

    print("\n🔍 或者搜索对话:")
    search = input("输入关键词搜索 (直接回车选择列表): ").strip()

    if search:
        results = search_conversations(conn, search)
        if not results:
            print("未找到匹配的对话")
            return None

        print(f"\n找到 {len(results)} 个匹配的对话:")
        for i, conv in enumerate(results, 1):
            name = conv['name'] or "未命名对话"
            count = conv['message_count']
            print(f"{i:2}. {terminal_text(name)} ({count} 条消息)")

        conversations = results

    if not conversations:
        print("没有可用的对话")
        return None

    while True:
        try:
            choice = input("\n请选择对话编号 (输入数字): ").strip()
            if not choice:
                continue

            idx = int(choice) - 1
            if 0 <= idx < len(conversations):
                return conversations[idx]['conversation_id']
            else:
                print("无效的选择，请重新输入")
        except ValueError:
            print("请输入有效的数字")


def get_query_parameters():
    """Get query parameters from user."""
    print("\n🔍 查询参数设置:")
    print("-" * 40)

    keyword = input("关键词 (可选，直接回车跳过): ").strip() or None

    print("\n时间范围 (格式: YYYY-MM-DD HH:MM:SS)")
    start_time = input("开始时间 (可选): ").strip() or None
    end_time = input("结束时间 (可选): ").strip() or None

    while True:
        try:
            limit_input = input("最大消息数 [1000]: ").strip()
            limit = int(limit_input) if limit_input else 1000
            if limit > 0:
                break
            print("请输入正整数")
        except ValueError:
            print("请输入有效的数字")

    return {
        "keyword": keyword,
        "start_time": start_time,
        "end_time": end_time,
        "limit": limit
    }


def main():
    """Main CLI function."""
    print_banner()

    try:
        conn = get_connection()
        print("✅ 已连接到数据库")

        # Select conversation
        conversation_id = select_conversation(conn)
        if not conversation_id:
            print("未选择对话，退出")
            return

        # Get conversation info
        conv_info = get_conversation_info(conn, conversation_id)
        conv_name = conv_info['name'] if conv_info else "未知对话"
        print(f"\n已选择: {terminal_text(conv_name)}")

        # Get query parameters
        params = get_query_parameters()

        # Query messages
        print(f"\n⏳ 正在查询消息...")
        messages = get_messages(
            conn,
            conversation_id,
            keyword=params["keyword"],
            start_time=params["start_time"],
            end_time=params["end_time"],
            limit=params["limit"]
        )

        if not messages:
            print("未找到匹配的消息")
            return

        print(f"✅ 找到 {len(messages)} 条消息")

        filename = generate_snapshot_filename()

        save_path = save_snapshot(messages, filename)
        print(f"\n💾 快照已保存: {save_path.name}")

        print(f"\n✅ 完成! 快照包含 {len(messages)} 条消息")
        print(f"📁 文件: {save_path.name}")

    except FileNotFoundError as e:
        print(f"❌ 错误: {terminal_text(e)}")
    except Exception as e:
        print(f"❌ 错误: {terminal_text(e)}")
    finally:
        if 'conn' in locals():
            conn.close()


if __name__ == "__main__":
    main()
