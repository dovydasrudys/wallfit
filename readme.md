# WallFit

WallFit is a Python tool designed to help you seamlessly resize and adapt wallpapers to fit your multi-monitor setup. Whether you have different monitor resolutions, aspect ratios, or specific gaps between your monitors, WallFit ensures that your wallpaper looks perfect on every screen.

## Features

- **Simple Resizing:** Easily resize your wallpapers to specified resolutions.
- **Aspect Ratio Handling:** Maintain the desired aspect ratio, with options to choose which part of the image to crop.
- **Monitor Gaps:** Account for estimated pixel gaps between monitors, providing a smooth transition between screens (only if multiple resolutions are provided).
- **Customization:** Choose which side of the picture should be preserved or add black bars to avoid cropping.

## How to Use

1. **Installation:**
    - [Installation steps go here.]

2. **Basic Resizing:**
    ```python
    from wallfit import multi_monitor_resize

    multi_monitor_resize('input.jpg', resolutions=[(1920, 1080)], output_path='output.jpg')
    ```

3. **Aspect Ratio Handling:**
    ```python
    from wallfit import multi_monitor_resize

    multi_monitor_resize('input.jpg', resolutions=[(3840, 2160)], prefer_center=True, output_path='output.jpg')
    ```

4. **Monitor Gaps:**
    ```python
    from wallfit import multi_monitor_resize

    multi_monitor_resize('input.jpg', resolutions=[(1920, 1080), (1920, 1080)], gaps=[20], output_path='output.jpg')
    ```

5. **Customization:**
    ```python
    from wallfit import multi_monitor_resize

    multi_monitor_resize('input.jpg', resolutions=[(3840, 2160)], prefer_left=True, output_path='output.jpg')
    ```

## Installation

[Detailed installation steps go here.]

## Contribution

Feel free to contribute to WallFit by opening issues or submitting pull requests. Your feedback and improvements are highly appreciated.

## License

This project is licensed under the [MIT License](LICENSE).
