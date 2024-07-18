# VPDB
> Python debug configuration generator for vscode

## Install

```shell script
pip install vpdbz
```

## Command Line Tools

### vpdbz
VSCode debug configuration generator from a python command line.

It can automatically generate the debug configuration file for vscode by just adding `vpdbz` in front of your python command.
It will parse the environment variables and the arguments list correctly.

For example:
```shell
vpdbz CUDA_VISIBLE_DEVICES=1,2 python train.py --batch-size 16 --lr 1e-4
```

It will generate the debug configuration in `.vscode/launch.json`. 
Then you can debug your python file by clicking the corresponding button.

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: python train.py --batch-size 16 --lr 1e-4",
            "type": "python",
            "request": "launch",
            "program": "train.py",
            "env": {
                "CUDA_VISIBLE_DEVICES": "1,2"
            },
            "console": "integratedTerminal",
            "args": [
                "--batch-size",
                "16",
                "--lr",
                "1e-4"
            ],
            "cwd": "/home/xxx/demo_project",
            "justMyCode": false,
            "variablePresentation": {
                "all": "hide",
                "protected": "inline"
        }
        }
    ]
}
```
![](imgs/vpdb_demo.png)

> Attention: The vpdbz command must be excuted in the root folder of the vscode project.

## TODO

- [ ] Support run file in different directories. 

## Update Log
### 2024.07.17
1. Auto install dependencies for vpdbz.
2. Handle the environment variables.
3. hide special variables and function variables.
4. debug all python files.

## Build

```shell
# 准备环境确保你已经安装了 setuptools 和 wheel，这些工具帮助你打包和分发Python包。
pip install setuptools wheel
# 创建分发包在包含 setup.py 的目录下，运行以下命令来生成分发包：这将生成两个目录：dist 和 build。dist 目录包含生成的分发包文件（例如 .tar.gz 和 .whl 文件）。
python setup.py sdist bdist_wheel

# 发布到 PyPI
pip install twine
twine upload dist/*

```