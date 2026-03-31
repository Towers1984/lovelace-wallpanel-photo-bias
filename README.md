> **Fork Notice:** This is a fork of [j-a-n/lovelace-wallpanel](https://github.com/j-a-n/lovelace-wallpanel)
> with the addition of a **recency bias** feature for photo selection.
> For general WallPanel support, issues, and documentation please refer to the original repository.
> Fork-specific changes are documented in the [Recency Bias](#recency-bias-fork-addition) section below.

# WallPanel

[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/j-a-n/lovelace-wallpanel?style=for-the-badge)](https://github.com/j-a-n/lovelace-wallpanel/releases)
[![GitHub stars](https://img.shields.io/github/stars/j-a-n/lovelace-wallpanel?color=yellow&style=for-the-badge)](https://github.com/j-a-n/lovelace-wallpanel/stargazers)
![GitHub All Releases](https://img.shields.io/github/downloads/j-a-n/lovelace-wallpanel/total.svg?color=green&style=for-the-badge)
[![Documentation](https://img.shields.io/badge/view-Documentation-blue?style=for-the-badge)](https://j-a-n.github.io/lovelace-wallpanel/ "Go to WallPanel documentation")


🖼️ **Wall panel mode for your Home Assistant Dashboards.**  

WallPanel is a configurable extension that features:

- Photo and video slideshow screensaver
- Show dashboard views, cards and badges of your choice on top of the images.
- Full-screen mode
- Hide the side and or top bar 
- Screen wake lock
- Motion detection

You can use images and videos from the following sources:

- Home Assistant Media-source
- Immich
- Home Assitant entities with entity_picture attribute
- Full websites as iframe
- Unsplash

![Screenshot of screensaver](./docs/screensaver-screenshot.png)

## Installation

* Search for `WallPanel` in the Home Assistant Community Store
* Click on the repository
* Click the `Download` button
* You can now select a special version if required
* Click on `Download`

## Quick Start
After [Installation](#installation) you can enable wallpanel for a dashboard.
To do this, add a wallpanel configuration to your Home Assistant dashboard configuration yaml (raw config).

* Navigate to the dashboard.
* Click Overview in your sidebar.
* Click the three dots menu (top-right) and click on Edit Dashboard.
* Click the three dots menu again and click on Raw configuration editor.
* Add the `wallpanel` configuration above anything else.

```yaml
wallpanel:
  enabled: true
  hide_toolbar: false
  hide_sidebar: true
  fullscreen: false
  idle_time: 10
```

After saving and closing the dashboard configuration, WallPanel should now be active for this dashboard.
The sidebar should be hidden and the screensaver should start after an idle time of 10 seconds.

## Documentation
Further information can be found in the [WallPanel Documentation](https://j-a-n.github.io/lovelace-wallpanel/).

## Credits
Thanks to Unsplash and to all the photographers for sharing their great photos!
Many thanks to Openstreetmap for providing the excellent Nominatim search engine!
Thanks to Jacob Seidelin for exif-js!

This project is inspired by:
- https://github.com/tcarlsen/lovelace-screensaver
- https://gist.github.com/ciotlosm/1f09b330aa5bd5ea87b59f33609cc931
- https://github.com/richtr/NoSleep.js
- https://github.com/madeInLagny/mil-no-sleep

## Reviews / Tutorials
- [SmartHomeScene - WallPanel: Home Assistant Screensaver for your wall-mounted control panel](https://smarthomescene.com/guides/wallpanel-home-assistant-screensaver-for-your-wall-mounted-control-panel)
- [Smart Home Pursuites - Install Fully-Kiosk + Wallpanel in Home Assistant for Fire Tablets](https://smarthomepursuits.com/fire-tablet-fully-kiosk-screensaver-home-assistant/)

## Videos
- [YouTube: Next Level Tablet Dashboard 🌅 mit lovelace-wallpanel 🤩 (🇩🇪)](https://www.youtube.com/watch?v=_KTyYIznzMY)
- [YouTube: So wird dein Home Assistant Wallpanel zum Kunstobjekt! (🇩🇪)](https://youtu.be/ohBRmoOTKW0?si=S1Yl_Mmj7jXKLPpC)

## Recency Bias (Fork Addition)

This fork adds a **recency bias** feature to the screensaver media selection. When enabled, a configurable percentage of screensaver slots are filled from photos taken within a recent time window, with the remainder drawn from older photos. This ensures your most recent memories appear more frequently without completely excluding older ones.

### Configuration Options

Add these options to your `wallpanel:` dashboard configuration:

| Option | Default | Description |
|---|---|---|
| `recent_media_days` | `0` | Number of days that defines "recent". Set to `0` to disable the feature entirely. |
| `recent_media_percent` | `70` | Percentage of screensaver slots to fill from recent photos. The remainder (100 minus this value) is filled from older photos. |

**Example:**

```yaml
wallpanel:
  enabled: true
  image_url: media-source://media_source/local/photos
  media_order: random
  media_list_max_size: 500

  # Show recent photos more frequently
  recent_media_days: 30       # Photos from the last 30 days are "recent"
  recent_media_percent: 70    # 70% of slots from recent, 30% from older
```

### How Dates Are Determined

The feature determines a photo's date using the following priority order:

1. **Immich `fileCreatedAt`** — when using an Immich API source, dates are read directly from the API response. No extra setup required.

2. **`YYYYMMDD_` filename prefix** — when using local media-source, the date is parsed from the start of the filename, e.g. `20260321_photo.jpg`. Files without this prefix are treated as "older" (they are never excluded, just less frequently shown).

3. **No date available** — items without any detectable date are placed in the "older" bucket and still shown regularly.

### Preparing Local Media Files

For local media-source users, photos need to have a `YYYYMMDD_` date prefix in their filename for the recency logic to work. This repository includes an **AppDaemon app** (`rename_photos_appdaemon.py`) that automates this.

The script:
- Reads the EXIF `DateTimeOriginal` tag from each JPEG using the `exifread` library
- Falls back to a date embedded in the filename (e.g. WhatsApp's `IMG-20260321-WA0001.jpg` format)
- Renames files to `YYYYMMDD_originalname.jpg`
- Files where no date can be determined are prefixed `unknown_###_` — these still display normally, just without recency weighting
- Already-renamed files are skipped on subsequent runs, making nightly re-runs safe

**Setup:**

1. Install the AppDaemon add-on in Home Assistant
2. Add `exifread` to AppDaemon's python packages in its add-on configuration
3. Copy `rename_photos_appdaemon.py` to `/addon_configs/a0d7b954_appdaemon/apps/rename_photos.py`
4. Add the following to `/addon_configs/a0d7b954_appdaemon/apps/apps.yaml`:

```yaml
rename_photos:
  module: rename_photos
  class: RenamePhotos
  directory: /media/wallpanel_photos   # path to your photos
  dry_run: false                        # set true to preview without renaming
```

The script runs automatically at 00:05 every night, picking up any newly added photos.

### Behaviour Notes

- If the recent photo pool is **smaller than the target slot count**, photos repeat (wrap-around sampling) — this is intentional and means you always get the exact ratio requested
- If **either bucket is empty** (all photos are recent, or none are), the feature logs a warning and returns the full list unchanged
- The bias is applied **before** `media_order` sorting and `media_list_max_size` trimming, so the ratio is preserved correctly regardless of list size
- To verify the feature is working, enable `debug: true` and check your browser console — you will see a log line such as:
  ```
  recency bias: 350 recent (last 30d, pool=45) + 150 older (pool=980) = 500 total
  ```

