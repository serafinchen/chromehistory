import pathlib

PROFILE_PATH = (
      pathlib.Path.home()
      / "AppData"
      / "Local"
      / "Google"
      / "Chrome"
      / "User Data"
      / "Default"
)

CACHE_PATHS = {
      "chrome": pathlib.Path.home() / "AppData/Local/Google/Chrome/User Data/Default/Cache/Cache_Data",
      "edge":   pathlib.Path.home() / "AppData/Local/Microsoft/Edge/User Data/Default/Cache/Cache_Data",
      "brave":  pathlib.Path.home() / "AppData/Local/BraveSoftware/Brave-Browser/User Data/Default/Cache/Cache_Data",
      "opera":  pathlib.Path.home() / "AppData/Roaming/Opera Software/Opera Stable/Cache/Cache_Data",
}
