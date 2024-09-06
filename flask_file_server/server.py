from flask import Flask, render_template, send_from_directory, request, abort
from werkzeug.utils import safe_join
import os
from datetime import datetime
import math
import argparse

app = Flask(__name__)

# 转换文件大小为human-readable格式
def human_readable_size(size, decimal_places=2):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.{decimal_places}f} {unit}"
        size /= 1024.0

# 获取文件类型
def get_file_type(file_path):
    if os.path.isdir(file_path):
        return 'Directory'
    else:
        return os.path.splitext(file_path)[1] or 'File'

# 获取文件信息
def get_file_info(folder_path):
    files_info = []
    try:
        for file_name in sorted(os.listdir(folder_path)):
            file_path = os.path.join(folder_path, file_name)
            if os.path.isdir(file_path) or os.path.isfile(file_path):
                stat_info = os.stat(file_path)
                files_info.append({
                    'name': file_name,
                    'size': stat_info.st_size,  # 保留字节大小，用于排序
                    'human_readable_size': human_readable_size(stat_info.st_size),  # 转换为可读大小
                    'creation_time': datetime.fromtimestamp(stat_info.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                    'modification_time': datetime.fromtimestamp(stat_info.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                    'type': get_file_type(file_path)
                })
    except Exception as e:
        print(f"Error accessing folder: {e}")
        abort(404)
    return files_info

# 文件排序逻辑
def sort_files(files_info, sort_by, order):
    reverse = (order == 'desc')
    if sort_by == 'name':
        files_info.sort(key=lambda x: x['name'].lower(), reverse=reverse)
    elif sort_by == 'size':
        files_info.sort(key=lambda x: x['size'], reverse=reverse)
    elif sort_by == 'creation_time':
        files_info.sort(key=lambda x: x['creation_time'], reverse=reverse)
    elif sort_by == 'modification_time':
        files_info.sort(key=lambda x: x['modification_time'], reverse=reverse)
    elif sort_by == 'type':
        files_info.sort(key=lambda x: x['type'].lower(), reverse=reverse)

# 路由：展示文件夹内容
@app.route('/')
@app.route('/<path:subpath>')
def list_files(subpath=''):
    folder_path = os.path.join(app.config['ROOT_FOLDER'], subpath)
    if not os.path.exists(folder_path):
        abort(404)

    # 获取排序参数
    sort_by = request.args.get('sort_by', 'name')
    order = request.args.get('order', 'asc')

    # 分页设置
    page = int(request.args.get('page', 1))
    items_per_page = 100
    start = (page - 1) * items_per_page
    end = start + items_per_page

    # 获取文件信息并排序
    files_info = get_file_info(folder_path)
    sort_files(files_info, sort_by, order)
    
    # 分页
    paginated_files = files_info[start:end]
    total_pages = math.ceil(len(files_info) / items_per_page)

    # 反转排序顺序（点击同一个表头时）
    next_order = 'desc' if order == 'asc' else 'asc'

    return render_template(
        'index.html',
        files=paginated_files,
        subpath=subpath,
        page=page,
        total_pages=total_pages,
        sort_by=sort_by,
        order=order,
        next_order=next_order
    )

@app.route('/download/<path:filepath>')
def download_file(filepath):
    # 使用 safe_join 确保文件路径的安全性
    safe_path = safe_join(app.config['ROOT_FOLDER'], filepath)
    
    if not os.path.exists(safe_path):
        abort(404)

    # 获取文件夹路径和文件名
    folder_path = os.path.dirname(safe_path)
    filename = os.path.basename(safe_path)
    
    # 使用 send_from_directory 发送文件
    return send_from_directory(folder_path, filename, as_attachment=True)


if __name__ == '__main__':
    # 使用 argparse 解析命令行参数  
    parser = argparse.ArgumentParser(description="Simple File Browser Web Service")
    parser.add_argument("--root", type=str, default=os.getcwd(), help="The root folder to serve files from (default: current working directory)")
    parser.add_argument('--host', type=str, default='0.0.0.0', help="The host URL to bind to (default: 0.0.0.0)")
    parser.add_argument('--port', type=int, default=8080, help="The port to bind to (default: 8080)")
    args = parser.parse_args()

    # 设置应用配置  
    app.config['ROOT_FOLDER'] = args.root
    print(f"Serving files from: {app.config['ROOT_FOLDER']}") 

    # 启动 Flask 应用
    app.run(host=args.host, port=args.port, debug=True)
