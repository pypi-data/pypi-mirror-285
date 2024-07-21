"""Configure AWS profile to access S3 via Cyral sidecar"""

import configparser
import importlib.resources
import os
import subprocess  # nosec: B404
from pathlib import Path

from botocore.configloader import raw_config_parse
from botocore.exceptions import ConfigNotFound
from botocore.session import get_session

S3_PROXY_PLUGIN = "awscli-plugin-proxy"
S3_PROXY_PACKAGE = S3_PROXY_PLUGIN.replace("-", "_")


class AWSConfig:
    """AWSConfig class provides access to the AWS config file"""

    def __init__(self, config_file: str) -> None:
        self.config_file = config_file
        try:
            self.config = raw_config_parse(self.config_file)
        except ConfigNotFound:
            self.config = {}

    def get_profile(self, profile_name: str) -> dict:
        """Get the profile with the given name."""
        return self.config.get(f"profile {profile_name}", {})

    def set_profile(self, profile_name: str, profile: dict) -> None:
        """Set the profile with the given name."""
        self.config[f"profile {profile_name}"] = profile

    def get_section(self, section_name: str) -> dict:
        """Get the section with the given name."""
        return self.config.get(section_name, {})

    def set_section(self, section_name: str, section: dict) -> None:
        """Set the section with the given name."""
        self.config[section_name] = section

    def write(self) -> None:
        """Write the config to the file"""
        config_parser = configparser.ConfigParser(interpolation=None)
        for (section, kvs) in self.config.items():
            config_parser.add_section(section)
            for (key, value) in kvs.items():
                if isinstance(value, dict):
                    val = ""
                    for (sub_key, sub_value) in value.items():
                        val += f"\n{sub_key} = {sub_value}"
                else:
                    val = value
                config_parser.set(section, key, val)
        with open(self.config_file, "w", encoding="utf-8") as config_file:
            config_parser.write(config_file)


class AWSCredentials(AWSConfig):
    """AWSCredentials class provides access to the AWS credentials file"""

    def get_profile(self, profile_name: str) -> dict:
        """
        Get the profile with the given name. This overrides the base class
        method because the names of profile sections in the credentials file
        do not have the "profile" prefix.
        """
        return self.config.get(profile_name, {})

    def set_profile(self, profile_name: str, profile: dict) -> None:
        """
        Set the profile with the given name. This overrides the base class
        method because the names of profile sections in the credentials file
        do not have the "profile" prefix.
        """
        self.config[profile_name] = profile


def _get_config_file_path(file: str) -> str:
    # we use the botocore and awscli existing code to get this done.
    session = get_session()
    config_path = session.get_config_variable(file)
    config_path = os.path.expanduser(config_path)
    return config_path


def update_aws_creds(
    access_token: str,
    user_email: str,
    aws_profile_name: str,
    silent: bool,
    user_account: str,
) -> None:
    """Update AWS credentials based on the Cyral access token."""
    creds = AWSCredentials(_get_config_file_path("credentials_file"))
    profile = creds.get_profile(aws_profile_name)

    key_id = f"{user_email}:{access_token}"
    if user_account != "":
        key_id += f":{user_account}"
    values = {
        "aws_access_key_id": key_id,
        "aws_secret_access_key": "none",
    }
    profile.update(values)
    creds.set_profile(aws_profile_name, profile)
    creds.write()

    if not silent:
        print(f"Updated S3 token for AWS profile '{aws_profile_name}'")
        if aws_profile_name != "default":
            print(
                "\nTo use this profile, specify the profile name using "
                "--profile, as shown:\n\n"
                f"aws s3 ls --profile {aws_profile_name}\n"
            )


class S3ProxyPluginNotInstalled(Exception):
    """S3ProxyPluginNotInstalled exception is raised if the user does
    not have the S3 proxy plugin installed."""


def configure_s3_proxy_settings(
    aws_profile_name: str,
    sidecar_endpoint: str,
    ca_bundle: str,
) -> None:
    """Configure S3 proxy settings in the AWS profile."""
    if not _s3_plugin_is_installed():
        raise S3ProxyPluginNotInstalled(
            "Please first install S3 proxy plugin using the command:\n\n"
            + f"pip3 install {S3_PROXY_PLUGIN}"
        )
    conf = AWSConfig(_get_config_file_path("config_file"))
    try:
        _update_s3_proxy_plugins(conf)
        _update_ca_bundle(conf, aws_profile_name, ca_bundle)
        conf.write()
        update_s3_proxy_endpoint(aws_profile_name, sidecar_endpoint)
    except Exception as ex:
        # pylint: disable=broad-exception-raised
        raise Exception("error configuring S3 proxy settings") from ex


