#!/bin/bash
# Linux (Apache) 環境用セットアップスクリプト

set -e

# カラー定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# プロジェクトルート
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 関数定義
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_header() {
    echo ""
    echo -e "${BOLD}${BLUE}============================================================${NC}"
    echo -e "${BOLD}${BLUE}$1${NC}"
    echo -e "${BOLD}${BLUE}============================================================${NC}"
    echo ""
}

# Pythonバージョンチェック
check_python() {
    print_header "Pythonバージョンチェック"
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python3がインストールされていません"
        echo "インストール: sudo apt-get install python3"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    print_info "Python $PYTHON_VERSION"
    print_success "Python OK"
}

# 必要なパッケージのチェック
check_packages() {
    print_header "パッケージチェック"
    
    # Apache
    if ! command -v apache2 &> /dev/null; then
        print_warning "Apache2がインストールされていません"
        read -p "インストールしますか? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            sudo apt-get update
            sudo apt-get install -y apache2
        else
            print_error "Apache2が必要です"
            exit 1
        fi
    else
        print_success "Apache2 OK"
    fi
    
    # SQLite3
    if ! command -v sqlite3 &> /dev/null; then
        print_warning "SQLite3がインストールされていません"
        sudo apt-get install -y sqlite3
    else
        print_success "SQLite3 OK"
    fi
}

# ディレクトリ作成
create_directories() {
    print_header "ディレクトリ作成"
    
    mkdir -p "$PROJECT_ROOT/uploads/images"
    mkdir -p "$PROJECT_ROOT/database"
    
    print_success "ディレクトリ作成完了"
}

# パーミッション設定
set_permissions() {
    print_header "パーミッション設定"
    
    # CGIスクリプトに実行権限
    find "$PROJECT_ROOT/cgi-bin" -name "*.py" -exec chmod +x {} \;
    print_success "CGIスクリプトに実行権限を付与"
    
    # データベースディレクトリ
    chmod 755 "$PROJECT_ROOT/database"
    chmod 755 "$PROJECT_ROOT/uploads"
    
    # Apacheユーザーに所有権を変更
    if [ -n "$SUDO_USER" ]; then
        sudo chown -R www-data:www-data "$PROJECT_ROOT/database"
        sudo chown -R www-data:www-data "$PROJECT_ROOT/uploads"
        print_success "www-dataに所有権を変更"
    else
        print_warning "sudo権限がないため、手動で所有権を変更してください:"
        print_info "sudo chown -R www-data:www-data $PROJECT_ROOT/database"
        print_info "sudo chown -R www-data:www-data $PROJECT_ROOT/uploads"
    fi
}

# データベース初期化
init_database() {
    print_header "データベース初期化"
    
    DB_PATH="$PROJECT_ROOT/database/manual_factory.db"
    
    if [ -f "$DB_PATH" ]; then
        read -p "既存のデータベースが見つかりました。再作成しますか? (y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_warning "データベース初期化をスキップしました"
            return
        fi
        rm "$DB_PATH"
    fi
    
    cd "$PROJECT_ROOT/database"
    python3 init_db.py << EOF
yes
EOF
    
    print_success "データベース初期化完了"
    print_info "初期管理者: admin@example.com / admin123"
}

# CGIスクリプトのshebang更新
update_shebang() {
    print_header "CGIスクリプト設定"
    
    PYTHON_PATH=$(which python3)
    
    for file in "$PROJECT_ROOT/cgi-bin/api"/*.py; do
        if [ -f "$file" ]; then
            # 最初の行をshebangに置き換え
            sed -i "1s|.*|#!$PYTHON_PATH|" "$file"
            print_success "更新: $(basename $file)"
        fi
    done
    
    print_info "shebangを #!$PYTHON_PATH に設定"
}

# Apache CGIモジュール有効化
enable_apache_cgi() {
    print_header "Apache CGI設定"
    
    if [ -n "$SUDO_USER" ] || [ "$EUID" -eq 0 ]; then
        sudo a2enmod cgi
        print_success "CGIモジュールを有効化"
    else
        print_warning "sudo権限がないため、手動でCGIモジュールを有効化してください:"
        print_info "sudo a2enmod cgi"
    fi
}

# Apacheサイト設定
create_apache_config() {
    print_header "Apacheサイト設定"
    
    SITE_NAME="manual_factory"
    CONFIG_FILE="/etc/apache2/sites-available/${SITE_NAME}.conf"
    
    if [ ! -f "$CONFIG_FILE" ]; then
        cat << EOF | sudo tee "$CONFIG_FILE" > /dev/null
<VirtualHost *:80>
    ServerName manual-factory.local
    DocumentRoot $PROJECT_ROOT

    <Directory $PROJECT_ROOT>
        Options +ExecCGI
        AddHandler cgi-script .py
        AllowOverride All
        Require all granted
    </Directory>

    <Directory $PROJECT_ROOT/cgi-bin>
        Options +ExecCGI
        SetHandler cgi-script
        Require all granted
    </Directory>

    ErrorLog \${APACHE_LOG_DIR}/${SITE_NAME}_error.log
    CustomLog \${APACHE_LOG_DIR}/${SITE_NAME}_access.log combined
</VirtualHost>
EOF
        print_success "Apacheサイト設定を作成"
        
        # サイトを有効化
        sudo a2ensite "$SITE_NAME"
        print_success "サイトを有効化"
    else
        print_warning "サイト設定が既に存在します: $CONFIG_FILE"
    fi
}

# Apache再起動
restart_apache() {
    print_header "Apache再起動"
    
    if [ -n "$SUDO_USER" ] || [ "$EUID" -eq 0 ]; then
        sudo systemctl restart apache2
        print_success "Apacheを再起動しました"
        
        # ステータス確認
        if sudo systemctl is-active --quiet apache2; then
            print_success "Apache起動中"
        else
            print_error "Apacheの起動に失敗しました"
            print_info "ログを確認: sudo journalctl -xeu apache2"
        fi
    else
        print_warning "sudo権限がないため、手動でApacheを再起動してください:"
        print_info "sudo systemctl restart apache2"
    fi
}

# 次のステップを表示
display_next_steps() {
    print_header "セットアップ完了"
    
    echo "次のステップ:"
    echo ""
    echo "1. /etc/hosts にエントリを追加（任意）:"
    echo "   127.0.0.1 manual-factory.local"
    echo ""
    echo "2. ブラウザでアクセス:"
    echo -e "   ${GREEN}http://localhost/manual_factory/login.html${NC}"
    echo "   または"
    echo -e "   ${GREEN}http://manual-factory.local/login.html${NC}"
    echo ""
    echo "3. 初期管理者アカウントでログイン:"
    echo -e "   Email: ${BOLD}admin@example.com${NC}"
    echo -e "   Password: ${BOLD}admin123${NC}"
    echo ""
    print_warning "※パスワードは必ず変更してください"
    echo ""
    echo "エラーログ確認:"
    echo "  sudo tail -f /var/log/apache2/manual_factory_error.log"
    echo ""
}

# メイン処理
main() {
    echo ""
    echo -e "${BOLD}============================================================${NC}"
    echo -e "${BOLD}手順書管理システム - Linux セットアップ${NC}"
    echo -e "${BOLD}============================================================${NC}"
    echo ""
    
    check_python
    check_packages
    create_directories
    init_database
    update_shebang
    set_permissions
    enable_apache_cgi
    create_apache_config
    restart_apache
    display_next_steps
}

# 実行
main
