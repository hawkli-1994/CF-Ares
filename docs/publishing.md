# 发布 CF-Ares 到 PyPI

本文档提供了将 CF-Ares 发布到 PyPI 的详细步骤。

## 准备工作

1. 确保你有 PyPI 账号。如果没有，请在 [PyPI](https://pypi.org/account/register/) 注册。

2. 安装必要的工具：

```bash
pip install build twine
```

3. 确保你的 `~/.pypirc` 文件配置正确（可选）：

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

## 构建包

1. 清理旧的构建文件：

```bash
make clean
```

2. 构建包：

```bash
make build
```

或者直接使用：

```bash
python -m build
```

这将在 `dist/` 目录下创建源代码分发包（`.tar.gz`）和轮子（`.whl`）。

## 测试发布

强烈建议先发布到 TestPyPI 进行测试：

```bash
twine upload --repository testpypi dist/*
```

然后测试安装：

```bash
pip install --index-url https://test.pypi.org/simple/ cf-ares
```

## 正式发布

确认测试无误后，发布到正式 PyPI：

```bash
twine upload dist/*
```

或者使用 Makefile：

```bash
make publish
```

## 版本更新

1. 更新 `cf_ares/version.py` 中的版本号。
2. 更新 `CHANGELOG.md`（如果有）。
3. 提交更改并打上版本标签：

```bash
git add cf_ares/version.py CHANGELOG.md
git commit -m "Bump version to X.Y.Z"
git tag vX.Y.Z
git push origin main --tags
```

4. 构建并发布新版本。

## 故障排除

- 如果上传失败，检查你的凭证是否正确。
- 确保版本号是唯一的，PyPI 不允许重复的版本号。
- 如果包名被占用，考虑使用不同的名称。

## 其他资源

- [Python Packaging User Guide](https://packaging.python.org/)
- [Packaging Python Projects](https://packaging.python.org/tutorials/packaging-projects/)
- [TestPyPI](https://test.pypi.org/)
- [PyPI](https://pypi.org/) 