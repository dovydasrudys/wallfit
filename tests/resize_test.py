from PIL import Image
from ..image_resizer.resizer import multi_monitor_resize

def create_test_image() -> Image:
    """
    Creates a test image that consists of three equal blocks of color.
    Image consists of two equal rows. The top row has the three blocks of color (Red, Green, Blue) next to each other.
    The bottom row is all white.
    Visual representation:

    6000px wide, 2000px high
    ________________________
    |       |       |       |
    |   R   |   G   |   B   |
    |_______|_______|_______|
    |                       |
    |         White         |
    |_______________________|

    """
    images = []
    images.append(Image.new("RGB", (2000, 1000), (255, 0, 0)))
    images.append(Image.new("RGB", (2000, 1000), (0, 255, 0)))
    images.append(Image.new("RGB", (2000, 1000), (0, 0, 255)))
    image = Image.new("RGB", (6000, 2000))
    for i, img in enumerate(images):
        image.paste(img, (i * 2000, 0))
    
    bottom_image = Image.new("RGB", (6000, 1000), (255, 255, 255))
    image.paste(bottom_image, (0, 1000))
    
    return image


def test_simple_resize():
    image = create_test_image()
    image = multi_monitor_resize(fp=image, resolutions=[(1920, 1080)])
    assert image.size == (1920, 1080)


def test_resize_center_to_smaller_aspect():
    old_image = create_test_image()
    image = multi_monitor_resize(fp=old_image, resolutions=[(1920, 1080)], prefer_center=True)
    assert image.size == (1920, 1080)
    
    old_aspect_ratio = old_image.size[0] / old_image.size[1]
    new_aspect_ratio = image.size[0] / image.size[1]
    assert new_aspect_ratio < old_aspect_ratio

    # old image had wider aspect ratio which means that the new image
    # should have less red and blue on the sides left (because of cropping)
    # all of original height should be visible using that we can calculate how much of the original width should be visible
    original_width_visible = new_aspect_ratio * old_image.size[1]
    # the difference between the original width and the visible width is the amount of pixels that should be cropped
    cropped_pixels = old_image.size[0] - original_width_visible
    # the cropped pixels should be divided by two because they are cropped from both sides
    side_cropped_pixels = cropped_pixels / 2
    # the amount of red and blue pixels that should be visible is 2000 - the amount of pixels that should be cropped
    visible_red_blue_pixels = 2000 - side_cropped_pixels
    # the amount of green pixels that should be visible is 2000 that is the same as the original image
    visible_green_pixels = 2000
    # however the image got smaller by some multiplier and we need to take that into account when checking the amount of pixels
    # that should be visible
    size_multiplier = old_image.size[1] / 1080
    visible_green_pixels = round(visible_green_pixels / size_multiplier)
    visible_red_blue_pixels = round(visible_red_blue_pixels / size_multiplier)

    first_red_pixel = 0
    last_red_pixel = visible_red_blue_pixels - 2 # -2 instead of -1 because -1 would collide with the first green pixel and be mixed up
    first_green_pixel = visible_red_blue_pixels + 1
    last_green_pixel = visible_red_blue_pixels + visible_green_pixels - 2
    first_blue_pixel = visible_red_blue_pixels + visible_green_pixels + 1
    last_blue_pixel = visible_red_blue_pixels + visible_green_pixels + visible_red_blue_pixels - 2

    # now we can check if the amount of pixels that are visible is correct
    assert image.getpixel((first_red_pixel, 0)) == (255, 0, 0)
    assert image.getpixel((last_red_pixel, 0)) == (255, 0, 0)
    assert image.getpixel((first_green_pixel, 0)) == (0, 255, 0)
    assert image.getpixel((last_green_pixel, 0)) == (0, 255, 0)
    assert image.getpixel((first_blue_pixel, 0)) == (0, 0, 255)
    assert image.getpixel((last_blue_pixel, 0)) == (0, 0, 255)


