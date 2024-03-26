#/bin/python

import datetime
import os

def sanitize_filename(filename):
    """简单地清理文件名中可能不被支持的字符"""
    return filename.replace(":", "-").replace("*", "-").replace("?", "")

def create_markdown_file():
    # 获取当前日期
    current_date = datetime.datetime.now().strftime('%Y-%m-%d')
    
    # 用户输入
    subject = input("请输入文档的主题: ").strip()
    title = subject  # 可以根据需要调整title的获取方式
    tags = input("请输入标签（用空格分隔）: ").strip()

    # 确保文件名符合操作系统文件命名规范
    sanitized_subject = sanitize_filename(subject)

    # 文件名格式化
    file_name = f"{current_date}-{sanitized_subject}.md"
    
    # 在这里，你可以指定一个特定的路径来存放markdown文件
    # 例如：directory_path = "/path/to/your/directory"
    # 或在Windows上，例如：directory_path = "C:\\path\\to\\your\\directory"
    # 以下使用当前目录作为示例
    directory_path = os.getcwd()  # 获取当前工作目录
    full_path = os.path.join(directory_path, "_posts", file_name)

    # 文档内容
    content = f"""---
layout: post
title: {title}
date: {current_date}
tags: {tags}
comments: true
author: lewx
---"""

    # 创建并写入文件
    with open(full_path, "w", encoding="utf-8") as file:
        file.write(content)
    
    print(f"文件 '{file_name}' 已创建在 '{full_path}'。")

if __name__ == "__main__":
    create_markdown_file()
