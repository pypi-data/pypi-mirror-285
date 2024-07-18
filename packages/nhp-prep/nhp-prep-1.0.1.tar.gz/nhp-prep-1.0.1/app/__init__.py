"""Top-level package for RP To-Do."""

__app_name__ = "nhp-prep"
__version__ = "1.0.1"

(
    SUCCESS,
    DIR_ERROR,
    FILE_ERROR,
    JSON_ERROR,
    ID_ERROR,
    YAML_ERROR,
) = range(6)

ERRORS = {
    DIR_ERROR: "Configuration directory error",
    FILE_ERROR: "Configuration file error",
    ID_ERROR: "ID error",
}
