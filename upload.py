import requests
from urllib.parse import quote
from requests_toolbelt.multipart.encoder import MultipartEncoder
import json
import glob
import time

# 登录
login_url = 'https://alist.265011.xyz/api/auth/login' #输入Alist地址
credentials = {'Username': 'xiguan', 'Password': '123654789'} #输入账户密码
response = requests.post(login_url, data=credentials, verify=False)
auth_data = json.loads(response.text)
token = auth_data.get('data', {}).get('token')

if not token:
    print("登录失败，请检查凭据")
    exit()

# 上传配置
upload_url = "https://alist.265011.xyz/api/fs/form"
patterns = ['AnyKernel3-KernelSU_Next-SUSFS-For-*', 'Image-KernelSU_Next-SUSFS-*']
max_retries = 10
retry_delay = 10

# 获取匹配文件列表
matched_files = []
for pattern in patterns:
    matched_files.extend(glob.glob(pattern))
matched_files = list(set(matched_files))  # 去重

if not matched_files:
    print("未找到匹配的文件")
    exit()

# 上传文件
for filename in matched_files:
    for attempt in range(max_retries):
        try:
            with open(filename, 'rb') as file:
                # 准备多部分表单数据
                multipart_data = MultipartEncoder(
                    fields={'file': (filename, file)}
                )

                # 构造请求头
                encoded_filename = quote(filename, 'utf-8')
                target_path_o = f'/{encoded_filename}' #上传路径
                target_path = target_path_o.encode('utf-8')
                
                headers = {
                    'Authorization': token,
                    'Content-Type': multipart_data.content_type,
                    'file-path': target_path
                }

                # 发送请求
                response = requests.put(upload_url, data=multipart_data, headers=headers, verify=False)

                if response.status_code == 200:
                    print(f"✓ 成功上传 {filename}")
                    break
                else:
                    print(f"× 上传失败 [{response.status_code}]: {response.text}")
                    
        except Exception as error:
            print(f"! 上传异常: {str(error)}")

        # 重试逻辑
        if attempt < max_retries - 1:
            print(f"↻ 尝试重试 {filename} ({attempt + 1}/{max_retries})...")
            time.sleep(retry_delay)
        else:
            print(f"× 已达到最大重试次数: {filename}")

print("所有文件处理完成")
