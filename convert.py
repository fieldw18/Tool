import re

def convert_proxy_line(line):
    """将单行代理配置转换为目标格式"""
    try:
        # 清理行，去除首尾空格
        line = line.strip()
        if not line or line.startswith('#'):
            return None

        # 解析原始格式
        # 示例：socks5=47.83.244.195:10000, username=123, password=123, fast-open=false, udp-relay=false, tag=🇭🇰 香港
        parts = dict(item.strip().split('=', 1) for item in line.split(',') if '=' in item)
        
        # 提取必要字段
        socks5 = parts.get('socks5', '').strip()
        username = parts.get('username', '').strip()
        password = parts.get('password', '').strip()
        tag = parts.get('tag', '').strip()

        if not socks5 or not username or not password:
            return None

        # 处理 tag：将 "🇭🇰 香港" 转换为 "中国_香港"
        tag_map = {
            '🇭🇰 香港': '中国_香港',
            # 可扩展其他映射，例如：
            # '🇺🇳 美国': '美国',
            # '🇯🇵 日本': '日本',
        }
        converted_tag = tag_map.get(tag, tag.replace(' ', '_'))  # 默认替换空格为下划线

        # 构造目标格式
        return f"socks5://{username}:{password}@{socks5}#{converted_tag}"
    except Exception as e:
        print(f"解析错误: {line}, 错误: {str(e)}")
        return None

def main():
    input_file = 'proxies.txt'
    output_file = 'converted_proxies.txt'
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"错误: 文件 {input_file} 不存在")
        return

    converted_lines = []
    for line in lines:
        converted = convert_proxy_line(line)
        if converted:
            converted_lines.append(converted)

    # 写入输出文件
    with open(output_file, 'w', encoding='utf-8') as f:
        for line in converted_lines:
            f.write(line + '\n')
    
    print(f"转换完成，结果保存到 {output_file}")
    print(f"共处理 {len(lines)} 行，成功转换 {len(converted_lines)} 行")

if __name__ == '__main__':
    main()