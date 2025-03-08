import requests
from urllib.parse import quote
from requests_toolbelt.multipart.encoder import MultipartEncoder
import json
import time
import fnmatch


def login():
    """获取token"""
    url = 'https://alist.265011.xyz/api/auth/login' #输入Alist地址
    d = {'Username': 'xiguan', 'Password': '123654789'} #输入账户密码
    r = requests.post(url, data=d, verify=False)
    data = json.loads(r.text)
    return data.get('data').get('token')


def list_files(token, dir_path, max_retries=3, retry_delay=5):
    """获取目录文件列表"""
    url = "https://alist.265011.xyz/api/fs/list"
    headers = {
        'Authorization': token,
        'Content-Type': 'application/json'
    }
    data = {"path": dir_path}
    
    for retry in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=data, verify=False)
            response.raise_for_status()
            files = response.json().get('data', {}).get('content', [])
            return [f['name'] for f in files if f.get('name')]
        except Exception as e:
            print(f"列表获取失败 (重试 {retry+1}/{max_retries}): {str(e)}")
            time.sleep(retry_delay)
    raise Exception("获取文件列表失败")


def remove_files(token, file_names, dir_path, max_retries=3, retry_delay=5):
    """批量删除文件"""
    url = "https://alist.265011.xyz/api/fs/remove"
    headers = {
        'Authorization': token,
        'Content-Type': 'application/json'
    }
    
    data = {
        "names": file_names,
        "dir": dir_path
    }
    
    for retry in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=data, verify=False)
            response.raise_for_status()
            print(f"成功删除 {len(file_names)} 个文件")
            return
        except Exception as e:
            print(f"删除失败 (重试 {retry+1}/{max_retries}): {str(e)}")
            time.sleep(retry_delay)
    print("文件删除最终失败")


if __name__ == "__main__":
    token = login()
    dir_path = "/"
    patterns = [
        "Image-KernelSU_Next-SUSFS-*",
        "AnyKernel3_KernelSU_Next-For-*"
    ]
    
    try:
        # 获取目录文件列表
        all_files = list_files(token, dir_path)
        print(f"找到 {len(all_files)} 个文件")
        
        # 过滤匹配文件
        matched_files = []
        for pattern in patterns:
            matched_files += fnmatch.filter(all_files, pattern)
        matched_files = list(set(matched_files))  # 去重
        
        if not matched_files:
            print("没有找到匹配文件")
            exit()
            
        print(f"匹配到 {len(matched_files)} 个文件:")
        print("\n".join(matched_files))
        
        # 执行删除操作
        remove_files(token, matched_files, dir_path)
        
    except Exception as e:
        print(f"程序运行异常: {str(e)}")
        exit(1)