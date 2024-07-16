from setuptools import setup, find_packages
import os
import sys

try:
    from torch.utils.cpp_extension import BuildExtension, CUDAExtension
    TORCH = True
except:
    TORCH = False
    
'''
any: 适用于任何平台的通用版本。
manylinux1_x86_64: 适用于符合ManyLinux规范的x86_64 Linux系统。
win_amd64: 适用于64位Windows系统。
macosx_10_9_x86_64: 适用于OS X 10.9及以上版本的x86_64 Mac系统
'''

VERSION = '0.1.2.19'

def make_cuda_ext(name, module, sources):
    # from torch.utils.cpp_extension import BuildExtension, CUDAExtension
    cuda_ext = CUDAExtension(
        name='%s.%s' % (module, name),
        sources=[os.path.join(*module.split('.'), src) for src in sources]
    )
    return cuda_ext



if sys.platform.startswith("linux") and TORCH==True:
    setup(
    name='wata',  # 包名
    version=VERSION,  # 版本
    description="wangtao tools",  # 包简介
    platforms=['Linux'],
    long_description=open('README.md').read(),  # 读取文件中介绍包的详细内容
    include_package_data=True,  # 是否允许上传资源文件
    author='wangtao',  # 作者
    author_email='1083719817@qq.com',  # 作者邮件
    maintainer='wangtao',  # 维护者
    maintainer_email='1083719817@qq.com',  # 维护者邮件
    license='MIT License',  # 协议
    url='',  # github或者自己的网站地址
    packages=find_packages(),  # 包的目录
    package_data={'': ['*.yaml', '*.txt', '*.bin', '*.pcd', '*.png', '*.ui']},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',  # 设置编写时的python版本
    ],
    options={
        'bdist_wheel': {
            'python_tag': 'py38',
            'plat_name': 'manylinux1_x86_64',
            'build_number': None,
            'dist_dir': None,
        }
    },
    python_requires='>=3.6',  # 设置python版本要求
    install_requires=['numpy', 'PyQt5', 'PyOpenGL', 'pyqtgraph', 'python-lzf',
                      'matplotlib', 'opencv-python', 'opencv-contrib-python','tqdm',
                      'pyyaml', 'vtk', 'scipy', 'tabulate', 'pyquaternion'],  # 安装所需要的库
    # entry_points={
    #     'console_scripts': [
    #         #'wata.lxq.yanhua=wata.console:fireworks',
    #     ],
    # },  # 设置命令行工具(可不使用就可以注释掉)
    
    cmdclass={
            'build_ext': BuildExtension,
        },
    ext_modules=[
        make_cuda_ext(
                name='roiaware_pool3d_cuda',
                module='wata.pointcloud.ops.roiaware_pool3d',
                sources=[
                        'src/roiaware_pool3d.cpp',
                        'src/roiaware_pool3d_kernel.cu',
                        ]
                    ),
        ]
)

else:
    setup(
        name='wata',  # 包名
        version=VERSION,  # 版本
        description="wangtao tools",  # 包简介
        platforms=['Windows', 'Linux'],
        long_description=open('README.md').read(),  # 读取文件中介绍包的详细内容
        include_package_data=True,  # 是否允许上传资源文件
        author='wangtao',  # 作者
        author_email='1083719817@qq.com',  # 作者邮件
        maintainer='wangtao',  # 维护者
        maintainer_email='1083719817@qq.com',  # 维护者邮件
        license='MIT License',  # 协议
        url='',  # github或者自己的网站地址
        packages=find_packages(),  # 包的目录
        package_data={'': ['*.yaml', '*.txt', '*.bin', '*.pcd', '*.png', '*.ui']},
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'Topic :: Software Development :: Build Tools',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3',  # 设置编写时的python版本
        ],
        options={
            'bdist_wheel': {
                'python_tag': 'py3',
                'plat_name': 'any',
                'build_number': None,
                'dist_dir': None,
            }
        },
        python_requires='>=3.6',  # 设置python版本要求
        install_requires=['numpy', 'PyQt5', 'PyOpenGL', 'pyqtgraph', 'python-lzf',
                        'matplotlib', 'opencv-python', 'opencv-contrib-python',
                        'pyyaml', 'vtk', 'scipy', 'tabulate', 'pyquaternion'],  # 安装所需要的库
        # entry_points={
        #     'console_scripts': [
        #         #'wata.lxq.yanhua=wata.console:fireworks',
        #     ],
        # },  # 设置命令行工具(可不使用就可以注释掉)
    )
