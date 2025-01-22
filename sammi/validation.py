import pathlib
import requests
from typing import List


class CDFValidator:
    """
    Python class to leverage the Science Physics Data Facility (SPDF)'s API for validation of International Solar-Terrestrial Physics (ISTP) guidelines.

    Parameters
    ----------
    api_url : `str`, optional
        The URL of the SPDF validation API. Default is "https://skteditor.heliophysics.net/cgi-bin/checkcdf.cgi".
    """

    def __init__(
        self,
        api_url: str = "https://skteditor.heliophysics.net/cgi-bin/checkcdf.cgi",
    ):
        self.api_url = api_url

    def validate(self, cdf_path: pathlib.Path) -> List[str]:
        """
        Function to validate a CDF file against the ISTP guidelines using the SPDF validation API.

        Parameters
        ----------
        cdf_path : `pathlib.Path`
            The path to the local CDF file to validate.

        Returns
        -------
        `List[str]`
            A list of error messages from the validation process.
        """
        try:
            raw_response = self.validate_raw(cdf_path)
            return self._parse_errors(raw_response)
        except Exception as e:
            return [f"Validation failed: {str(e)}"]

    def validate_raw(self, cdf_path: pathlib.Path) -> str:
        """
        Function to validate a CDF file against the ISTP guidelines using the SPDF validation API.

        Parameters
        ----------
        cdf_path : `pathlib.Path`
            The path to the local CDF file to validate.

        Returns
        -------
        `str`
            The raw response from the SPDF validation API.
        """
        try:
            with open(cdf_path, "rb") as cdf_to_upload:
                response = requests.post(
                    self.api_url, files={"file": (cdf_path.name, cdf_to_upload)}
                )
                response.raise_for_status()
                return response.content.decode("utf-8")
        except requests.RequestException as e:
            return f"API request failed: {str(e)}"

    def _parse_errors(self, raw_response: str) -> List[str]:
        """
        Parses the raw response from the SPDF validation API to extract error messages.

        Args:
            raw_response (str): The raw string response from the SPDF validation API.

        Returns:
            List[str]: A list of error messages extracted from the raw response.
        """
        errors = []
        current_section = None
        current_variable = None

        if raw_response.startswith("API request failed:"):
            return [raw_response]

        for line in raw_response.splitlines():
            if "Global errors:" in line:
                current_section = "Global errors"
                current_variable = None
            elif "The following variables are not ISTP-compliant" in line:
                current_section = "Variable"
                current_variable = None
            # Two tabs for each new variable name, 4 tabs for each error for that variable.
            elif (
                current_section == "Variable"
                and line.startswith("\t")
                and not line.startswith("\t\t")
            ):
                current_variable = line.strip()
            elif current_section and line.strip() and "Warning" not in line:
                if current_section == "Variable" and current_variable:
                    errors.append(f"{current_variable}:: {line.strip()}")
                else:
                    errors.append(f"{current_section}: {line.strip()}")
            elif current_section and not line.strip():
                current_section = None
                current_variable = None

        # Filter out any entries that are just section headers without actual errors
        errors = [error for error in errors if not error.endswith(":")]

        return errors
