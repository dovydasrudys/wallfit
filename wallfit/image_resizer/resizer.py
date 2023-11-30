import io
import requests
from pathlib import Path
from PIL import Image


def multi_monitor_resize(fp: str | bytes | Path | Image.Image, resolutions, gaps=None, black_bars=False, prefer_center=False, prefer_left=False, prefer_right=False, prefer_top=False, prefer_bottom=False, output_path=None):
    # Check if fp is a url
    if isinstance(fp, str) and fp.startswith("http"):
        response = requests.get(fp)
        image_bytes = io.BytesIO(response.content)
        fp = image_bytes
    
    if gaps is None:
        gaps = []

    # there should be less gaps than resolutions
    if len(gaps) >= len(resolutions):
        raise ValueError("There should be less gaps than resolutions")
    
    # Only one of the prefer flags should be set
    flags_set = sum([1 if p else 0 for p in [black_bars, prefer_center, prefer_left, prefer_right, prefer_top, prefer_bottom]])
    if flags_set > 1:
        raise ValueError("Only one of the prefer flags should be set")
    elif flags_set == 0:
        prefer_center = True
    
    monitors_wdith = sum([r[0] for r in resolutions])
    width_with_gaps = monitors_wdith + sum(gaps)
    target_height = min([r[1] for r in resolutions])

    # Load image
    if isinstance(fp, Image.Image):
        image = fp
    else:
        image = Image.open(fp)
    
    target_aspect_ratio = width_with_gaps / target_height

    image = match_aspect_ratio(
        image=image,
        target_aspect_ratio=target_aspect_ratio,
        black_bars=black_bars,
        prefer_center=prefer_center,
        prefer_left=prefer_left,
        prefer_right=prefer_right,
        prefer_top=prefer_top,
        prefer_bottom=prefer_bottom
    )

    # Now that the image has the correct aspect ratio, resize it to match both dimensions
    image = image.resize((width_with_gaps, target_height))

    # Cut out the gaps
    if len(gaps) > 0:
        image_parts = []
        current_x = 0
        for i, resolution in enumerate(resolutions):
            gap_after = gaps[i] if i < len(gaps) else 0
            image_parts.append(image.crop((current_x, 0, current_x + resolution[0], resolution[1])))
            current_x += resolution[0] + gap_after
        
        # Paste the image parts together
        image = Image.new("RGB", (monitors_wdith, target_height))
        current_x = 0
        for image_part in image_parts:
            image.paste(image_part, (current_x, 0))
            current_x += image_part.size[0]
        
    if output_path:
        image.save(output_path)

    return image


def match_aspect_ratio(image, target_aspect_ratio, black_bars=False, prefer_center=True, prefer_left=False, prefer_right=False, prefer_top=False, prefer_bottom=False):
    # Only one of the modes can be selected
    if sum([1 if p else 0 for p in [black_bars, prefer_center, prefer_left, prefer_right, prefer_top, prefer_bottom]]) != 1:
        raise ValueError("Only one of the prefer flags should be set")

    width, height = image.size
    center_x = width / 2
    center_y = height / 2
    # First get current and target aspect ratios
    current_aspect_ratio = width / height

    if current_aspect_ratio > target_aspect_ratio:
        # Current image is wider than target so we want to cut off one or both of the sides or add black bars to the top and bottom
        if any([prefer_top, prefer_bottom]):
            raise ValueError("Can't prefer top or bottom when image is wider than target")
        
        if black_bars:
            new_height = width / target_aspect_ratio
            height_diff = new_height - height
            y0, y1 = -height_diff / 2, height + height_diff / 2
            x0, x1 = 0, width
        else:
            new_width = height * target_aspect_ratio
            y0, y1 = 0, height
            if prefer_left:
                x0, x1 = 0, new_width
            elif prefer_right:
                x0, x1 = width - new_width, width
            else:
                x0, x1 = center_x - (new_width / 2), center_x + (new_width / 2)
    else:
        # Current image is taller than target so we want to cut off the top and/or bottom or add black bars to the left and right
        if any([prefer_left, prefer_right]):
            raise ValueError("Can't prefer left or right when image is taller than target")

        if black_bars:
            new_width = height * target_aspect_ratio
            width_diff = new_width - width
            x0, x1 = -width_diff / 2, width + width_diff / 2
            y0, y1 = 0, height
        else:
            new_height = width / target_aspect_ratio
            x0, x1 = 0, width
            if prefer_top:
                y0, y1 = 0, new_height
            elif prefer_bottom:
                y0, y1 = height - new_height, height
            else:
                y0, y1 = center_y - (new_height / 2), center_y + (new_height / 2)

    image = image.crop((x0, y0, x1, y1))
    return image

    