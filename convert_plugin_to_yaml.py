import os
import re
import yaml

# 设定文件路径
LOON_PLUGIN_DIR = "Loon/Plugin"
EGERN_MODULE_DIR = "Egern/Module"

# 确保 Egern 目录存在
os.makedirs(EGERN_MODULE_DIR, exist_ok=True)

def parse_loon_plugin(file_path):
    """解析 Loon 插件格式并转换为 Egern 的 YAML 结构"""
    yaml_data = {
        "name": "",
        "description": "",
        "open_url": "",
        "author": "",
        "icon": "",
        "rules": [],
        "map_locals": [],
        "body_rewrites": [],
        "mitm": {"hostnames": {"includes": []}}
    }

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    for line in lines:
        line = line.strip()
        
        # 解析元信息
        if line.startswith("#!name="):
            yaml_data["name"] = line.replace("#!name=", "").strip()
        elif line.startswith("#!desc="):
            yaml_data["description"] = line.replace("#!desc=", "").strip()
        elif line.startswith("#!openUrl="):
            yaml_data["open_url"] = line.replace("#!openUrl=", "").strip()
        elif line.startswith("#!author="):
            yaml_data["author"] = line.replace("#!author=", "").strip()
        elif line.startswith("#!icon="):
            yaml_data["icon"] = line.replace("#!icon=", "").strip()
        
        # 解析规则
        elif line.startswith("DOMAIN,"):
            domain = line.replace("DOMAIN,", "").strip()
            yaml_data["rules"].append({"domain": {"match": domain, "policy": "REJECT"}})
        
        elif line.startswith("AND,"):
            match = re.findall(r"IP-ASN,(\d+)", line)
            if match:
                yaml_data["rules"].append({
                    "and": {
                        "match": [{"asn": {"match": match[0], "no_resolve": True}}],
                        "policy": "REJECT"
                    }
                })

        # 解析 MITM
        elif "hostname = %APPEND%" in line:
            hosts = line.split("%APPEND%")[-1].strip().split(", ")
            yaml_data["mitm"]["hostnames"]["includes"].extend(hosts)

    return yaml_data

def convert_plugins():
    """遍历 Loon 目录并转换所有插件"""
    for filename in os.listdir(LOON_PLUGIN_DIR):
        if filename.endswith(".plugin"):
            file_path = os.path.join(LOON_PLUGIN_DIR, filename)
            yaml_data = parse_loon_plugin(file_path)

            # 生成 YAML 文件
            yaml_filename = filename.replace(".plugin", ".yaml")
            yaml_path = os.path.join(EGERN_MODULE_DIR, yaml_filename)
            
            with open(yaml_path, "w", encoding="utf-8") as yaml_file:
                yaml.dump(yaml_data, yaml_file, allow_unicode=True, default_flow_style=False)

            print(f"转换完成: {filename} → {yaml_filename}")

if __name__ == "__main__":
    convert_plugins()
