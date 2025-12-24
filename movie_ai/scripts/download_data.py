import os
import urllib.request
import zipfile

def download_ml100k(data_dir="./datasets"):
    url = "http://files.grouplens.org/datasets/movielens/ml-100k.zip"
    os.makedirs(data_dir, exist_ok=True)
    
    # 下载
    zip_path = os.path.join(data_dir, "ml-100k.zip")
    if not os.path.exists(zip_path):
        print("正在下载 MovieLens 100K...")
        urllib.request.urlretrieve(url, zip_path)
    
    # 解压
    extract_dir = os.path.join(data_dir, "ml-100k")
    if not os.path.exists(extract_dir):
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(data_dir)
        print(f"数据集已解压到 {extract_dir}")
    
    return extract_dir

data_path = download_ml100k()