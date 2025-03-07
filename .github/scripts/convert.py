import os
import re
import yaml

# Loon 插件目录
LOON_PLUGIN_DIR = "Loon/Plugin"
# Egern 模块目录
EGERN_MODULE_DIR = "Egern/Module"

# 确保输出目录存在
os.makedirs(EGERN_MODULE_DIR, exist_ok=True)

# 解析 Loon `.plugin` 文件
def parse_loon_plugin(content):
    lines = content.split("\n")
    yaml_data = {
        "name": "",
        "description": "",
        "open_url": "",
        "author": "",
        "icon": "",
        "rules": [],
        "map_locals": [],
        "body_rewrites": [],
        "mitm": {"hostnames": {"includes": []}},
    }

    section = None  # 当前解析的部分

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue  # 跳过空行和注释

        # 解析插件头部信息
        if line.startswith("#!name="):
            yaml_data["name"] = line.split("=", 1)[1].strip()
        elif line.startswith("#!desc="):
            yaml_data["description"] = line.split("=", 1)[1].strip()
        elif line.startswith("#!openUrl="):
            yaml_data["open_url"] = line.split("=", 1)[1].strip()
        elif line.startswith("#!author="):
            yaml_data["author"] = line.split("=", 1)[1].strip()
        elif line.startswith("#!icon="):
            yaml_data["icon"] = line.split("=", 1)[1].strip()

        # 解析各个模块部分
        elif line.startswith("[Rule]"):
            section = "rules"
        elif line.startswith("[Map Local]"):
            section = "map_locals"
        elif line.startswith("[MITM]"):
            section = "mitm"

        # 解析 Rule
        elif section == "rules":
            if "DOMAIN," in line:
                domain = line.split(",")[1].strip()
                yaml_data["rules"].append({"domain": {"match": domain, "policy": "REJECT"}})
            elif "AND," in line:
                parts = re.findall(r"\((.*?)\)", line)
                and_rule = {"match": [], "policy": "REJECT"}
                for part in parts:
                    key, value = part.split(",", 1)
                    key, value = key.strip(), value.strip()
                    if key == "IP-ASN":
                        and_rule["match"].append({"asn": {"match": value, "no_resolve": True}})
                    elif key == "DEST-PORT":
                        and_rule["match"].append({"dest_port": {"match": value}})
                    elif key == "PROTOCOL":
                        and_rule["match"].append({"protocol": {"match": value}})
                yaml_data["rules"].append(and_rule)

        # 解析 Map Local
        elif section == "map_locals":
            match = re.match(r'^\^(.+?)\s+data-type=text\s+data="(.+?)"\s+status-code=(\d+)', line)
            if match:
                yaml_data["map_locals"].append({
                    "match": match.group(1),
                    "status_code": int(match.group(3)),
                    "body": match.group(2),
                })

        # 解析 MITM
        elif section == "mitm":
            if "hostname" in line:
                hosts = re.findall(r"[\w\.\-\*]+", line)
                yaml_data["mitm"]["hostnames"]["includes"].extend(hosts)

    return yaml_data


# 遍历 Loon 插件目录并转换
for filename in os.listdir(LOON_PLUGIN_DIR):
    if filename.endswith(".plugin"):
        plugin_path = os.path.join(LOON_PLUGIN_DIR, filename)
        yaml_filename = filename.replace(".plugin", ".yaml")
        yaml_path = os.path.join(EGERN_MODULE_DIR, yaml_filename)

        # 读取 `.plugin` 文件内容
        with open(plugin_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 解析并转换
        yaml_data = parse_loon_plugin(content)

        # 保存为 `.yaml`
        with open(yaml_path, "w", encoding="utf-8") as f:
            yaml.dump(yaml_data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)

        print(f"✅ 转换完成: {plugin_path} -> {yaml_path}")

print("🎉 所有插件转换完成！")
