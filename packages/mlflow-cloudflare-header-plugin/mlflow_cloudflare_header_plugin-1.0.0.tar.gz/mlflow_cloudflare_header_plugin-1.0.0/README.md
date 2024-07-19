## MLFlow Cloudflare Auth Request Header plugin

This package provides a custom MLflow plugin that allows users to pass extra headers when authenticating to a MLflow server that is protected by Cloudflare.


* `mlflow-cloudflare-header-plugin"`: uses `CloudflareRequestHeaderProvider` class that is used to specify the custom request headers `CF-Access-Client-Id` and `CF-Access-Client-Secret` required for a user to authenticate to the MLflow server when using the MLflow Python API.
* `pyproject.toml` file defines the entrypoint that tells MLflow to automatically register the custom request header provider to the registry when this package is installed.

### Usage

Install this package using pip and then use MLflow as normal.

```bash
pip install mlflow-cloudflare-header-plugin
```

The plugin expects Cloudflare ID and Secret to be defined as env variables
