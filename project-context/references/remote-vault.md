# 可选远程项目记忆库

只有当前用户请求明确要求远程项目记忆库、同步、拉取或推送时，才读取本文件并执行其中流程。
单独调用 `project-context`、创建/更新/接手/审计本地 `.agent-context/`，都不要读取本文件，也不要探测、创建或访问全局配置和 Vault。

## 三层结构

```text
当前项目/.agent-context/          # 项目工作副本，默认仍 gitignore
        ↕ 仅显式远程指令时复制

~/.local/share/opencode/project-context/vault/
  projects/<host>/<owner>/<repo>/.agent-context/
        ↕ git fetch / commit / push

私有远程 Context Vault 仓库
```

本机配置和状态：

```text
~/.config/opencode/project-context/config.yaml
~/.local/state/opencode/project-context/state.yaml
```

不要把本机绝对路径、Vault 路径、token、同步 commit 写入项目内 `.agent-context/`。

## 何时进入远程模式

必须同时满足：

1. 当前请求已经授权操作 `project-context` / `.agent-context/`。
2. 用户明确提到以下之一：项目记忆库、远程记忆库、Context Vault、同步到远程、从远程恢复/拉取、推送上下文、导入到记忆库。

以下情况保持纯本地，禁止联网：

- 只说“创建/更新/接手/审计项目上下文”
- 只手动调用本 skill，没有提远程
- 普通编码、修 bug、提交、任务收尾
- 发现本机已有 config.yaml 或 vault 克隆

## 自动配置

不要把某个 GitHub 仓库写死为所有人的默认远程。

首次远程操作按顺序自动配置，不要为了“先问一句”而停下：

1. 若 `config.yaml` 已存在且含 `store.remote`，直接使用。
2. 若用户本轮给出了记忆库 URL，写入配置。已有配置且 URL 不同时停止，询问是否重配。
3. 若用户只说“我的项目记忆库”但没给 URL：
   - 已有配置或已有 vault 克隆，则使用；
   - 都没有，才询问 URL。
4. 配置写入后，克隆或更新本地 Vault。

`config.yaml` 由 agent 自动创建，用户不必手写。模板：

```yaml
store:
  type: git
  remote: https://github.com/example/project-context.git
  local_path: ~/.local/share/opencode/project-context/vault
  projects_prefix: projects
sync:
  pull: explicit
  push: explicit
  conflict: stop
```

`sync.pull` / `sync.push` 必须保持 `explicit`。不得改成创建或更新本地上下文后自动推送。

## 项目身份

默认从当前项目 `git remote origin` 推导：

```text
https://github.com/KomeijiReimu/Komei-Agent.git
→ github.com/KomeijiReimu/Komei-Agent
→ projects/github.com/KomeijiReimu/Komei-Agent/.agent-context/
```

无 origin 时不要猜测本机目录名；请用户给一个稳定 `project_id`。
不要用 symlink 把项目 `.agent-context/` 链到 Vault；只复制文件。

## 脚本

机械步骤使用本 skill 的 `scripts/vault.py`。先定位 skill 目录，再执行，不要手写 git clone/rsync 流程。

```text
python3 scripts/vault.py self-check
python3 scripts/vault.py ensure-config --remote <vault-url>
python3 scripts/vault.py ensure-vault
python3 scripts/vault.py project-id --project-root <project>
python3 scripts/vault.py scan --path <project>/.agent-context
python3 scripts/vault.py status --project-root <project>
python3 scripts/vault.py diff --project-root <project>
python3 scripts/vault.py push --project-root <project>
python3 scripts/vault.py pull --project-root <project>
python3 scripts/vault.py pull --project-root <project> --force
```

退出码：`0` 成功；`2` 有差异或冲突已停止；`3` 疑似秘密；`4` 缺配置或项目身份。

## 远程子模式

在确认用户明确要求远程后，再选一个：

| 用户意图 | 子模式 | 动作 |
|---|---|---|
| 绑定/初始化记忆库 | `remote-init` | `ensure-config` + `ensure-vault` |
| 查看差异 | `remote-status` | `status` / `diff` |
| 推送/导入当前项目 | `remote-push` | 扫描秘密后 `push` |
| 从记忆库恢复到当前项目 | `remote-pull` | 无冲突则 `pull`；有冲突停止 |
| 双向同步 | `remote-sync` | 先 `status`；仅本地变则 push，仅远程变则 pull，两侧都变则停止 |

`remote-pull` 默认禁止覆盖本地已有且不同的 `.agent-context/`。只有用户明确要求覆盖时才加 `--force`。

`remote-sync` 不做自动三方合并。冲突时列出文件并停止。

## 推送规则

1. 只复制当前项目 `.agent-context/`，不要把项目源码、`.env`、锁文件或构建产物放进 Vault。
2. 推送前扫描秘密；命中则停止。
3. Vault 提交只包含该项目切片、`registry.yaml` 和必要时的 Vault `README.md`。
4. 提交信息说明项目 ID，例如 `chore: import github.com/org/repo agent context`。
5. 只 `git push` Vault 仓库，不要改当前项目仓库的提交。
6. 同步基线写入 `~/.local/state/opencode/project-context/state.yaml`，不要写入项目文档。

## 拉取规则

1. 先更新 Vault 克隆。
2. 只把对应项目切片复制到当前项目 `.agent-context/`。
3. 不修改项目其他文件，不因为拉取而删除 `.gitignore` 中的 `.agent-context/` 规则。
4. 本地已有不同内容时停止并报告 diff。

## 安全

- Vault 必须按私有仓库使用；若远程明显是公开仓库，推送前警告用户。
- 不记录令牌、私钥、密码、`.env` 内容。
- `user-preferences.md` 会随项目切片一起进入个人 Vault；不要把与当前项目无关的个人隐私写进去。
- 配置文件和 state 只存在本机全局目录。

## 完成汇报额外项

若本次确实执行了远程操作，在本地上下文汇报之外补充：

- 使用的 Vault 远程 URL 和本机克隆是否已创建
- 项目 ID 和 Vault 内路径
- pull / push / 仅查看 / 因冲突停止
- 是否写入了本机 `config.yaml`
- 未改当前项目 git 历史

未执行远程操作时，不要提及 config、Vault 或联网。
