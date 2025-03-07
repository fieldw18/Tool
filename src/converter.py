import re
import sys
from pathlib import Path
from jinja2 import Template

def parse_loon(content):
    result = {
        "rules": [],
        "map_locals": [],
        "mitm": {"hostnames": {"includes": []}}
    }
    
    current_section = None
    for line in content.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        # 检测段落切换
        if line.startswith('['):
            current_section = line[1:-1].lower()
            continue
            
        # 解析规则
        if current_section == 'rule':
            if 'DOMAIN' in line:
                domain = line.split(',')[1]
                result["rules"].append({
                    "domain": {"match": domain, "policy": "REJECT"}
                })
                
        # 解析MITM
        elif current_section == 'mitm':
            if 'hostname' in line:
                hosts = line.split('=')[1].strip().split(',')
                result["mitm"]["hostnames"]["includes"].extend(
                    [h.strip() for h in hosts if h.strip()]
                )
    
    return result

def generate_egern(data, template_path):
    with open(template_path) as f:
        template = Template(f.read())
    return template.render(data)

if __name__ == "__main__":
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    
    with open(input_path) as f:
        content = f.read()
    
    data = parse_loon(content)
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(generate_egern(data, "src/template.egern.j2"))
