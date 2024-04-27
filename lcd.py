import Adafruit_SSD1306

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

disp = Adafruit_SSD1306.SSD1306_128_64(rst=None)
disp.begin()
disp.clear()
disp.display()

image = Image.new('1', (disp.width, disp.height))
font  = ImageFont.load_default()
draw  = ImageDraw.Draw(image)

barSpace  = 10
barHeight = 12
x=0
h=0
for a in range(3):
  h = x + barHeight
  draw.rectangle((x, 0, h, disp.height), outline=255, fill=255)
  x += barHeight + barSpace

# Display image
disp.image(image)
disp.display()