#!/bin/bash
# 通用分身调用脚本
# 用法: ./clone.sh "任务类型" "具体任务"

API="http://localhost:11434/api/generate"
MODEL="qwen2:7b"

TASK_TYPE="${1:-general}"
TASK_CONTENT="$2"
OUTPUT_DIR="/Users/syj/.openclaw/workspace/clone_tasks/outputs"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p "$OUTPUT_DIR"

case "$TASK_TYPE" in
    "batch")
        # 批量生成 - 输出多个变体
        RESULT=$(curl -s $API -d "{
          \"model\": \"$MODEL\",
          \"prompt\": \"$TASK_CONTENT\n\n请生成5个不同的版本，用---分隔。\",
          \"stream\": false
        }" | python3 -c "import sys, json; print(json.load(sys.stdin)['response'])")
        ;;
    "analyze")
        # 分析任务 - 结构化输出
        RESULT=$(curl -s $API -d "{
          \"model\": \"$MODEL\",
          \"prompt\": \"请分析以下内容，给出结构化的结论：\n$TASK_CONTENT\",
          \"stream\": false
        }" | python3 -c "import sys, json; print(json.load(sys.stdin)['response'])")
        ;;
    "code")
        # 代码生成
        RESULT=$(curl -s $API -d "{
          \"model\": \"$MODEL\",
          \"prompt\": \"请生成代码，只输出代码本身，不要解释：\n$TASK_CONTENT\",
          \"stream\": false
        }" | python3 -c "import sys, json; print(json.load(sys.stdin)['response'])")
        ;;
    *)
        # 通用任务
        RESULT=$(curl -s $API -d "{
          \"model\": \"$MODEL\",
          \"prompt\": \"$TASK_CONTENT\",
          \"stream\": false
        }" | python3 -c "import sys, json; print(json.load(sys.stdin)['response'])")
        ;;
esac

# 保存结果
echo "$RESULT" > "$OUTPUT_DIR/${TASK_TYPE}_${TIMESTAMP}.txt"
echo "$RESULT"
