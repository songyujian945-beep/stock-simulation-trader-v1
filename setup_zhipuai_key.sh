#!/bin/bash

# 智谱AI API Key 安全配置脚本
# 用法: ./setup_zhipuai_key.sh

echo "🔒 智谱AI API Key 配置"
echo "========================"
echo ""

# 读取 API Key (不显示在终端)
read -s -p "请输入您的智谱AI API Key: " API_KEY
echo ""
echo ""

# 验证格式
if [[ ! $API_KEY =~ ^[a-f0-9]{32}\.[A-Za-z0-9]{16}$ ]]; then
    echo "⚠️  API Key 格式不正确"
    echo "正确格式: 32位十六进制.16位字母数字"
    exit 1
fi

# 添加到环境变量
SHELL_RC=""
if [ -f "$HOME/.zshrc" ]; then
    SHELL_RC="$HOME/.zshrc"
elif [ -f "$HOME/.bashrc" ]; then
    SHELL_RC="$HOME/.bashrc"
else
    echo "❌ 找不到 shell 配置文件"
    exit 1
fi

# 检查是否已存在
if grep -q "ZHIPUAI_API_KEY" "$SHELL_RC"; then
    echo "📝 更新现有配置..."
    # macOS compatible sed
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/export ZHIPUAI_API_KEY=.*/export ZHIPUAI_API_KEY=\"$API_KEY\"/" "$SHELL_RC"
    else
        sed -i "s/export ZHIPUAI_API_KEY=.*/export ZHIPUAI_API_KEY=\"$API_KEY\"/" "$SHELL_RC"
    fi
else
    echo "➕ 添加新配置..."
    echo "" >> "$SHELL_RC"
    echo "# 智谱AI API Key (OpenClaw)" >> "$SHELL_RC"
    echo "export ZHIPUAI_API_KEY=\"$API_KEY\"" >> "$SHELL_RC"
fi

echo "✅ API Key 已安全存储到: $SHELL_RC"
echo ""
echo "🔄 请运行以下命令使配置生效:"
echo "   source $SHELL_RC"
echo ""
echo "🔄 然后重启 OpenClaw Gateway:"
echo "   openclaw gateway restart"
echo ""
echo "✨ 配置完成！"
