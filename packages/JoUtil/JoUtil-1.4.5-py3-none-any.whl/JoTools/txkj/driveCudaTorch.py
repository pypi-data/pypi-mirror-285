# -*- coding: utf-8  -*-
# -*- author: jokker -*-


from JoTools.utils.ScrapyUtil import ScrapyUtil

# Linux下PyTorch、CUDA Toolkit 及显卡驱动版本对应关系 refer : https://blog.csdn.net/weixin_42069606/article/details/105198845

# todo torch | cuda | drive | python 之间的关系
    # 检测模型代码能否运行取决于 （1）python 版本 （2）torch 版本
    # torch 版本取决于 cuda 版本
    # cuda 版本取决于 NVIDIA drive 版本

# todo drive    下载 | 安装 | 查看
    # 下载 http://download.nvidia.com/XFree86/Linux-x86_64/
    # 下载速度慢 -- 使用百度网盘离线下载，
        # 找到下载网址（F12 查看），网址路径 + 驱动名， http://download.nvidia.com/XFree86/Linux-x86_64/430.50 + NVIDIA-Linux-x86_64-430.50.run
        # 复制到百度网盘，使用离线下载
        # 完整示例：http://download.nvidia.com/XFree86/Linux-x86_64/418.88/NVIDIA-Linux-x86_64-418.88.run
    # 查看 nvidia-smi

# todo cuda     下载 | 安装 | 配置 | 查看
    # 下载 https://developer.nvidia.com/cuda-toolkit-archive
    # 安装 https://zhuanlan.zhihu.com/p/112138261
    # 查看 nvidia-smi
    # 配置
        # sudo vim ~/.bashrc
        # 如果有其他版本的 cuda，注释相关的代码
        # 添加下面两行预计
        # export PATH="/usr/local/cuda-10.1/bin:$PATH"
        # export LD_LIBRARY_PATH="/usr/local/cuda-10.1/lib64:$LD_LIBRARY_PATH"
        # 保存关闭后source文件使配置生效：
        # source ~/.bashrc

# todo torch    下载 | 安装 | 查看
    # 下载 https://download.pytorch.org/whl/torch_stable.html
    # 安装 pip install *.whl
    # 查看 pip list

# todo Anaconda 下载 | 安装 | 配置 | 查看
    # 配置 /home/user .bashrc 文件
    #

# todo 模型加密

    #




class DriveCudaTorch():

    cuda_drive_dict = {
        "CUDA_11.1":{"Linux"}
    }

    def __init__(self):
        pass


if __name__ == "__main__":



    url = r'https://download.pytorch.org/whl/torch_stable.html'
    bs = ScrapyUtil.get_bs_obj_from_url(url)

    # 传入正则表达式，找到存在 title 和 href 属性的 标签
    for each in bs.find_all(lambda x: 'href' in x.attrs):  # （3）使用 find_all 正则表达式 找到所有需要的标签值
        href = each.attrs['href']
        print(href)



