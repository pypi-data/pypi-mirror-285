# Example Package

This is a simple example package. You can use
[Github-flavored Markdown](https://guides.github.com/features/mastering-markdown/)
to write your content.

## 安装构建工具

`python -m pip install --upgrade build`

## build

`python -m build`

## 安装上传工具

`pip install --upgrade twine`

## 上传

`python -m twine upload --repository testpypi dist/*`
`python -m twine upload --repository pypi dist/*`

## 安装开发版

`pip install --editable .`
