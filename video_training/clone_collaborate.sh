#!/bin/bash
# 分身协作 - 短视频内容生成
# 让本地Qwen2:7B批量生成短视频内容

API="http://localhost:11434/api/generate"
MODEL="qwen2:7b"

echo "🤖 本地分身开始工作..."
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"

# 任务1: 生成10个短视频主题
echo -e "\n📝 任务1: 生成10个热门短视频主题..."
curl -s $API -d "{
  \"model\": \"$MODEL\",
  \"prompt\": \"为抖音生成10个热门短视频主题，每个主题包含：主题名称、5个场景描述。主题要贴近年轻人生活，有共鸣，能引发互动。用JSON格式输出。\",
  \"stream\": false
}" | python3 -c "import sys, json; print(json.load(sys.stdin)['response'])" > /Users/syj/.openclaw/workspace/video_training/themes_qwen.json

echo "✅ 主题已保存到 themes_qwen.json"

# 任务2: 为现有主题生成更多场景变体
echo -e "\n📝 任务2: 扩展'职场吐槽'主题的场景..."
curl -s $API -d "{
  \"model\": \"$MODEL\",
  \"prompt\": \"为'职场吐槽'主题生成10个新的场景，每个场景一句话，要有画面感、幽默感、共鸣点。格式：场景1: xxx | 场景2: xxx\",
  \"stream\": false
}" | python3 -c "import sys, json; print(json.load(sys.stdin)['response'])" > /Users/syj/.openclaw/workspace/video_training/workplace_scenes.txt

echo "✅ 场景已保存到 workplace_scenes.txt"

# 任务3: 生成吸引人的标题池
echo -e "\n📝 任务3: 生成标题池..."
curl -s $API -d "{
  \"model\": \"$MODEL\",
  \"prompt\": \"为抖音短视频生成20个通用标题模板，要求：1. 吸引眼球 2. 引发好奇 3. 制造共鸣 4. 适合各种主题。每个标题控制在15字以内，用换行分隔。\",
  \"stream\": false
}" | python3 -c "import sys, json; print(json.load(sys.stdin)['response'])" > /Users/syj/.openclaw/workspace/video_training/title_templates.txt

echo "✅ 标题模板已保存到 title_templates.txt"

# 任务4: 生成视频描述文案
echo -e "\n📝 任务4: 生成视频描述文案..."
curl -s $API -d "{
  \"model\": \"$MODEL\",
  \"prompt\": \"为'程序员加班'主题的抖音视频写3个描述文案，每个包含：1. 吸引人的开头 2. 内容概括 3. 互动引导（点赞、评论、分享） 4. 相关话题标签。每个描述100字左右。\",
  \"stream\": false
}" | python3 -c "import sys, json; print(json.load(sys.stdin)['response'])" > /Users/syj/.openclaw/workspace/video_training/descriptions.txt

echo "✅ 描述文案已保存到 descriptions.txt"

# 任务5: 分析热门视频要素
echo -e "\n📝 任务5: 分析热门视频要素..."
curl -s $API -d "{
  \"model\": \"$MODEL\",
  \"prompt\": \"分析抖音热门短视频的10个关键要素，包括：标题特点、开头3秒、节奏控制、情感共鸣点、互动设计等。给出具体建议。\",
  \"stream\": false
}" | python3 -c "import sys, json; print(json.load(sys.stdin)['response'])" > /Users/syj/.openclaw/workspace/video_training/hot_video_analysis.txt

echo "✅ 分析报告已保存到 hot_video_analysis.txt"

echo -e "\n========================================"
echo "🎉 分身任务完成！"
echo "生成的文件："
ls -lh /Users/syj/.openclaw/workspace/video_training/*.txt /Users/syj/.openclaw/workspace/video_training/*.json 2>/dev/null | tail -5
