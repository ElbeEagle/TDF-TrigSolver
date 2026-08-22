# Trig Gold 轻量标注页面

这是一个与 `src/trig_solver/` 分离的本地 Streamlit MVP。它只执行输入隔离、字段引导、AST 生成和结构校验，不调用求解器，也不判断数学结论是否正确。

## 1. 安装

在仓库根目录运行：

```bash
.venv/bin/python -m pip install -e '.[annotation,dev]'
```

## 2. 两位标注者分别启动

标注者 A：

```bash
.venv/bin/python annotation_app/run.py --annotator annotator_a --port 8501
```

标注者 B：

```bash
.venv/bin/python annotation_app/run.py --annotator annotator_b --port 8502
```

然后分别打开 `http://127.0.0.1:8501` 和 `http://127.0.0.1:8502`。启动器固定监听本机地址，并关闭 Streamlit 使用统计。

若两人共用同一台电脑，应使用各自的浏览器会话，并且不得浏览对方目录。若需要更强的访问控制，应让两人各自在自己的系统账号或电脑上运行。当前 MVP 的“隔离”是应用数据路径隔离，不是操作系统级权限沙箱。

## 3. 页面边界

页面仅加载 `test_annotation_template.jsonl`，并在启动时执行以下检查：

- 模板 SHA-256 必须与相邻 `manifest.json` 一致；
- 必须恰好包含 50 条唯一题目；
- `oracle_urm`、`gold_answer`、`gold_option` 必须为空；
- 不得含 `answer`、`analysis`、`solution`、求解器输出或模型预测字段；
- 当前会话只能读写 `<workspace>/<annotator_id>/`。

页面显示题干、选项和锁定元数据；不会读取原始 CMM-Math 答案、另一位标注者文件或任何 solver prediction。

## 4. 标注流程

1. 独立完成数学推导。
2. 在 Oracle-URM 区填写目标公式、主变量、操作、角制、象限、显式约束和性质名称。不要把最终答案写入 Oracle-URM。
3. 在 Gold 区选择 `expression`、`set` 或 `periodic_set`，填写人工推导出的数学答案。
4. 选择题最后填写 `gold_option`；开放题会强制保存为 `null`。
5. 检查“实时结构校验”生成的规范 JSON。只有显示结构有效后，才能保存为 completed。

“结构有效”只表示数据符合 schema，例如 AST 节点合法、周期点位于 `[0,T)`；不表示答案算对了。页面不会化简、证明或替标注者选择答案。

常用输入格式：

- 表达式：标准 LaTeX，例如 `\frac{\sqrt{6}-\sqrt{2}}{4}`；常见的 `\left|...\right|` 会转换为 `abs` AST 节点。
- 显式约束：每行一个关系式，或 `[property] name=value`、`[membership] name=value`。
- 有限集：每行一个 LaTeX 表达式。
- 区间：`[0,2]`、`(-\infty,-1]`。
- 周期点：每行一个基本周期内的点。
- 周期区间：每行一个区间；跨越周期端点时拆成两行。

## 5. 私有输出

默认输出到：

```text
annotation_runs/<annotator_id>/
├── annotations.jsonl
├── drafts.json
└── events.jsonl
```

- `annotations.jsonl`：50 条规范记录，完成项含结构化 Oracle-URM 和 Gold；供后续字段级比较。
- `drafts.json`：自动保存的未完成表单，可恢复会话。
- `events.jsonl`：完成/覆盖事件的最小审计日志。

目录默认权限为 `0700`，文件为 `0600`，并已被 `.gitignore` 排除。侧栏“导出本人的 JSONL”只导出当前会话的 `annotations.jsonl`。

可通过 `--workspace` 指定私有保存根目录，通过 `--template` 指定模板；模板仍必须与其相邻 manifest 的哈希匹配。

## 6. 开发验证

```bash
.venv/bin/python -m pytest -q tests/test_annotation_app.py
.venv/bin/python -m pytest -q
```

测试覆盖冻结输入边界、敏感字段拒绝、双标注员路径隔离、恢复状态、普通集合、完整周期解及选择/开放题约束。
