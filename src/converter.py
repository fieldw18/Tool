import re
import sys
from pathlib import Path
from jinja2 import Template

def parse_loon(content):
    # 保持原有解析逻辑不变
    # 返回包含 rules/mitm 等数据的字典

def generate_egern(data, template_path):
    # 保持原有模板渲染逻辑不变

if __name__ == "__main__":
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    
    # 确保输出目录存在
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    # 执行转换
    with open(input_path) as f:
        content = f.read()
    
    data = parse_loon(content)
    
    with open(output_path, 'w') as f:
        f.write(generate_egern(data, "src/template.j2"))
