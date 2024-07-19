from pathlib import Path
import os
import logging

log = logging.getLogger("epycs.config")

infer = ""

known_format = {
    "txt",
    "toml",
    "json",
    "ini",
    "yaml",
}
default_format = "txt"


def load_from(config_name, use_env=infer, use_dot_config=infer, file_format=infer):
    assert config_name, "must provide a config name"

    tried = []
    if use_env is not None:
        if use_env == infer:
            env_name = config_name.upper() + "_CONFIG"
        else:
            env_name = use_env

        if env_name in os.environ:
            tried.append(Path(os.environ[env_name]))

    if use_dot_config is not None:
        if use_dot_config == infer:
            dot_config_dir = Path.home() / ".config" / config_name
        else:
            dot_config_dir = Path.home() / ".config" / use_dot_config

        if file_format:
            ext = f".{file_format}"
            dot_path = (dot_config_dir / f"{config_name}").with_suffix(ext)
            tried.append(dot_path)
        elif file_format == infer:
            for fmt in known_format:
                ext = f".{fmt}"
                dot_path = (dot_config_dir / f"{config_name}").with_suffix(ext)
                tried.append(dot_path)

    for path in tried:
        if path.is_file():
            log.info(f"{path!r} found")
            fmt = ""
            if file_format is None:
                fmt = default_format
            elif file_format == infer:
                fmt = path.suffix[1:]
            else:
                fmt = file_format

            with open(path) as f:
                txt = f.read()

            return interpret_as(txt, fmt)

    return None


def interpret_as(txt, fmt):
    if fmt == "txt":
        return txt
    elif fmt == "toml":
        import toml

        return toml.loads(txt)
    elif fmt == "json":
        import json

        return json.loads(txt)
    elif fmt == "yaml":
        import yaml

        return yaml.safe_load(txt)
    elif fmt == "ini":
        import configparser

        cfg = configparser.ConfigParser()
        cfg.read_string(txt)
        return cfg
    else:
        raise Exception(f"unsupported config file format: {fmt}")
