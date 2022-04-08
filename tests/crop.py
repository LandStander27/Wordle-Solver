from PIL import Image

img = Image.open("test.png")

img.crop((785, 204, 1118, 607)).show()

