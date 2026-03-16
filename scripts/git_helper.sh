#!/bin/bash
# Git项目自动化管理脚本
# 作者：小小宋

set -e

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# GitHub用户名（需要替换）
GITHUB_USER="${GITHUB_USER:-your-username}"

# 打印带颜色的消息
print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 创建新项目
create_project() {
    local project_name=$1
    local project_dir="$HOME/.openclaw/workspace/$project_name"

    print_info "创建项目: $project_name"

    # 创建目录
    mkdir -p "$project_dir"/{src,tests,docs,config,scripts}

    # 初始化git
    cd "$project_dir"
    git init

    # 创建README
    cat > README.md <<EOF
# $project_name

## 简介
[项目描述]

## 功能
- [ ] 功能1
- [ ] 功能2

## 安装
\`\`\`bash
# 安装依赖
\`\`\`

## 使用
\`\`\`bash
# 使用说明
\`\`\`

## 作者
宋先生的数字分身

## 版本历史
- v1.0.0 - 初始版本
EOF

    # 创建.gitignore
    cat > .gitignore <<EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
*.egg-info/

# 敏感信息
config/secrets.json
*.key
*.pem

# IDE
.vscode/
.idea/
*.swp
*.swo

# 系统文件
.DS_Store
Thumbs.db

# 日志
*.log
logs/
EOF

    # 首次提交
    git add .
    git commit -m "feat: 初始化项目 $project_name"

    print_success "项目创建完成: $project_dir"
}

# 关联GitHub仓库
link_github() {
    local project_name=$1
    local project_dir="$HOME/.openclaw/workspace/$project_name"

    cd "$project_dir"

    # 检查是否已关联
    if git remote | grep -q "origin"; then
        print_info "已关联远程仓库"
        git remote -v
        return
    fi

    # 创建GitHub仓库
    print_info "创建GitHub仓库..."
    gh repo create "$project_name" --public --source=. --remote=origin

    # 推送
    git push -u origin main || git push -u origin master

    print_success "已关联并推送到GitHub"
}

# 提交优化
commit_optimize() {
    local project_name=$1
    local message=$2
    local project_dir="$HOME/.openclaw/workspace/$project_name"

    cd "$project_dir"

    # 创建优化分支
    local branch_name="optimize/$(date +%Y%m%d-%H%M%S)"
    git checkout -b "$branch_name"

    # 提交
    git add .
    git commit -m "optimize: $message"

    # 合并到develop
    git checkout develop 2>/dev/null || git checkout -b develop
    git merge "$branch_name"

    # 推送
    git push origin develop

    print_success "优化已提交到develop分支: $branch_name"
}

# 发布版本
release_version() {
    local project_name=$1
    local version=$2
    local project_dir="$HOME/.openclaw/workspace/$project_name"

    cd "$project_dir"

    # 切换到main
    git checkout main || git checkout master

    # 合并develop
    git merge develop

    # 创建标签
    git tag -a "$version" -m "Release $version"

    # 推送
    git push origin main
    git push origin "$version"

    print_success "版本 $version 已发布"
}

# 查看状态
status() {
    local project_name=$1
    local project_dir="$HOME/.openclaw/workspace/$project_name"

    if [ -d "$project_dir" ]; then
        cd "$project_dir"
        print_info "项目: $project_name"
        echo ""
        echo "分支:"
        git branch -a
        echo ""
        echo "最近提交:"
        git log --oneline -5
        echo ""
        echo "状态:"
        git status -s
    else
        print_error "项目不存在: $project_name"
    fi
}

# 主菜单
main() {
    case "${1:-help}" in
        create)
            create_project "$2"
            ;;
        link)
            link_github "$2"
            ;;
        optimize)
            commit_optimize "$2" "$3"
            ;;
        release)
            release_version "$2" "$3"
            ;;
        status)
            status "$2"
            ;;
        *)
            echo "用法: $0 {create|link|optimize|release|status} [项目名] [消息/版本]"
            echo ""
            echo "示例:"
            echo "  $0 create stock-trader-v1      # 创建新项目"
            echo "  $0 link stock-trader-v1        # 关联GitHub"
            echo "  $0 optimize stock-trader-v1 \"优化算法\"  # 提交优化"
            echo "  $0 release stock-trader-v1 v1.1.0      # 发布版本"
            echo "  $0 status stock-trader-v1      # 查看状态"
            ;;
    esac
}

main "$@"
