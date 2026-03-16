# 智谱AI 多模型配置方案

## 🔒 API Key 安全存储

**方式 1: 环境变量（推荐）**
```bash
# 添加到 ~/.zshrc 或 ~/.bash_profile
export ZHIPUAI_API_KEY="你的API_KEY"
```

**方式 2: OpenClaw 配置**
```bash
openclaw configure --section models --provider zai
```

---

## 📋 模型-任务映射规则

| 任务类型 | 模型选择 | API 名称 | 成本/千tokens | 原因 |
|---------|---------|----------|--------------|------|
| **短视频文案** | GLM-4-Flash | `glm-4-flash` | ¥0 | 免费、快速、批量生成 |
| **代码生成** | CodeGeeX-4 | `codegeex-4` | ¥0.001 | 专用代码模型 |
| **复杂数据分析** | GLM-4-Plus | `glm-4-plus` | ¥0.05 | 推理能力强 |
| **日常对话** | GLM-4-Air | `glm-4-air` | ¥0.001 | 性价比高 |
| **超长文本** | GLM-4-Long | `glm-4-long` | ¥0.001 | 100万token上下文 |
| **图像理解** | GLM-4V-Plus | `glm-4v-plus` | ¥0.01 | 视觉+文本 |

---

## 🚀 自动切换规则

### 规则 1: 关键词触发
当用户消息包含以下关键词时，自动切换模型：

```
视频/文案/脚本 → glm-4-flash (免费)
代码/编程/函数/bug → codegeex-4 (代码专用)
分析/统计/推理 → glm-4-plus (强推理)
图片/截图/看图 → glm-4v-plus (视觉理解)
```

### 规则 2: Subagent 隔离
不同任务启动独立 subagent，避免主session污染：

```python
# 视频生成任务
spawn_subagent(task="生成视频", model="glm-4-flash")

# 代码任务
spawn_subagent(task="编写代码", model="codegeex-4")

# 分析任务
spawn_subagent(task="分析数据", model="glm-4-plus")
```

---

## 💰 成本优化策略

1. **默认使用免费模型** (GLM-4-Flash) 处理简单任务
2. **仅在需要时切换** 到付费模型
3. **批量处理** 相同类型任务
4. **缓存常用结果** 避免重复调用

---

## 📊 预估月成本

假设每月使用量：
- 短视频文案：1000次 × 500 tokens = 50万tokens (¥0)
- 代码生成：50次 × 1000 tokens = 5万tokens (¥0.05)
- 复杂分析：20次 × 2000 tokens = 4万tokens (¥2)
- 日常对话：200次 × 300 tokens = 6万tokens (¥0.06)

**总计：约 ¥2.11/月** 🎉

---

## ✅ 配置步骤

1. **设置 API Key** (安全方式)
   ```bash
   # 添加到环境变量
   echo 'export ZHIPUAI_API_KEY="你的key"' >> ~/.zshrc
   source ~/.zshrc
   ```

2. **更新 OpenClaw 配置**
   - 我会自动更新配置文件
   - 重启 Gateway 生效

3. **测试切换**
   - "生成一段视频文案" → 自动用 glm-4-flash
   - "帮我写个Python函数" → 自动用 codegeex-4
   - "分析这份数据" → 自动用 glm-4-plus

---

_创建时间: 2026-03-16_
_状态: 待配置_
