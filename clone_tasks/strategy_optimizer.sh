#!/bin/bash
# 分身策略优化
# 让qwen2帮助优化交易策略和视频策略

API="http://localhost:11434/api/generate"
MODEL="qwen2:7b"
OUTPUT_DIR="/Users/syj/.openclaw/workspace/clone_tasks/outputs"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p "$OUTPUT_DIR"

echo "🧠 分身开始策略优化..."
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"

# 股票策略优化
echo -e "\n📈 股票策略优化..."
curl -s $API -d "{
  \"model\": \"$MODEL\",
  \"prompt\": \"分析以下股票交易策略，指出问题并给出改进建议：\n策略：超跌反弹（跌幅>2%买入）\n股票池：浪潮信息、三花智控、立讯精密、歌尔股份\n目标：7天内盈利\n\n请给出3-5条具体改进建议，每条50字以内。\",
  \"stream\": false
}" | python3 -c "import sys, json; print(json.load(sys.stdin)['response'])" > "$OUTPUT_DIR/stock_strategy_$TIMESTAMP.txt"
echo "✅ 已保存"

# 视频内容优化
echo -e "\n🎬 短视频内容优化..."
curl -s $API -d "{
  \"model\": \"$MODEL\",
  \"prompt\": \"为以下短视频主题生成更吸引人的内容方案：\n主题：职场吐槽、扎心真相、情感共鸣\n\n每个主题生成：1个爆款标题 + 3个场景描述 + 1个互动结尾。要求有趣、有共鸣、有传播性。\",
  \"stream\": false
}" | python3 -c "import sys, json; print(json.load(sys.stdin)['response'])" > "$OUTPUT_DIR/video_content_$TIMESTAMP.txt"
echo "✅ 已保存"

# 创意方向
echo -e "\n💡 新创意方向..."
curl -s $API -d "{
  \"model\": \"$MODEL\",
  \"prompt\": \"为2026年3月的抖音短视频平台，推荐5个创新的内容方向。要求：1.差异化明显 2.制作门槛适中 3.有变现潜力。每个方向100字说明。\",
  \"stream\": false
}" | python3 -c "import sys, json; print(json.load(sys.stdin)['response'])" > "$OUTPUT_DIR/creative_directions_$TIMESTAMP.txt"
echo "✅ 已保存"

echo -e "\n========================================"
echo "🎉 策略优化完成！"