def test_resize_center_to_larger_aspect():
    old_image = create_test_image()
    image = multi_monitor_resize(fp=old_image, resolutions=[(3840, 1080)], prefer_center=True)
    assert image.size == (3840, 1080)
    
    old_aspect_ratio = old_image.size[0] / old_image.size[1]
    new_aspect_ratio = image.size[0] / image.size[1]
    assert new_aspect_ratio > old_aspect_ratio

    # new image has wider aspect ratio which means that the new image should have all of the original width
    # so we can check if the amounts of red, green and blue pixels are equal on the first row
    red_pixels = sum([1 for x in range(image.size[0]) if image.getpixel((x, 0)) == (255, 0, 0)])
    green_pixels = sum([1 for x in range(image.size[0]) if image.getpixel((x, 0)) == (0, 255, 0)])
    blue_pixels = sum([1 for x in range(image.size[0]) if image.getpixel((x, 0)) == (0, 0, 255)])
    mixing_tolerance = 4 # the amount of pixels that we tolerate to be mixed up because of colour transitions
    assert (3840 / 3) - red_pixels <= mixing_tolerance
    assert (3840 / 3) - green_pixels <= mixing_tolerance
    assert (3840 / 3) - blue_pixels <= mixing_tolerance
    
    # as we're using prefer_center=True the image should be cropped from top and bottom equally
    red_pixels = sum([1 for x in range(image.size[1]) if image.getpixel((0, x)) == (255, 0, 0)])
    white_pixels = sum([1 for x in range(image.size[1]) if image.getpixel((0, x)) == (255, 255, 255)])
    assert red_pixels == white_pixels


def test_resize_top_to_larger_aspect():
    old_image = create_test_image()
    image = multi_monitor_resize(fp=old_image, resolutions=[(3840, 1080)], prefer_top=True)
    assert image.size == (3840, 1080)
    
    old_aspect_ratio = old_image.size[0] / old_image.size[1]
    new_aspect_ratio = image.size[0] / image.size[1]
    assert new_aspect_ratio > old_aspect_ratio

    # new image has wider aspect ratio which means that the new image should have all of the original width
    # so we can check if the amounts of red, green and blue pixels are equal on the first row
    red_pixels = sum([1 for x in range(image.size[0]) if image.getpixel((x, 0)) == (255, 0, 0)])
    green_pixels = sum([1 for x in range(image.size[0]) if image.getpixel((x, 0)) == (0, 255, 0)])
    blue_pixels = sum([1 for x in range(image.size[0]) if image.getpixel((x, 0)) == (0, 0, 255)])
    mixing_tolerance = 4 # the amount of pixels that we tolerate to be mixed up because of colour transitions
    assert abs((3840 / 3) - red_pixels) <= mixing_tolerance
    assert abs((3840 / 3) - green_pixels) <= mixing_tolerance
    assert abs((3840 / 3) - blue_pixels) <= mixing_tolerance
    
    # as we're using prefer_top=True the image should be cropped from the bottom so there should be more red pixels than white in the first column
    red_pixels = sum([1 for x in range(image.size[1]) if image.getpixel((0, x)) == (255, 0, 0)])
    white_pixels = sum([1 for x in range(image.size[1]) if image.getpixel((0, x)) == (255, 255, 255)])
    

    original_height_visible = old_image.size[0] / new_aspect_ratio
    cropped_pixels = old_image.size[1] - original_height_visible
    remaining_pixels = old_image.size[1] - cropped_pixels
    size_multiplier = old_image.size[0] / 3840
    remaining_white_pixels = remaining_pixels - 1000

    assert abs(1000 / size_multiplier) - red_pixels <= mixing_tolerance
    assert abs(remaining_white_pixels / size_multiplier) - white_pixels <= mixing_tolerance


