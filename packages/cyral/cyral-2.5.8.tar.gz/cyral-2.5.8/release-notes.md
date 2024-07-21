---
# Release Notes

## 2.5.8
* Update dependencies.
## 2.5.7
* Update dependencies.
## 2.5.6
* (Bug fix) Add missing PyYAML dependency.
## 2.5.5
* (Bug fix) Fix the bug where attempting to set log level for a service may give error "service does not exist".
## 2.5.4
* (Bug fix) Remove dependency on awscli 1.x package and use awscli-plugin-proxy instead of
awscli-plugin-s3-proxy to avoid clobbering of awscli installation.
## 2.5.3
* (Bug fix) Fix possible unexpected exception in `access s3` command.
## 2.5.2
* (Bug fix) Fix bug in `access token` command for older (< v4.12) control planes.
## 2.5.1
* (Enhancement) Add --no-browser flag to disable automatic browser launch for authentication.
* (Enhancement) Add --auto-token-generation option.
## 2.5.0
* (Enhancement) Add access token management commands and token cache.
* (Refactor) Update access commands to use new token interactions.
## 2.4.0
* (Enhancement) Add `help` command for comprehensive command help.
* (Bug Fix) Disable option validity checking when `--help` is specified.
## 2.3.0
* (Enhancement) Allow users to choose account name for S3 access.
## 2.2.4
* (Chore) Update dependency versions.
## 2.2.3
* (Enhancement) Support new certificate download endpoint on Cyral Control Plane.
## 2.2.2
* (Bug Fix) Support `aws s3api` command.
## 2.2.1
* (Bug Fix) Make changes compatible with Python version 3.9.
## 2.2.0
* (Enhancement) Add `sidecar` command.
## 2.1.1
* (Enhancement) Add `--realm` option to support some older control planes.
## 2.0.1
* (Bug Fix) Choose non-proxy mode port for S3 repo.
## 2.0.0
* (Enhancement) Add support for Cyral Control Plane v4.x.
---
