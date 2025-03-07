import os
import re
import yaml

# 输入和输出目录
input_dir = "Loon/Plugin"
output_dir = "Egern/Module"

# 创建输出目录
os.makedirs(output_dir, exist_ok=True)

# 解析 Loon .plugin 文件
def parse_loon_plugin(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    config = {
        "metadata": {},
        "url_rewrites": [],
        "http_response": [],
        "scripts": [],
        "remote_scripts": [],
        "mitm": {"hostnames": []}
    }
    
    section = None
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#!"):
            if line.startswith("#!name"):
                config["metadata"]["name"] = line.split("=", 1)[1].strip()
            elif line.startswith("#!desc"):
                config["metadata"]["description"] = line.split("=", 1)[1].strip()
            elif line.startswith("#!author"):
                config["metadata"]["author"] = line.split("=", 1)[1].strip()
            continue
        
        if line.startswith("[Rewrite]"):
            section = "rewrite"
        elif line.startswith("[MitM]"):
            section = "mitm"
        elif line.startswith("[Script]"):
            section = "script"
        elif line.startswith("[Remote Script]"):
            section = "remote_script"
        elif line.startswith("[HTTP Response]"):
            section = "http_response"
        elif line:
            if section == "rewrite":
                parts = line.split()
                if len(parts) >= 3:
                    pattern, status_code, target = parts[0], parts[1], parts[2]
                    config["url_rewrites"].append({
                        "match": pattern,
                        "status_code": int(status_code),
                        "location": target
                    })
            elif section == "mitm" and line.startswith("hostname"):
                hostname = line.split("=", 1)[1].strip()
                config["mitm"]["hostnames"] = [h.strip() for h in hostname.split(",")]
            elif section == "script":
                parts = line.split()
                if len(parts) >= 4:
                    name, type_, pattern, script_path = parts[0], parts[1], parts[2], parts[3]
                    config["scripts"].append({
                        "name": name,
                        "type": type_,
                        "match": pattern,
                        "script_path": script_path
                    })
            elif section == "remote_script":
                parts = line.split()
                if len(parts) >= 4:
                    name, type_, pattern, url = parts[0], parts[1], parts[2], parts[3]
                    config["remote_scripts"].append({
                        "name": name,
                        "type": type_,
                        "match": pattern,
                        "url": url
                    })
            elif section == "http_response":
                # 假设格式为: pattern response-body-json-jq 'filter'
                parts = re.split(r'\s+', line, 2)
                if len(parts) == 3 and parts[1] == "response-body-json-jq":
                    pattern, _, jq_filter = parts
                    jq_filter = jq_filter.strip("'")
                    config["http_response"].append({
                        "match": pattern,
                        "filter": jq_filter,
                        "type": "response_jq"
                    })
    
    return config

# 转换为 Egern .yaml 格式
def convert_to_egern(config):
    egern_config = {
        "name": config["metadata"].get("name", "Converted Module"),
        "description": config["metadata"].get("description", "Converted from Loon"),
        "author": config["metadata"].get("author", "Unknown"),
        "url_rewrites": [],
        "http_response": [],
        "scripts": [],
        "remote_scripts": [],
        "mitm": {
            "hostnames": {
                "includes": config["mitm"]["hostnames"]
            }
        }
    }
    
    # 转换 [Rewrite]
    for rewrite in config["url_rewrites"]:
        match = rewrite["match"].replace(r"(https:\/\/)?", "^https?:\\/\\/")
        location = rewrite["location"].replace("$2", "$1")
        egern_config["url_rewrites"].append({
            "match": match,
            "location": location,
            "status_code": rewrite["status_code"]
        })
    
    # 转换 [HTTP Response]
    for response in config["http_response"]:
        egern_config["http_response"].append({
            "match": response["match"],
            "filter": response["filter"],
            "type": response["type"]
        })
    
    # 转换 [Script]
    for script in config["scripts"]:
        egern_config["scripts"].append({
            "name": script["name"],
            "type": script["type"],
            "match": script["match"],
            "script_path": script["script_path"]
        })
    
    # 转换 [Remote Script]
    for remote_script in config["remote_scripts"]:
        egern_config["remote_scripts"].append({
            "name": remote_script["name"],
            "type": remote_script["type"],
            "match": remote_script["match"],
            "url": remote_script["url"]
        })
    
    return egern_config

# 主函数
def main():
    # 输入文件
    input_file = os.path.join(input_dir, "turrit.plugin")
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found!")
        return
    
    # 解析 Loon 插件
    config = parse_loon_plugin(input_file)
    if not any([config["url_rewrites"], config["http_response"], config["scripts"], config["remote_scripts"], config["mitm"]["hostnames"]]):
        print("No actionable content found in Loon plugin!")
        return
    
    # 转换为 Egern 格式并保存
    egern_config = convert_to_egern(config)
    output_file = os.path.join(output_dir, "turrit.yaml")
    with open(output_file, "w", encoding="utf-8") as f:
        yaml.dump(egern_config, f, allow_unicode=True, sort_keys=False)
    print(f"Converted Loon plugin to Egern module: {output_file}")

if __name__ == "__main__":
    main()