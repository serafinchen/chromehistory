import pathlib
import shutil


def create_snapshot(profile_path: pathlib.Path, snapshot_path: pathlib.Path) -> pathlib.Path:
    profile_path = pathlib.Path(profile_path)
    snapshot_path = pathlib.Path(snapshot_path)
    snapshot_path.mkdir(parents=True, exist_ok=True)

    history_src = profile_path / "History"
    history_dst = snapshot_path / "History"
    try:
        shutil.copy2(history_src, history_dst)
    except OSError as exc:
        raise RuntimeError(
            f"Konnte History-Datenbank nicht kopieren ({exc}). "
            "Ist Chrome geschlossen?"
        ) from exc

    cache_src = profile_path / "Cache" / "Cache_Data"
    cache_dst = snapshot_path / "Cache" / "Cache_Data"

    if not cache_src.exists():
        raise FileNotFoundError(f"Cache-Ordner nicht gefunden: {cache_src}")

    if cache_dst.exists():
        shutil.rmtree(cache_dst)
    cache_dst.mkdir(parents=True, exist_ok=True)

    skipped = []
    for item in cache_src.iterdir():
        if not item.is_file():
            continue
        try:
            shutil.copy2(item, cache_dst / item.name)
        except OSError:
            skipped.append(item.name)

    critical = ["index"] + [f"data_{i}" for i in range(4)]
    missing_critical = [c for c in critical if c in skipped]
    if missing_critical:
        print(
            f"[snapshot] WARNUNG: kritische Cache-Datei(en) gesperrt: "
            f"{missing_critical}. Bitte Chrome schließen und Snapshot neu erstellen."
        )
    elif skipped:
        print(f"[snapshot] {len(skipped)} gesperrte Cache-Datei(en) übersprungen: {skipped}")

    return snapshot_path