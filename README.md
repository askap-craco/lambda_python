# lambda_python
Python utilities for LAMBDA project

# building the lambda_config tool so it can send raw ethernet frames
You need `sudo setcap cap_net_raw=ep` permissions

```
python setup.py build_exe
sudo setcap cap_net_raw=ep ./dist/lambda_config
```



# Development
## To add a  dependencies
see: https://chatgpt.com/share/6861d02c-48c0-800b-bd36-2ad36a6664d0
Using pip-tools to create requirements.txt
Add runtime dependences in setup.py/install_requires
requirements.in is simple.

To add developemnt dependencies: Add them to `dev-requirements.in`

Then do the following to update requirements.txt

```
pip-compile reuqirements.in generates a pinned requirements.txt
pip-compile dev-requirements.in generates pinned dev-requiremnets.txt
pip install -r requirements.txt
pip install -r dev-requirements.txt
```

Checkin all .in and .txt files into source control


## UPdate version number
in `pathfinder_testing/__init__.py`