# pyReqCheck
Python library for checking if any modules are missing in your project's requirements.txt file


# Install
`pip install pyReqCheck`

# Run
`python -m pyReqCheck`

## Success
`::success:: All packages are used in requirements.txt`

## warning

`::warning:: Package in requirements.txt file not used in any modules: []`

## Failure
`::error:: One or more packages are imported but not found in requirements.txt: [comma seperated list of missing modules]`