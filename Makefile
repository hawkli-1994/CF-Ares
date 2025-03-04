.PHONY: setup setup-dev clean lint test build publish docs

# 默认目标
all: lint test build

# 安装基本依赖
setup:
	pip install -e .

# 安装开发依赖
setup-dev: setup
	pip install -e ".[dev]"

# 清理构建文件
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# 代码格式化和静态检查
format:
	isort cf_ares tests
	black cf_ares tests

# 代码质量检查
lint:
	flake8 cf_ares tests
	isort --check cf_ares tests
	black --check cf_ares tests
	mypy cf_ares

# 运行测试
test:
	pytest tests/

# 运行测试并生成覆盖率报告
test-cov:
	pytest --cov=cf_ares tests/ --cov-report=term --cov-report=html

# 构建包
build: clean
	python -m build

# 发布到 PyPI
publish: build
	twine upload dist/*

# 生成文档
docs:
	cd docs && make html

# 安装开发版本
dev-install: clean
	pip install -e .

# 帮助信息
help:
	@echo "可用命令:"
	@echo "  make setup      - 安装基本依赖"
	@echo "  make setup-dev  - 安装开发依赖"
	@echo "  make clean      - 清理构建文件"
	@echo "  make format     - 格式化代码"
	@echo "  make lint       - 代码质量检查"
	@echo "  make test       - 运行测试"
	@echo "  make test-cov   - 运行测试并生成覆盖率报告"
	@echo "  make build      - 构建包"
	@echo "  make publish    - 发布到 PyPI"
	@echo "  make docs       - 生成文档"
	@echo "  make dev-install - 安装开发版本" 