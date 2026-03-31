import appdaemon.plugins.hass.hassapi as hass
import os
import re
import exifread

# Patterns that extract YYYYMMDD from common filename formats:
#   IMG-20260321-WA0001.jpg        -> 20260321
#   Screenshot_20250725_085509.jpg -> 20250725
FILENAME_DATE_PATTERNS = [
    re.compile(r'(?<!\d)(\d{4})-(\d{2})-(\d{2})(?!\d)'),  # YYYY-MM-DD
    re.compile(r'(?<!\d)(\d{4})(\d{2})(\d{2})(?!\d)'),     # YYYYMMDD
]

class RenamePhotos(hass.Hass):

    def initialize(self):
        self.log("RenamePhotos app started")
        self.run_once(self.run_rename, "00:05:00")
        self.run_daily(self.run_rename, "00:05:00")

    def run_rename(self, kwargs):
        directory = self.args.get("directory", "/media/wallpanel_photos")
        dry_run = self.args.get("dry_run", False)
        self.log(f"Starting rename run — directory={directory} dry_run={dry_run}")
        renamed, skipped, unknown = 0, 0, 0

        IMAGE_EXTS = {".jpg", ".jpeg", ".JPG", ".JPEG"}
        ALREADY_DATED = re.compile(r"^\d{8}_")
        ALREADY_UNKNOWN = re.compile(r"^unknown_\d+_")

        for root, dirs, files in os.walk(directory):
            dirs.sort()
            unk_counter = 1
            for fname in sorted(files):
                ext = os.path.splitext(fname)[1]
                if ext not in IMAGE_EXTS:
                    continue
                if ALREADY_DATED.match(fname) or ALREADY_UNKNOWN.match(fname):
                    skipped += 1
                    continue

                fpath = os.path.join(root, fname)

                # 1. Try EXIF DateTimeOriginal via exifread
                date_str = self._get_exif_date(fpath)

                # 2. Fall back to date embedded in filename
                if not date_str:
                    date_str = self._get_filename_date(fname)

                if date_str:
                    new_name = date_str + "_" + fname
                else:
                    new_name = f"unknown_{unk_counter:03d}_" + fname
                    unk_counter += 1
                    unknown += 1

                new_path = os.path.join(root, new_name)
                if os.path.exists(new_path):
                    base, e = os.path.splitext(new_name)
                    new_name = base + "_2" + e
                    new_path = os.path.join(root, new_name)

                if not dry_run:
                    os.rename(fpath, new_path)
                self.log(f"{'[DRY] ' if dry_run else ''}Renamed: {fname} -> {new_name}")
                renamed += 1

        self.log(f"Done — renamed={renamed} skipped={skipped} unknown={unknown}")

    def _get_exif_date(self, path):
        try:
            with open(path, "rb") as f:
                tags = exifread.process_file(f, stop_tag="EXIF DateTimeOriginal", details=False)
            tag = tags.get("EXIF DateTimeOriginal") or tags.get("Image DateTime")
            if tag:
                raw = str(tag)
                # Format: 2025:05:10 06:38:00
                if re.match(r"\d{4}:\d{2}:\d{2}", raw):
                    return raw[:4] + raw[5:7] + raw[8:10]
        except Exception as e:
            self.log(f"EXIF read error for {path}: {e}", level="WARNING")
        return None

    def _get_filename_date(self, fname):
        name = os.path.splitext(fname)[0]
        for pattern in FILENAME_DATE_PATTERNS:
            m = pattern.search(name)
            if m:
                try:
                    year  = int(m.group(1))
                    month = int(m.group(2))
                    day   = int(m.group(3))
                    if 2000 <= year <= 2099 and 1 <= month <= 12 and 1 <= day <= 31:
                        return f"{year:04d}{month:02d}{day:02d}"
                except (ValueError, IndexError):
                    continue
        return None