def _save_ca_bundle(ca_bundle: str, direname: str) -> str:
    ca_bundle_default_path = Path(direname) / "cyral_ca_bundle.pem"
    with open(ca_bundle_default_path, "w", encoding="utf-8") as file:
        file.write(ca_bundle)
    return str(ca_bundle_default_path)


def _update_ca_bundle(
    conf: AWSConfig,
    aws_profile_name: str,
    ca_bundle: str,
) -> None:
    config_path = _get_config_file_path("config_file")
    ca_bundle_direname = os.path.dirname(config_path)
    cyral_ca_bundle_file = _save_ca_bundle(ca_bundle, ca_bundle_direname)
    profile = conf.get_profile(aws_profile_name)
    profile.update({"ca_bundle": cyral_ca_bundle_file})
    conf.set_profile(aws_profile_name, profile)


def _update_s3_proxy_plugins(conf: AWSConfig) -> None:
    installed_plugin_name = S3_PROXY_PACKAGE
    plugins = conf.get_section("plugins")
    plugins.update({"s3-proxy": installed_plugin_name})
    if _get_cli_version() == "v2":
        plugins.update(
            {"cli_legacy_plugin_path": _get_cli_legacy_plugin_path()},
        )
    conf.set_section("plugins", plugins)


def update_s3_proxy_endpoint(aws_profile_name: str, endpoint: str) -> None:
    """update the S3 proxy endpoint"""
    endpoint = endpoint.replace("http://", "").replace("https://", "")
    conf = AWSConfig(_get_config_file_path("config_file"))

    profile = conf.get_profile(aws_profile_name)
    for command in ["s3", "s3api"]:
        value = profile.get(command, {})
        value.update({"proxy": f"http://{endpoint}"})
        profile.update({command: value})
    conf.write()


def s3_proxy_is_configured(aws_profile_name: str) -> bool:
    """Check if S3 proxy is setup in the specified AWS profile."""
    conf = AWSConfig(_get_config_file_path("config_file"))
    plugins = conf.get_section("plugins")
    profile = conf.get_profile(aws_profile_name)
    # a correctly configured config looks like the following:
    # {
    #     "plugins":{
    #         "s3-proxy":"awscli_plugin_s3_proxy"
    #     },
    #     "profiles":{
    #         "cyral":{
    #             "ca_bundle":"/home/user/.aws/cyral_ca_bundle.pem",
    #             "s3":{
    #                 "proxy":"http://sidecar.endpoint:453"
    #             },
    #             "s3api":{
    #                 "proxy":"http://sidecar.endpoint:453"
    #             }
    #         }
    #     }
    # }
    if (  # pylint: disable=too-many-boolean-expressions
        plugins.get("s3-proxy")
        and profile.get("ca_bundle")
        and Path(profile["ca_bundle"]).is_file()
        and profile.get("s3")
        and profile["s3"].get("proxy")
        and profile.get("s3api")
        and profile["s3api"].get("proxy")
        and _s3_plugin_is_installed()
    ):
        return True
    return False


def _get_cli_legacy_plugin_path() -> str:
    # should be the dir of the installed S3_PROXY_PLUGIN
    try:
        pkg = importlib.resources.files(S3_PROXY_PACKAGE)
        return os.path.dirname(str(pkg))
    except ModuleNotFoundError as ex:
        raise Exception(  # pylint: disable=broad-exception-raised
            "Failed to find a legacy plugin path for AWS cli.",
        ) from ex


def _s3_plugin_is_installed() -> bool:
    try:
        _ = importlib.resources.files(S3_PROXY_PACKAGE)
        return True
    except ModuleNotFoundError:
        return False


def _get_cli_version() -> str:
    # returns the major version
    try:
        cli_output = subprocess.check_output(  # nosec: B603 B607
            ["aws", "--version"],
        ).decode("utf-8")
        if not cli_output.startswith("aws-cli"):
            raise AssertionError(f"unrecognized AWS CLI version: {cli_output}")
        # example output: aws-cli/2.1.15 Python/3.7.3 ...
        aws_version = cli_output.split("/")[1]
        major_version = "v" + aws_version[0]
        return major_version
    except (subprocess.CalledProcessError, AssertionError) as ex:
        raise Exception(  # pylint: disable=broad-exception-raised
            "Failed to get AWS cli version. Make sure AWS CLI is installed!",
        ) from ex
