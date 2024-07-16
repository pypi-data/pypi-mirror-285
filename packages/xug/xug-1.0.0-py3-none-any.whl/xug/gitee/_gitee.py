import base64
import os
import requests
from tqdm import tqdm
import random
from pathlib import Path


def upload_file(
    file_path,
    rename,
    target_path="",
    owner="",
    repo_path="",
    access_token="",
    message="upload file",
):
    '''
    上传文件到gitee仓库

    :param file_path: 文件路径
    :param rename: 重命名
    :param target_path: 目标路径
    :param owner: 仓库拥有者
    :param repo_path: 仓库路径
    :param access_token: 访问令牌
    :param message: 提交信息
    '''
    base_url = "https://gitee.com/api/v5/repos/"

    try:
        with open(file_path, "rb") as file:
            file_content = base64.b64encode(file.read()).decode("utf-8")

        filename = rename or os.path.basename(file_path)
        target_path = os.path.join(target_path, filename)
        data = {
            "access_token": access_token,
            "message": message,
            "content": file_content,
        }

        api_url = base_url + owner + "/" + repo_path + "/contents/" + target_path
        response = requests.post(api_url, data=data)

        if response.status_code == 400:
            update_data = {
                "access_token": access_token,
                "content": file_content,
                "sha": "",
                "message": "update file",
            }

            get_file_url = f"https://gitee.com/api/v5/repos/{owner}/{repo_path}/contents/{target_path}"
            get_file_response = requests.get(
                get_file_url, params={"access_token": access_token}
            )

            if get_file_response.status_code == 200:
                sha_value = get_file_response.json().get("sha", "")
                update_data["sha"] = sha_value

                update_url = f"https://gitee.com/api/v5/repos/{owner}/{repo_path}/contents/{target_path}"
                response = requests.put(update_url, data=update_data)

        response.raise_for_status()

        return response

    except Exception as e:
        print(e)



def download_file(
    remote_path,
    rename,
    save_path="./",
    repo_path="",
    owner="",
    access_token="",
    overwrite=False,
):
    '''
    下载文件到本地
    :param remote_path: 远程文件路径
    :param rename: 重命名
    :param save_path: 保存路径
    :param repo_path: 仓库路径
    :param owner: 仓库拥有者
    :param access_token: 访问令牌
    :param overwrite: 是否覆盖
    '''
    if access_token=='':
        url = f"https://gitee.com/{owner}/{repo_path}/raw/master/{remote_path}?random={str(random.randint(1, 1000))}"
    else:
        url = f"https://gitee.com/api/v5/repos/{owner}/{repo_path}/raw/{remote_path}?random={str(random.randint(1, 1000))}"
    try:
        file_name = rename or os.path.basename(remote_path)
        file_path = Path(os.path.join(save_path, file_name))

        head_response = requests.head(
            url,
            params={
                "access_token": access_token,
            },
        )
        if head_response.status_code != 200:
            print(f"远程文件丢失，更新失败: {head_response.status_code}")
            return False

        if not overwrite and file_path.exists():
            print(f"文件 '{file_name}' 已存在，将不再下载。")
            return True

        response = requests.get(
            url,
            stream=True,
            params={
                "access_token": access_token,
            },
        )

        total_size = int(response.headers.get("content-length", 0))

        block_size = 1024
        progress_bar = tqdm(
            total=total_size,
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            miniters=1,
            desc="Downloading",
        )
        with open(file_path, "wb") as file:
            for data in response.iter_content(block_size):
                progress_bar.update(len(data))
                file.write(data)
        progress_bar.close()
        print(f"{file_name}已下载到{save_path}")
        return True
    except Exception as e:
        print(f"下载失败: {e}")
        return False


def get_remote_text(remote_path, repo_path="", owner=""):
    '''
    获取远程文本内容
    :param remote_path: 远程文件路径
    :param repo_path: 仓库路径
    :param owner: 仓库拥有者
    '''
    url = f"https://gitee.com/{owner}/{repo_path}/raw/master/{remote_path}?random={str(random.randint(1, 1000))}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        content = (
            response.content.decode("unicode_escape")
            .encode("latin1")
            .decode("utf-8")
            .strip()
        )
        return content
    except requests.exceptions.RequestException as e:
        return None
