import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from utils import *

# ========= 配置 =========
ROOT_DIR = Path(r"C:\Users\syw\Downloads\spire-codex\extraction\raw\animations")   # 文件夹A
MD5_RECORD_FILE = Path(__file__).resolve().parent / "spine_md5.json"

# =======================


def file_md5(path: Path) -> str:
    m = hashlib.md5()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            m.update(chunk)
    return m.hexdigest()


def normalize_relpath(path: Path) -> str:
    return path.as_posix()


def relpath_without_ext(path: Path) -> str:
    return path.with_suffix("").as_posix()


def png_wiki_filename_from_relpath(relpath: str) -> str:
    return relpath.replace("/", "_")


def load_md5_record(record_file: Path) -> dict:
    if not record_file.exists():
        return {}
    with record_file.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        return {}
    return data


def save_md5_record(record_file: Path, data: dict):
    tmp = record_file.with_suffix(record_file.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)
    tmp.replace(record_file)


def read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def upload_text_page(site, title: str, text: str, summary: str):
    page = site.pages[title]
    page.save(text, summary=summary)


def convert_skel_to_json(skel_path: Path) -> Path:
    converter = Path(__file__).resolve().parent / "SpineSkeletonDataConverter.exe"
    if not converter.exists():
        raise FileNotFoundError(f"找不到转换器: {converter}")

    temp_dir = Path(tempfile.mkdtemp(prefix="spine_skel_"))
    json_path = temp_dir / (skel_path.stem + ".json")

    result = subprocess.run(
        [str(converter), str(skel_path), str(json_path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(converter.parent),
    )
    if result.returncode != 0:
        raise RuntimeError(
            "skel 转 json 失败\n"
            f"命令: {converter} {skel_path} {json_path}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )

    if not json_path.exists():
        raise RuntimeError(f"转换器返回成功，但未生成 json: {json_path}")

    return json_path


def rewrite_atlas_first_page_name(atlas_text: str, new_png_name: str) -> str:
    lines = atlas_text.splitlines()
    for i, line in enumerate(lines):
        if line.strip():
            lines[i] = new_png_name
            break
    return "\n".join(lines) + ("\n" if atlas_text.endswith("\n") else "")


def get_first_nonempty_line(text: str) -> str:
    for line in text.splitlines():
        s = line.strip()
        if s:
            return s
    return ""


def process_png(site, root_dir: Path, path: Path, md5_record: dict):
    rel = normalize_relpath(path.relative_to(root_dir))
    md5 = file_md5(path)

    old_md5 = md5_record.get(rel)
    if old_md5 == md5:
        return False

    wiki_filename = png_wiki_filename_from_relpath(rel)
    # print(f"[PNG ] 上传: {rel} -> File:{wiki_filename}")

    site.upload(str(path), wiki_filename, '[[分类:Spine资源]]', True)
    md5_record[rel] = md5
    return True


def process_atlas(site, root_dir: Path, path: Path, md5_record: dict):
    rel = normalize_relpath(path.relative_to(root_dir))
    md5 = file_md5(path)

    old_md5 = md5_record.get(rel)
    if old_md5 == md5:
        return False

    atlas_text = read_text_file(path)
    first_page_name = get_first_nonempty_line(atlas_text)
    if not first_page_name:
        raise RuntimeError(f"atlas 首个非空行为空: {path}")

    png_local_path = path.parent / first_page_name
    if not png_local_path.exists():
        raise FileNotFoundError(
            f"atlas 引用的 png 不存在: {png_local_path}\n"
            f"atlas 文件: {path}\n"
            f"atlas 第一行: {first_page_name}"
        )

    png_rel = normalize_relpath(png_local_path.relative_to(root_dir))
    png_wiki_filename = png_wiki_filename_from_relpath(png_rel)

    new_atlas_text = rewrite_atlas_first_page_name(atlas_text, png_wiki_filename)
    page_title = f"Data:Spine/{relpath_without_ext(path.relative_to(root_dir))}/atlas"

    # print(f"[ATLAS] 上传: {rel} -> {page_title}")
    # print(f"        第一行: {first_page_name} -> {png_wiki_filename}")

    upload_text_page(site, page_title, new_atlas_text, "更新 Spine atlas")
    md5_record[rel] = md5
    return True


def process_skel(site, root_dir: Path, path: Path, md5_record: dict):
    rel = normalize_relpath(path.relative_to(root_dir))
    md5 = file_md5(path)

    old_md5 = md5_record.get(rel)
    if old_md5 == md5:
        return False

    json_path = None
    try:
        json_path = convert_skel_to_json(path)
        json_text = read_text_file(json_path)
        page_title = f"Data:Spine/{relpath_without_ext(path.relative_to(root_dir))}/json"

        # print(f"[SKEL] 上传: {rel} -> {page_title}")
        upload_text_page(site, page_title, json_text, "更新 Spine json")

        md5_record[rel] = md5
        return True
    finally:
        if json_path is not None and json_path.exists():
            try:
                json_path.unlink()
            except Exception:
                pass
            try:
                json_path.parent.rmdir()
            except Exception:
                pass


def split_text_by_utf8_bytes(text: str, max_bytes: int) -> list[str]:
    parts = []
    buf = []
    buf_bytes = 0

    for ch in text:
        ch_bytes = len(ch.encode("utf-8"))
        if buf and buf_bytes + ch_bytes > max_bytes:
            parts.append("".join(buf))
            buf = [ch]
            buf_bytes = ch_bytes
        else:
            buf.append(ch)
            buf_bytes += ch_bytes

    if buf:
        parts.append("".join(buf))

    return parts


def iter_target_files(root_dir: Path):
    exts = {".atlas", ".png", ".skel"}
    for path in root_dir.rglob("*"):
        if not path.is_file():
            continue
        if path == MD5_RECORD_FILE:
            continue
        if path.suffix.lower() in exts:
            yield path


def filter_changed_files(files, root_dir: Path, md5_record: dict):
    changed_files = []
    for path in files:
        rel = normalize_relpath(path.relative_to(root_dir))
        md5 = file_md5(path)

        if md5_record.get(rel) != md5:
            changed_files.append(path)

    return changed_files


def main():
    if not ROOT_DIR.exists():
        raise FileNotFoundError(f"ROOT_DIR 不存在: {ROOT_DIR}")

    md5_record = load_md5_record(MD5_RECORD_FILE)

    changed = 0
    failed = 0

    files = sorted(
        iter_target_files(ROOT_DIR),
        key=lambda p: normalize_relpath(p.relative_to(ROOT_DIR))
    )

    # 先过滤
    changed_files = filter_changed_files(files, ROOT_DIR, md5_record)

    print(f"共 {len(files)} 个文件，其中 {len(changed_files)} 个需要处理")

    # tqdm 只跑变更文件
    for path in tqdm(changed_files):
        try:
            suffix = path.suffix.lower()
            if suffix == ".png":
                if process_png(site, ROOT_DIR, path, md5_record):
                    changed += 1
                    save_md5_record(MD5_RECORD_FILE, md5_record)
            elif suffix == ".atlas":
                if process_atlas(site, ROOT_DIR, path, md5_record):
                    changed += 1
                    save_md5_record(MD5_RECORD_FILE, md5_record)
            elif suffix == ".skel":
                if process_skel(site, ROOT_DIR, path, md5_record):
                    changed += 1
                    save_md5_record(MD5_RECORD_FILE, md5_record)
        except Exception as e:
            failed += 1
            rel = normalize_relpath(path.relative_to(ROOT_DIR))
            print(f"[失败] {rel}")
            print(e)

    print(f"完成。成功更新 {changed} 个文件，失败 {failed} 个。")


if __name__ == "__main__":
    main()