import jinja2
import os

from importlib import resources

from computenestcli.common import project_setup_constant


def indent(d, width=10, first_line_indent=False, strip=False):
    result_lines = []  # 使用列表来构建结果，这样就可以避免不必要的字符串连接
    if isinstance(d, (str, bool, int)):
        lines = str(d).split('\n')
        if strip and lines[-1] == '':  # 如果开启了strip并且最后一个元素为空，则去除
            lines.pop()
        for i, line in enumerate(lines):
            if i == 0 and not first_line_indent:
                result_lines.append(line)  # 第一行不缩进
            else:
                result_lines.append((' ' * width) + line)  # 其余的行缩进
    elif isinstance(d, dict):
        for key, value in d.items():
            formatted_key = str(key) + ": "
            if first_line_indent or result_lines:
                formatted_key = (' ' * width) + formatted_key
            result_lines.append(formatted_key + indent(value, width + 2, first_line_indent=True, strip=strip))
    elif isinstance(d, list):
        for i, item in enumerate(d):
            prefix = "- " if i == 0 and not first_line_indent else (' ' * (width - 2) + "- ")
            result_lines.append(prefix + indent(item, width + 2, first_line_indent=True, strip=strip))

    result = '\n'.join(result_lines)
    return result.rstrip() if strip else result  # 移除结果字符串末尾的空格和换行符


class Jinja2Processor:

    def __init__(self):
        self.env = jinja2.Environment(autoescape=False)

        self.env.filters['indent'] = indent

    def process(self, file_path, parameters, output_path, package_name=None):
        if package_name:
            # 加载包中的模板
            with resources.open_text(package_name, file_path) as f:
                template_text = f.read()

            # 从字符串加载模板
            template = self.env.from_string(template_text)
        else:
            # 加载文件系统上的模板
            file_dir, file_name = os.path.split(file_path)
            self.env.loader = jinja2.FileSystemLoader(file_dir)
            template = self.env.get_template(file_name)

        # 渲染模板
        rendered_content = template.render(parameters)

        # 将渲染内容写入输出文件
        with open(output_path, "w") as f:
            f.write(rendered_content)
