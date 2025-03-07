import os
import re
import yaml
from pathlib import Path

# 输入和输出目录
loon_dir = "Loon/Plugin"
egern_dir = "Egern/Module"

# 确保输出目录存在
Path(egern_dir).mkdir(parents=True, exist_ok=True)

def parse_loon_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 初始化数据结构
    egern_data = {
        'name': '',
        'description': '',
        'open_url': '',
        'author': '',
        'icon': '',
        'rules': [],
        'map_locals': [],
        'mitm': {'hostnames': {'includes': []}}
    }

    # 解析 metadata
    metadata = {}
    for line in content.splitlines():
        if line.startswith('#!'):
            key, value = line[2:].split('=', 1)
            metadata[key.strip()] = value.strip()

    egern_data['name'] = metadata.get('name', '')
    egern_data['description'] = metadata.get('desc', '')
    egern_data['open_url'] = metadata.get('openUrl', '')
    egern_data['author'] = metadata.get('author', '')
    egern_data['icon'] = metadata.get('icon', '')

    # 解析 [Rule]
    rule_section = re.search(r'\[Rule\](.*?)(?=\[|$)', content, re.DOTALL)
    if rule_section:
        for line in rule_section.group(1).splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('DOMAIN,'):
                _, match, policy = line.split(',')
                egern_data['rules'].append({
                    'domain': {'match': match, 'policy': policy}
                })
            elif line.startswith('AND,'):
                conditions = re.findall(r'\((.*?)\)', line)
                and_rule = {'and': {'match': [], 'policy': 'REJECT'}}
                for cond in conditions:
                    key, value = cond.split(',', 1)
                    if key == 'IP-ASN':
                        and_rule['and']['match'].append({'asn': {'match': value.split(',')[0], 'no_resolve': 'no-resolve' in value}})
                    elif key == 'DEST-PORT':
                        and_rule['and']['match'].append({'dest_port': {'match': value}})
                    elif key == 'PROTOCOL':
                        and_rule['and']['match'].append({'protocol': {'match': value}})
                egern_data['rules'].append(and_rule)

    # 解析 [Map Local]
    map_local_section = re.search(r'\[Map Local\](.*?)(?=\[|$)', content, re.DOTALL)
    if map_local_section:
        for line in map_local_section.group(1).splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            match = re.match(r'^(.*?)\s+data-type=text\s+data="(.+)"\s+status-code=(\d+)', line)
            if match:
                url, body, status_code = match.groups()
                egern_data['map_locals'].append({
                    'match': url,
                    'status_code': int(status_code),
                    'body': body
                })

    # 解析 [MITM]
    mitm_section = re.search(r'\[MITM\](.*?)(?=\[|$)', content, re.DOTALL)
    if mitm_section:
        for line in mitm_section.group(1).splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('hostname ='):
                hostnames = line.split('=', 1)[1].strip().replace('%APPEND% ', '').split(', ')
                egern_data['mitm']['hostnames']['includes'] = hostnames

    # 删除空的字段，但保留 mitm 结构
    if not egern_data['rules']:
        del egern_data['rules']
    if not egern_data['map_locals']:
        del egern_data['map_locals']
    if not egern_data['mitm']['hostnames']['includes']:
        del egern_data['mitm']['hostnames']['includes']

    return egern_data

def convert_to_egern_yaml(loon_file):
    # 解析 Loon 文件
    egern_data = parse_loon_file(loon_file)

    # 生成输出文件名
    output_file = os.path.join(egern_dir, os.path.basename(loon_file).replace('.plugin', '.yaml'))

    # 写入 YAML 文件
    with open(output_file, 'w', encoding='utf-8') as f:
        yaml.dump(egern_data, f, allow_unicode=True, sort_keys=False)

    print(f"Converted {loon_file} to {output_file}")

# 遍历 Loon/Plugin 目录
for filename in os.listdir(loon_dir):
    if filename.endswith('.plugin'):
        loon_file = os.path.join(loon_dir, filename)
        convert_to_egern_yaml(loon_file)