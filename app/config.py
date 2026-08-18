import pathlib

PROFILE_PATH = pathlib.Path(r"C:\Users\seraf\AppData\Local\Google\Chrome\User Data\Default")

CACHE_PATHS = {
      "chrome": pathlib.Path.home() / "AppData/Local/Google/Chrome/User Data/Default",
      "edge":   pathlib.Path.home() / "AppData/Local/Microsoft/Edge/User Data/Default/Cache/Cache_Data",
      "brave":  pathlib.Path.home() / "AppData/Local/BraveSoftware/Brave-Browser/User Data/Default/Cache/Cache_Data",
      "opera":  pathlib.Path.home() / "AppData/Roaming/Opera Software/Opera Stable/Cache/Cache_Data",
}