def test_resize_bottom_to_larger_aspect():
    old_image = create_test_image()
    image = multi_monitor_resize(fp=old_image, resolutions=[(3840, 1080)], prefer_bottom=True)
    assert image.size == (3840, 1080)
    
    old_aspect_ratio = old_image.size[0] / old_image.size[1]
    new_aspect_ratio = image.size[0] / image.size[1]
    assert new_aspect_ratio > old_aspect_ratio

    # new image has wider aspect ratio which means that the new image should have all of the original width
    # so we can check if the amounts of red, green and blue pixels are equal on the first row
    red_pixels = sum([1 for x in range(image.size[0]) if image.getpixel((x, 0)) == (255, 0, 0)])
    green_pixels = sum([1 for x in range(image.size[0]) if image.getpixel((x, 0)) == (0, 255, 0)])
    blue_pixels = sum([1 for x in range(image.size[0]) if image.getpixel((x, 0)) == (0, 0, 255)])
    mixing_tolerance = 4 # the amount of pixels that we tolerate to be mixed up because of colour transitions
    assert abs((3840 / 3) - red_pixels) <= mixing_tolerance
    assert abs((3840 / 3) - green_pixels) <= mixing_tolerance
    assert abs((3840 / 3) - blue_pixels) <= mixing_tolerance
    
    # as we're using prefer_bottom=True the image should be cropped from the top so there should be more white pixels than red in the first column
    red_pixels = sum([1 for x in range(image.size[1]) if image.getpixel((0, x)) == (255, 0, 0)])
    white_pixels = sum([1 for x in range(image.size[1]) if image.getpixel((0, x)) == (255, 255, 255)])
    

    original_height_visible = old_image.size[0] / new_aspect_ratio
    cropped_pixels = old_image.size[1] - original_height_visible
    remaining_pixels = old_image.size[1] - cropped_pixels
    size_multiplier = old_image.size[0] / 3840
    remaining_red_pixels = remaining_pixels - 1000

    assert abs(1000 / size_multiplier) - white_pixels <= mixing_tolerance
    assert abs(remaining_red_pixels / size_multiplier) - red_pixels <= mixing_tolerance


def test_resize_left_to_smaller_aspect():
    old_image = create_test_image()
    image = multi_monitor_resize(fp=old_image, resolutions=[(2560, 1080)], prefer_left=True)
    assert image.size == (2560, 1080)
    
    old_aspect_ratio = old_image.size[0] / old_image.size[1]
    new_aspect_ratio = image.size[0] / image.size[1]
    assert new_aspect_ratio < old_aspect_ratio

    # old image had wider aspect ratio which means that the new image
    # should have less blue on the right side (because of cropping)
    # all of original height should be visible using that we can calculate how much of the original width should be visible
    original_width_visible = new_aspect_ratio * old_image.size[1]
    # the difference between the original width and the visible width is the amount of pixels that should be cropped
    cropped_pixels = old_image.size[0] - original_width_visible
    assert cropped_pixels < 2000 # only part of the blue should be cropped

    red_pixels = sum([1 for x in range(image.size[0]) if image.getpixel((x, 0)) == (255, 0, 0)])
    green_pixels = sum([1 for x in range(image.size[0]) if image.getpixel((x, 0)) == (0, 255, 0)])
    blue_pixels = sum([1 for x in range(image.size[0]) if image.getpixel((x, 0)) == (0, 0, 255)])

    mixing_tolerance = 4 # the amount of pixels that we tolerate to be mixed up because of colour transitions
    size_multiplier = old_image.size[1] / 1080
    # red and green should be visible in full
    assert abs(2000 / size_multiplier) - red_pixels <= mixing_tolerance
    assert abs(2000 / size_multiplier) - green_pixels <= mixing_tolerance
    # blue should be visible in part
    assert abs((2000 - cropped_pixels) / size_multiplier) - blue_pixels <= mixing_tolerance


def test_resize_right_to_smaller_aspect():
    old_image = create_test_image()
    image = multi_monitor_resize(fp=old_image, resolutions=[(2560, 1080)], prefer_right=True)
    assert image.size == (2560, 1080)
    
    old_aspect_ratio = old_image.size[0] / old_image.size[1]
    new_aspect_ratio = image.size[0] / image.size[1]
    assert new_aspect_ratio < old_aspect_ratio

    # old image had wider aspect ratio which means that the new image
    # should have less red on the left side (because of cropping)
    # all of original height should be visible using that we can calculate how much of the original width should be visible
    original_width_visible = new_aspect_ratio * old_image.size[1]
    # the difference between the original width and the visible width is the amount of pixels that should be cropped
    cropped_pixels = old_image.size[0] - original_width_visible
    assert cropped_pixels < 2000 # only part of the red should be cropped

    red_pixels = sum([1 for x in range(image.size[0]) if image.getpixel((x, 0)) == (255, 0, 0)])
    green_pixels = sum([1 for x in range(image.size[0]) if image.getpixel((x, 0)) == (0, 255, 0)])
    blue_pixels = sum([1 for x in range(image.size[0]) if image.getpixel((x, 0)) == (0, 0, 255)])

    mixing_tolerance = 4 # the amount of pixels that we tolerate to be mixed up because of colour transitions
    size_multiplier = old_image.size[1] / 1080
    # green and blue should be visible in full
    assert abs(2000 / size_multiplier) - green_pixels <= mixing_tolerance
    assert abs(2000 / size_multiplier) - blue_pixels <= mixing_tolerance
    # red should be visible in part
    assert abs((2000 - cropped_pixels) / size_multiplier) - red_pixels <= mixing_tolerance


