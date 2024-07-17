from __future__ import annotations

from pathlib import Path

from digitalhub_core.utils.generic_utils import (
    decode_string,
    extract_archive,
    get_bucket_and_key,
    get_s3_source,
    requests_chunk_download,
)
from digitalhub_core.utils.git_utils import clone_repository
from digitalhub_core.utils.logger import LOGGER
from digitalhub_runtime_dbt.utils.env import (
    POSTGRES_DATABASE,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_SCHEMA,
    POSTGRES_USER,
)

####################
# Templates
####################

PROJECT_TEMPLATE = """
name: "{}"
version: "1.0.0"
config-version: 2
profile: "postgres"
model-paths: ["{}"]
models:
""".lstrip(
    "\n"
)

MODEL_TEMPLATE_VERSION = """
models:
  - name: {}
    latest_version: {}
    versions:
        - v: {}
          config:
            materialized: table
""".lstrip(
    "\n"
)

PROFILE_TEMPLATE = f"""
postgres:
    outputs:
        dev:
            type: postgres
            host: {POSTGRES_HOST}
            user: {POSTGRES_USER}
            pass: {POSTGRES_PASSWORD}
            port: {POSTGRES_PORT}
            dbname: {POSTGRES_DATABASE}
            schema: {POSTGRES_SCHEMA}
    target: dev
""".lstrip(
    "\n"
)


def generate_dbt_profile_yml(root: Path) -> None:
    """
    Create dbt profiles.yml

    Returns
    -------
    None
    """
    profiles_path = root / "profiles.yml"
    profiles_path.write_text(PROFILE_TEMPLATE)


def generate_dbt_project_yml(root: Path, model_dir: Path, project: str) -> None:
    """
    Create dbt_project.yml from 'dbt'

    Parameters
    ----------
    project : str
        The project name.

    Returns
    -------
    None
    """
    project_path = root / "dbt_project.yml"
    project_path.write_text(PROJECT_TEMPLATE.format(project, model_dir.name))


def generate_outputs_conf(model_dir: Path, sql: str, output: str, uuid: str) -> None:
    """
    Write sql code for the model and write schema
    and version detail for outputs versioning

    Parameters
    ----------
    sql : str
        The sql code.
    output : str
        The output table name.
    uuid : str
        The uuid of the model for outputs versioning.

    Returns
    -------
    None
    """
    sql_path = model_dir / f"{output}.sql"
    sql_path.write_text(sql)

    output_path = model_dir / f"{output}.yml"
    output_path.write_text(MODEL_TEMPLATE_VERSION.format(output, uuid, uuid))


def generate_inputs_conf(model_dir: Path, name: str, uuid: str) -> None:
    """
    Generate inputs confs dependencies for dbt project.

    Parameters
    ----------
    project : str
        The project name.
    inputs : list
        The list of inputs dataitems names.

    Returns
    -------
    None
    """
    # write schema and version detail for inputs versioning
    input_path = model_dir / f"{name}.yml"
    input_path.write_text(MODEL_TEMPLATE_VERSION.format(name, uuid, uuid))

    # write also sql select for the schema
    sql_path = model_dir / f"{name}_v{uuid}.sql"
    sql_path.write_text(f'SELECT * FROM "{name}_v{uuid}"')


def get_output_table_name(outputs: list[dict]) -> str:
    """
    Get output table name from run spec.

    Parameters
    ----------
    outputs : list
        The outputs.

    Returns
    -------
    str
        The output dataitem/table name.

    Raises
    ------
    RuntimeError
        If outputs are not a list of one dataitem.
    """
    try:
        return outputs["output_table"]
    except IndexError as e:
        msg = f"Outputs must be a list of one dataitem. Exception: {e.__class__}. Error: {e.args}"
        LOGGER.exception(msg)
        raise RuntimeError(msg) from e
    except KeyError as e:
        msg = f"Must pass reference to 'output_table'. Exception: {e.__class__}. Error: {e.args}"
        LOGGER.exception(msg)
        raise RuntimeError(msg) from e


def save_function_source(path: Path, source_spec: dict) -> str:
    """
    Save function source.

    Parameters
    ----------
    path : Path
        Path where to save the function source.
    source_spec : dict
        Function source spec.

    Returns
    -------
    path
        Function code.
    """
    # Get relevant information
    code = source_spec.get("code")
    base64 = source_spec.get("base64")
    source = source_spec.get("source")
    handler = source_spec.get("handler")

    if code is not None:
        return code

    if base64 is not None:
        return decode_base64(base64)

    scheme = source.split("://")[0]

    # Http(s) or s3 presigned urls
    if scheme in ["http", "https"]:
        filename = path / "archive.zip"
        get_remote_source(source, filename)
        unzip(path, filename)
        return (path / handler).read_text()

    # Git repo
    if scheme == "git+https":
        path = path / "repository"
        get_repository(path, source)
        return (path / handler).read_text()

    # S3 path
    if scheme == "zip+s3":
        filename = path / "archive.zip"
        bucket, key = get_bucket_and_key(source)
        get_s3_source(bucket, key, filename)
        unzip(path, filename)
        return (path / handler).read_text()

    # Unsupported scheme
    raise RuntimeError(f"Unsupported scheme: {scheme}")


def get_remote_source(source: str, filename: Path) -> None:
    """
    Get remote source.

    Parameters
    ----------
    source : str
        HTTP(S) or S3 presigned URL.
    filename : Path
        Path where to save the function source.

    Returns
    -------
    str
        Function code.
    """
    try:
        requests_chunk_download(source, filename)
    except Exception as e:
        msg = f"Some error occurred while downloading function source. Exception: {e.__class__}. Error: {e.args}"
        LOGGER.exception(msg)
        raise RuntimeError(msg) from e


def unzip(path: Path, filename: Path) -> None:
    """
    Extract an archive.

    Parameters
    ----------
    path : Path
        Path where to extract the archive.
    filename : Path
        Path to the archive.

    Returns
    -------
    None
    """

    try:
        extract_archive(path, filename)
    except Exception as e:
        msg = f"Source must be a valid zipfile. Exception: {e.__class__}. Error: {e.args}"
        LOGGER.exception(msg)
        raise RuntimeError(msg) from e


def get_repository(path: Path, source: str) -> str:
    """
    Get repository.

    Parameters
    ----------
    path : Path
        Path where to save the function source.
    source : str
        Git repository URL in format git://<url>.

    Returns
    -------
    None
    """
    try:
        clone_repository(path, source)
    except Exception as e:
        msg = f"Some error occurred while downloading function repo source. Exception: {e.__class__}. Error: {e.args}"
        LOGGER.exception(msg)
        raise RuntimeError(msg) from e


def decode_base64(base64: str) -> str:
    """
    Decode base64 encoded code.

    Parameters
    ----------
    base64 : str
        The encoded code.

    Returns
    -------
    str
        The decoded code.

    Raises
    ------
    RuntimeError
        Error while decoding code.
    """
    try:
        return decode_string(base64)
    except Exception as e:
        msg = f"Some error occurred while decoding function source. Exception: {e.__class__}. Error: {e.args}"
        LOGGER.exception(msg)
        raise RuntimeError(msg) from e
