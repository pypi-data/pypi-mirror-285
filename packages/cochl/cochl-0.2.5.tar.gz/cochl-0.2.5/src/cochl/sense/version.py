import requests
import warnings

from requests import RequestException

from . import __version__


def check_latest_lib_version(host: str):
    url = f"{host}/client-libraries/latest"
    params = {"current_version": __version__}

    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            latest_version = response.json().get("version")

            if __version__ != latest_version:
                warnings.warn(
                    f"Warning! The library version is outdated. "
                    f"Please upgrade the library: pip3 install cochl=={latest_version}",
                    stacklevel=3
                )
        else:
            pass
    except RequestException as _e:
        pass