def test_resize_black_bars_to_smaller_aspect():
    old_image = create_test_image()
    image = multi_monitor_resize(fp=old_image, resolutions=[(2560, 1080)], black_bars=True)
    assert image.size == (2560, 1080)
    
    old_aspect_ratio = old_image.size[0] / old_image.size[1]
    new_aspect_ratio = image.size[0] / image.size[1]
    assert new_aspect_ratio < old_aspect_ratio

    # old image had wider aspect ratio which means that the new image should have black bars on the top and bottom
    sizing_factor = image.size[0] / old_image.size[0]
    resized_height = old_image.size[1] * sizing_factor
    missing_height = image.size[1] - resized_height # the amount of pixels that should be black bars
    black_pixels = sum([1 for y in range(image.size[1]) if image.getpixel((0, y)) == (0, 0, 0)])
    mixing_tolerance = 4 # the amount of pixels that we tolerate to be mixed up because of colour transitions
    assert abs(missing_height - black_pixels) <= mixing_tolerance


def test_resize_black_bars_to_larger_aspect():
    old_image = create_test_image()
    image = multi_monitor_resize(fp=old_image, resolutions=[(3840, 1080)], black_bars=True)
    assert image.size == (3840, 1080)
    
    old_aspect_ratio = old_image.size[0] / old_image.size[1]
    new_aspect_ratio = image.size[0] / image.size[1]
    assert new_aspect_ratio > old_aspect_ratio

    # new image has wider aspect ratio which means that the new image should have black bars on the left and right
    sizing_factor = image.size[1] / old_image.size[1]
    resized_width = old_image.size[0] * sizing_factor
    missing_width = image.size[0] - resized_width # the amount of pixels that should be black bars
    black_pixels = sum([1 for x in range(image.size[0]) if image.getpixel((x, 0)) == (0, 0, 0)])
    mixing_tolerance = 4 # the amount of pixels that we tolerate to be mixed up because of colour transitions
    assert abs(missing_width - black_pixels) <= mixing_tolerance


def test_gaps():
    old_image = create_test_image()
    image = multi_monitor_resize(fp=old_image, resolutions=[
        (3000, 2000),
        (3000, 2000)
    ], gaps=[200])

    red_pixels = sum([1 for x in range(image.size[0]) if image.getpixel((x, 0)) == (255, 0, 0)])
    green_pixels = sum([1 for x in range(image.size[0]) if image.getpixel((x, 0)) == (0, 255, 0)])
    blue_pixels = sum([1 for x in range(image.size[0]) if image.getpixel((x, 0)) == (0, 0, 255)])

    sizing_factor = 6200 / old_image.size[0]
    expected_red = 2000 * sizing_factor
    expected_green = 2000 * sizing_factor - 200
    expected_blue = 2000 * sizing_factor
    mixing_tolerance = 4 # the amount of pixels that we tolerate to be mixed up because of colour transitions
    assert abs(expected_red - red_pixels) <= mixing_tolerance
    assert abs(expected_green - green_pixels) <= mixing_tolerance
    assert abs(expected_blue - blue_pixels) <= mixing_tolerance


def test_url():
    url = "https://i.redd.it/can-someone-covert-this-wallpaper-to-5120x1440p-plz-v0-0797jqzt56vb1.jpg?s=42606379c8e35aac42d46e401bc0b0802d17477a"
    image = multi_monitor_resize(fp=url, resolutions=[(5120, 1440)], prefer_top=True)
    image.show()