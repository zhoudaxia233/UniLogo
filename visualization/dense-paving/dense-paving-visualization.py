import math
from pathlib import Path
from colorsys import rgb_to_hsv

import fast_colorthief
from PIL import Image, UnidentifiedImageError
from tqdm import tqdm


class LogoPainting:
    def __init__(self, logo_path, num_logos=1000, single_logo_size=150):
        self.path = Path(logo_path)
        self.num_logos = num_logos
        self.single_logo_size = single_logo_size

        logos_per_dimension = math.ceil(math.sqrt(self.num_logos))

        self.canvas_width = logos_per_dimension * self.single_logo_size
        self.canvas_height = logos_per_dimension * self.single_logo_size
        self.canvas = Image.new("RGBA", (self.canvas_width, self.canvas_height))

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

    def paint(self):
        path_color = self.get_sorted_path_color_list()[: self.num_logos]
        auxillary_canvas = [[0] * self.canvas_height for _ in range(self.canvas_width)]

        next_pos = [0, 0]  # The next available position in the canvas
        max_y = 0  # Keep track of the maximum y-coordinate where a logo is placed

        for image_path, _ in tqdm(path_color):
            with Image.open(image_path) as image:
                image.thumbnail((self.single_logo_size, self.single_logo_size))
                image_width, image_height = image.size

                # Check if the image can be placed at the next available position
                while True:
                    if (
                        next_pos[0] + image_width <= self.canvas_width
                        and next_pos[1] + image_height <= self.canvas_height
                        and all(
                            auxillary_canvas[next_pos[0] + w][next_pos[1] + h] == 0
                            for w in range(image_width)
                            for h in range(image_height)
                        )
                    ):
                        # Place the image and mark the space as filled
                        self.canvas.paste(image, (next_pos[0], next_pos[1]))
                        for w in range(image_width):
                            for h in range(image_height):
                                auxillary_canvas[next_pos[0] + w][next_pos[1] + h] = 1

                        # Update the maximum y-coordinate
                        max_y = max(max_y, next_pos[1] + image_height)

                        # Update the next available position
                        next_pos[0] += self.single_logo_size
                        break
                    else:
                        # If the image doesn't fit here, try the next column in the same row
                        next_pos[0] += self.single_logo_size
                        if next_pos[0] >= self.canvas_width:
                            next_pos[0] = 0
                            next_pos[1] += self.single_logo_size

        # Crop the canvas to remove empty rows
        self.canvas = self.canvas.crop((0, 0, self.canvas_width, max_y))
        self.canvas.save(f"{self.num_logos}-logos.png")


if __name__ == "__main__":
    logo_painting = LogoPainting("./images/img_transparent")
    logo_painting.paint()
