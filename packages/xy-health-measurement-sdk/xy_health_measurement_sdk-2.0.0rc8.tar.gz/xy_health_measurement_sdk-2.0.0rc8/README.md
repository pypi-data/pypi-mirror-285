# 小阳心健康测量SDK

[使用手册](https://measurement.xymind.cn/docs/sdk/python.html)

## Conda
```bash
conda create --name measurement_client_sdk -y python=3.10
conda activate measurement_client_sdk
pip install --trusted-host 10.0.0.1 -i http://10.0.0.1:8081/repository/xy-pypi/simple build toml twine
pip install --trusted-host 10.0.0.1 -i http://10.0.0.1:8081/repository/xy-pypi/simple -r <(python -c "import toml; print('\n'.join(toml.load('pyproject.toml')['project']['dependencies']))")
```

## publish
```bash
# clear
sudo rm -rf dist *.egg-info
# build
python -m build
# publish
python -m twine upload dist/*

# build docker image
docker build --build-arg ACCELERATE_CONFIG='--trusted-host 10.0.0.1 -i http://10.0.0.1:8081/repository/xy-pypi/simple' -t xiaoyangtech/measurement-python-client-sdk:2.1 .
```