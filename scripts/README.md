# CF-Ares 脚本工具

本目录包含用于 CF-Ares 项目的各种实用脚本。

## 发布脚本

CF-Ares 提供了两种发布脚本，一个是 Bash 脚本 (`publish.sh`)，另一个是 Python 脚本 (`publish.py`)。两者功能类似，但 Python 脚本提供了更好的跨平台支持和更多的选项。

### Bash 脚本 (publish.sh)

`publish.sh` 是一个用于构建和发布 CF-Ares 包到 PyPI 的 Bash 脚本。

#### 功能

- 检查必要的工具是否安装（Python、build、twine）
- 运行测试以确保代码质量
- 清理旧的构建文件
- 构建包
- 发布到 PyPI 或 TestPyPI

#### 使用方法

```bash
# 基本用法 - 运行测试，构建并发布到 PyPI
./scripts/publish.sh

# 跳过测试
./scripts/publish.sh --skip-tests

# 发布到 TestPyPI 而不是 PyPI
./scripts/publish.sh --test

# 显示帮助信息
./scripts/publish.sh --help
```

#### 选项

- `--skip-tests`: 跳过测试步骤
- `--test`: 发布到 TestPyPI 而不是 PyPI
- `--help`: 显示帮助信息

### Python 脚本 (publish.py)

`publish.py` 是一个用于构建和发布 CF-Ares 包到 PyPI 的 Python 脚本，提供了更好的跨平台支持。

#### 功能

- 检查 Python 版本和必要的工具（build、twine）
- 运行测试以确保代码质量
- 清理旧的构建文件
- 构建包
- 发布到 PyPI 或 TestPyPI
- 提供更详细的错误信息和日志

#### 使用方法

```bash
# 基本用法 - 运行测试，构建并发布到 PyPI
python scripts/publish.py

# 跳过测试
python scripts/publish.py --skip-tests

# 发布到 TestPyPI 而不是 PyPI
python scripts/publish.py --test

# 不需要确认即可发布（适用于自动化流程）
python scripts/publish.py --no-confirm

# 组合选项
python scripts/publish.py --skip-tests --test --no-confirm
```

#### 选项

- `--skip-tests`: 跳过测试步骤
- `--test`: 发布到 TestPyPI 而不是 PyPI
- `--no-confirm`: 不需要确认即可发布（适用于自动化流程）

## 注意事项

1. 确保你已经在 PyPI 和 TestPyPI 上注册了账号
2. 配置你的 `~/.pypirc` 文件，包含你的凭据：

```
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = your_username
password = your_password

[testpypi]
repository = https://test.pypi.org/legacy/
username = your_username
password = your_password
```

或者使用 API 令牌：

```
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmc...

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-AgEIcHlwaS5vcmc...
```

3. 也可以使用环境变量设置凭据：

```bash
export TWINE_USERNAME=your_username
export TWINE_PASSWORD=your_password
```

4. 对于 API 令牌：

```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=your-token
```

## 故障排除

如果遇到问题，请检查：

1. Python 版本是否为 3.8 或更高
2. 是否安装了最新版本的 build 和 twine
3. 网络连接是否正常
4. PyPI 凭据是否正确 