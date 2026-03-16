#!/bin/bash
# 分身每日市场分析
# 让qwen2分析股市和币圈趋势

API="http://localhost:11434/api/generate"
MODEL="qwen2:7b"
OUTPUT_DIR="/Users/syj/.openclaw/workspace/clone_tasks/outputs"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p "$OUTPUT_DIR"

echo "📊 分身开始市场分析..."
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"

# 股市分析
echo -e "\n📈 A股市场分析..."
curl -s $API -d "{
  \"model\": \"$MODEL\",
  \"prompt\": \"作为股市分析师，分析当前A股市场（2026年3月）的投资机会。关注：1.科技股（AI、芯片、机器人） 2.新能源汽车 3.消费电子。给出3-5个看好的方向和理由，每个100字以内。\",
  \"stream\": false
}" | python3 -c "import sys, json; print(json.load(sys.stdin)['response'])" > "$OUTPUT_DIR/stock_analysis_$TIMESTAMP.txt"
echo "✅ 已保存到 stock_analysis_$TIMESTAMP.txt"

# 币圈分析
echo -e "\n🪙 加密货币市场分析..."
curl -s $API -d "{
  \"model\": \"$MODEL\",
  \"prompt\": \"作为加密货币分析师，分析当前市场趋势（2026年3月）。关注：1.BTC走势预判 2.ETH生态 3.热门赛道（AI、DePIN、RWA）。给出投资建议，注意风险提示。200字以内。\",
  \"stream\": false
}" | python3 -c "import sys, json; print(json.load(sys.stdin)['response'])" > "$OUTPUT_DIR/crypto_analysis_$TIMESTAMP.txt"
echo "✅ 已保存到 crypto_analysis_$TIMESTAMP.txt"

# 热点挖掘
echo -e "\n🔥 热点话题挖掘..."
curl -s $API -d "{
  \"model\": \"$MODEL\",
  \"prompt\": \"为抖音短视频挖掘10个当前可能热门的话题方向，要求：1.贴近年轻人生活 2.有共鸣点 3.容易引发互动。每个话题一句话描述。\",
  \"stream\": false
}" | python3 -c "import sys, json; print(json.load(sys.stdin)['response'])" > "$OUTPUT_DIR/hot_topics_$TIMESTAMP.txt"
echo "✅ 已保存到 hot_topics_$TIMESTAMP.txt"

echo -e "\n========================================"
echo "🎉 市场分析完成！"
