# Mixin Chat Miner Skill

[English](README.md)

一个可移植的 Agent Skill 和本地 CLI，用来把 Mixin Desktop 聊天记录中经过筛选的一小部分导出为 JSONL。工具以只读方式访问源 SQLite 数据库，并让分析流程尽量留在本机。

本仓库不绑定某一种 AI 产品。任何能加载 `SKILL.md` 并执行本地 shell 命令的 Agent 都可以使用；不支持自动发现 Skill 的 Agent，也可以先读取 [SKILL.md](SKILL.md) 再执行任务。

## 必要环境

- macOS，已安装 Mixin Messenger Desktop，并已将聊天记录同步到本机。
- Python 3.9 或更高版本。
- Bash，用于运行仓库自带 helper。
- 对 Mixin Desktop 应用容器的读取权限。

不需要 API key，也没有第三方运行依赖。如果 macOS 拒绝访问，请在“系统设置”中给终端或 Agent 宿主授予所需的“文件与文件夹”或“完全磁盘访问权限”。

## 作为通用 Agent Skill 安装

把仓库克隆到所用 Agent 宿主的 Skill 目录：

```bash
git clone https://github.com/SeniorZhai/mixin-chat-miner-skill.git \
  /path/to/your-agent/skills/mixin-chat-miner
cd /path/to/your-agent/skills/mixin-chat-miner
./scripts/run_miner.sh db-check
```

不同 Agent 产品的 Skill 目录并不相同，请使用对应宿主文档给出的目录，或把本仓库添加为 Skill 来源。唯一必须的 Skill 入口是 `SKILL.md`。

## 初始化

标准 Mixin Desktop 数据目录下只有一个账号时，helper 会自动发现数据库。本机存在多个账号时，需要明确指定：

```bash
export MIXIN_CHAT_DB_PATH="$HOME/Library/Containers/one.mixin.messenger.desktop/Data/Documents/<account-id>/mixin.db"
./scripts/run_miner.sh db-check
```

输出 `available` 表示初始化完成。默认的私有快照目录是：

```text
~/Library/Application Support/Mixin Chat Miner/snapshots
```

只有需要更换位置时才设置：

```bash
export MIXIN_CHAT_SNAPSHOT_DIR="/path/to/private/snapshots"
```

## 使用 Skill

告诉 Agent 目标对话、主题或关键词、时间范围和最大消息数。Skill 会使用这些命令：

```bash
./scripts/run_miner.sh interactive
./scripts/run_miner.sh snapshots
./scripts/run_miner.sh latest
```

`latest` 只输出不含隐私信息的文件名和记录数，不输出消息正文。

## 直接使用 CLI

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
mixin-chat-miner
```

不安装包也可以运行仓库入口：

```bash
./bin/mixin-chat-miner
```

## 隐私与安全

- Mixin 数据库始终以 SQLite `mode=ro` 打开。
- 快照目录权限为仅用户可访问的 `0700`，文件权限为 `0600`。
- 快照文件名不包含对话名称或查询关键词。
- CLI 默认不打印消息预览，也不输出 Python traceback。
- 工具不发起网络请求，也不复制附件文件。
- 快照仍包含消息正文和用户名称。未经检查内容与接收方，不要提交、打包、上传或分享。

通过云端 Agent 使用 Skill 时，快照内容可能发送给该 Agent 服务商。请选择自己认可其数据处理方式的环境；CLI 自身不会上传数据。

## 开发验证

```bash
python -m unittest discover -s tests
python -m compileall -q src tests
bash -n scripts/run_miner.sh
```

让 AI 编程 Agent 修改本仓库前，还应阅读 [AI.md](AI.md)。

## 当前限制

- 仅支持当前 macOS 版 Mixin Desktop 数据库布局。
- 关键词查询使用 SQLite `LIKE`，不提供语义搜索。
- 快照是单次导出，不是备份或增量同步。
- 消息正文按数据库存储内容导出，不复制媒体文件。

## 许可证

[MIT](LICENSE)
