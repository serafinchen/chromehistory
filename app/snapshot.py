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
            f"Couldn't make snapchot ({exc}). "
        ) from exc

    cache_src = profile_path / "Cache" / "Cache_Data"
    cache_dst = snapshot_path / "Cache" / "Cache_Data"

    if not cache_src.exists():
        raise FileNotFoundError(f"Cache-folder not found: {cache_src}")

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
            "[snapshot] Warning: critical cache data is missing "
        )
    elif skipped:
        print(f"[snapshot] {len(skipped)} locked cache data skipped: {skipped}")

    return snapshot_path