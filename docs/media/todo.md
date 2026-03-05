## AI Coding
谈谈 AI 编程时代的「道法术」
https://www.ginonotes.com/posts/the-art-of-ai-coding#13---%E6%95%8F%E6%8D%B7%E4%B8%8E%E7%B2%BE%E7%9B%8A%E6%B3%95%E4%BB%B7%E5%80%BC%E6%B5%81%E5%8A%A8%E7%9A%84%E8%89%BA%E6%9C%AF

软件架构、设计模式、数据结构、程序算法。
DDD、微服务架构、六边形架构、洋葱架构、整洁架构。

如何结合AI？

规范驱动开发应该怎么搞？

SDD：https://bytedance.larkoffice.com/wiki/VyjJwgRIeik4Rbk8fGEcDs1gnjc

## agent设计模式
https://github.com/ginobefun/agentic-design-patterns-cn/blob/main/07-Chapter-01-Prompt-Chaining.md

## langchain、langgraph、 Claude agent sdk、codex agent sdk。

## 知识工程

## 上下文管理

## 沙箱定制

## 如何进行评测

## claude code如何更好的使用



一个 Agent 在想什么 / 正在做什么 / 卡在哪里

用户如何 中途介入、纠偏、追加约束

如何展示：

计划（Plan）

执行状态（Running / Blocked）

结果置信度（Confidence）

AI 的核心问题不是能力，而是 不稳定

系统必须能：

看见错误

回放过程

修正结果


数据不再是表

数据 = 记忆 / 状态 / 时间序列 / 事件

真正的护城河是：

懂人

懂复杂系统

懂不确定性

懂如何把“混乱”变成“可操作”



从「写确定程序」→「设计不确定系统」
你需要学会设计：
可回放（Replay）
可中断（Interrupt）
可修正（Correction）
可评估（Eval）

“让系统不翻车”比“让模型更强”更重要
状态管理
重试策略
降级设计
审计与日志
行为边界

数据的本质变了：从“存储”变成“记忆”
时间
上下文
历史决策
状态演化

Agent 时代，工程师要学会“授权”而不是“控制”
人设目标，系统自行探索
设定边界
定义目标函数
设计激励 / 惩罚机制

工程师个人的长期护城河：抽象能力
框架会过时
模型会升级
抽象能力不会