from pathlib import Path
from colorsys import rgb_to_hsv

import fast_colorthief
from PIL import Image, UnidentifiedImageError
from tqdm import tqdm


class LogoPainting:
    def __init__(
        self, logo_path, canvas_width=1000, canvas_height=1000, single_logo_size=150
    ):
        self.path = Path(logo_path)
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.canvas = Image.new("RGBA", (canvas_width, canvas_height))
        self.single_logo_size = single_logo_size

    def get_dominant_color(self, image_path):
        # Get the dominant color in RGB
        dominant_color = fast_colorthief.get_dominant_color(image_path, quality=1)
        # Convert the dominant color to HSV
        dominant_color_hsv = rgb_to_hsv(*[ch / 255.0 for ch in dominant_color])
        return dominant_color_hsv

    def get_sorted_path_color_list(self):
        path_color = []
        for img_path in self.path.iterdir():
            try:
                path_color.append((img_path, self.get_dominant_color(img_path)))
            except UnidentifiedImageError:
                print(img_path, "is not a valid image file")
        path_color.sort(key=lambda x: x[1], reverse=True)
        return path_color

    def paint(self, num_uni=500):
        path_color = self.get_sorted_path_color_list()
        auxillary_canvas = [[0] * self.canvas_height for _ in range(self.canvas_width)]

        for image_path, _ in tqdm(path_color[:num_uni]):
            with Image.open(image_path) as image:
                image.thumbnail((self.single_logo_size, self.single_logo_size))
                image_width, image_height = image.size

                # Try to place the image at each position in the canvas
                for i in range(self.canvas_width - image_width + 1):
                    for j in range(self.canvas_height - image_height + 1):
                        # Check if the space is empty
                        if all(
                            auxillary_canvas[i + w][j + h] == 0
                            for w in range(image_width)
                            for h in range(image_height)
                        ):
                            # Place the image and mark the space as filled
                            self.canvas.paste(image, (i, j))
                            for w in range(image_width):
                                for h in range(image_height):
                                    auxillary_canvas[i + w][j + h] = 1
                            break
                    else:
                        continue
                    break
        return self.canvas.save(f"{num_uni}-logos.png")


if __name__ == "__main__":
    logo_painting = LogoPainting("./images/img_transparent")
    logo_painting.paint(1000)
