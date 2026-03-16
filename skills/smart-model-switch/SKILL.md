# Smart Model Switch - 智能模型切换

自动根据任务类型选择最合适的智谱AI模型，优化成本和性能。

## 功能

- 🔍 **关键词识别**: 自动识别任务类型
- 💰 **成本优化**: 优先使用免费模型
- 🎯 **精准匹配**: 不同任务用不同模型
- 📊 **使用追踪**: 记录成本消耗

## 使用方式

当用户提出任务时，自动分析并切换模型：

```
用户: "帮我生成一段抖音短视频文案"
→ 检测到关键词 "短视频", "文案"
→ 切换到 glm-4-flash (免费)

用户: "写一个Python爬虫"
→ 检测到关键词 "Python", "写"
→ 切换到 codegeex-4 (代码专用)

用户: "分析这份销售数据"
→ 检测到关键词 "分析"
→ 切换到 glm-4-plus (强推理)
```

## 模型规则

| 触发词 | 模型 | 成本 |
|--------|------|------|
| 视频/文案/脚本/抖音 | glm-4-flash | ¥0 |
| 代码/编程/函数/bug | codegeex-4 | ¥0.001/千tokens |
| 分析/统计/推理 | glm-4-plus | ¥0.05/千tokens |
| 图片/截图/看图 | glm-4v-plus | ¥0.01/千tokens |
| 默认 | glm-4-air | ¥0.001/千tokens |

## 实现方式

### 方式 1: Subagent 模式（推荐）

```javascript
// 在处理任务前，选择合适的模型
const model = selectModelByKeywords(userMessage);
spawn_subagent({
  task: userMessage,
  model: model,
  runtime: "subagent"
});
```

### 方式 2: Session Status 切换

```javascript
// 切换当前session的模型
session_status({ model: selectedModel });
```

## 配置

规则文件: `/Users/syj/.openclaw/workspace/memory/model-switch-rules.json`

可以编辑此文件自定义规则。

---

_skill版本: 1.0_
_创建时间: 2026-03-16_
