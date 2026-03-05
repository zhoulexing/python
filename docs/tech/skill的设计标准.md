## skill的目录结构

```
my-ts-skill/
├── SKILL.md            # 技能描述文件
├── agents/      
│   └── openai.yaml     # 技能的名片
├── scripts/            # 脚本
│   ├── package.json
│   ├── tsconfig.json
│   ├── src/
│   │   ├── index.ts
│   │   └── cli.ts
│   └── .gitignore
├── references/         # 参考文档
│   └── api.md
└── assets/
    └── template.json   # 产出物模板
```

## SKILL.md编写规则

### name描述规则

- 最多 64 个字符
- 只能包含小写字母、数字和连字符
- 不能包含 XML 标签
- 不能包含保留字："anthropic"、"claude"

### description描述规则

- 必须非空
- 最多 1024 个字符
- 不能包含 XML 标签
- 应描述技能的功能和使用时机，即when to use。