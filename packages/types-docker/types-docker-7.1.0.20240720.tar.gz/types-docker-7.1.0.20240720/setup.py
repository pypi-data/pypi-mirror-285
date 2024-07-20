from setuptools import setup

name = "types-docker"
description = "Typing stubs for docker"
long_description = '''
## Typing stubs for docker

This is a [PEP 561](https://peps.python.org/pep-0561/)
type stub package for the [`docker`](https://github.com/docker/docker-py) package.
It can be used by type-checking tools like
[mypy](https://github.com/python/mypy/),
[pyright](https://github.com/microsoft/pyright),
[pytype](https://github.com/google/pytype/),
PyCharm, etc. to check code that uses
`docker`.

This version of `types-docker` aims to provide accurate annotations
for `docker==7.1.*`.
The source for this package can be found at
https://github.com/python/typeshed/tree/main/stubs/docker. All fixes for
types and metadata should be contributed there.

See https://github.com/python/typeshed/blob/main/README.md for more details.
This package was generated from typeshed commit
[`389b318691354fbaaea319967a2174699265644c`](https://github.com/python/typeshed/commit/389b318691354fbaaea319967a2174699265644c) and was tested
with mypy 1.10.1, pyright 1.1.372, and
pytype 2024.4.11.
'''.lstrip()

setup(name=name,
      version="7.1.0.20240720",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      project_urls={
          "GitHub": "https://github.com/python/typeshed",
          "Changes": "https://github.com/typeshed-internal/stub_uploader/blob/main/data/changelogs/docker.md",
          "Issue tracker": "https://github.com/python/typeshed/issues",
          "Chat": "https://gitter.im/python/typing",
      },
      install_requires=['types-requests', 'urllib3>=2'],
      packages=['docker-stubs'],
      package_data={'docker-stubs': ['__init__.pyi', '_types.pyi', 'api/__init__.pyi', 'api/build.pyi', 'api/client.pyi', 'api/config.pyi', 'api/container.pyi', 'api/daemon.pyi', 'api/exec_api.pyi', 'api/image.pyi', 'api/network.pyi', 'api/plugin.pyi', 'api/secret.pyi', 'api/service.pyi', 'api/swarm.pyi', 'api/volume.pyi', 'auth.pyi', 'client.pyi', 'constants.pyi', 'context/__init__.pyi', 'context/api.pyi', 'context/config.pyi', 'context/context.pyi', 'credentials/__init__.pyi', 'credentials/constants.pyi', 'credentials/errors.pyi', 'credentials/store.pyi', 'credentials/utils.pyi', 'errors.pyi', 'models/__init__.pyi', 'models/configs.pyi', 'models/containers.pyi', 'models/images.pyi', 'models/networks.pyi', 'models/nodes.pyi', 'models/plugins.pyi', 'models/resource.pyi', 'models/secrets.pyi', 'models/services.pyi', 'models/swarm.pyi', 'models/volumes.pyi', 'tls.pyi', 'transport/__init__.pyi', 'transport/basehttpadapter.pyi', 'transport/npipeconn.pyi', 'transport/npipesocket.pyi', 'transport/sshconn.pyi', 'transport/unixconn.pyi', 'types/__init__.pyi', 'types/base.pyi', 'types/containers.pyi', 'types/daemon.pyi', 'types/healthcheck.pyi', 'types/networks.pyi', 'types/services.pyi', 'types/swarm.pyi', 'utils/__init__.pyi', 'utils/build.pyi', 'utils/config.pyi', 'utils/decorators.pyi', 'utils/fnmatch.pyi', 'utils/json_stream.pyi', 'utils/ports.pyi', 'utils/proxy.pyi', 'utils/socket.pyi', 'utils/utils.pyi', 'version.pyi', 'METADATA.toml', 'py.typed']},
      license="Apache-2.0 license",
      python_requires=">=3.8",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Programming Language :: Python :: 3",
          "Typing :: Stubs Only",
      ]
)
