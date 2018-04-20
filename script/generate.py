from PIL import Image, ImageDraw, ImageFont
from random import randint, choice
import json


def getConfig ():
	with open('config.json', 'r') as f:
		config = json.load(f)
		return config

# The image size can be determined in two ways
# 1) standard width and height
# 2) a ratio and a width / height (the missing property is extrapolated with the help of the ratio)
# This method gets the size config object and interprets it in order to generate a (width, height) touple (int values)
def getSize (size_obj):
	
	if 'ratio' in size_obj:

		ratio = size_obj['ratio']
		
		if 'width' in size_obj:
			width  = getDimension(size_obj['width'])
			height = int(width / ratio)
		elif 'height' in size_obj:
			height = getDimension(size_obj['height'])
			width  = int(height * ratio)

	else:

		width  = getDimension(size_obj['width'])
		height = getDimension(size_obj['height'])

	return (width, height)


# A dimension (used for sizes) can be declared in three ways
# 1) a basic integer
# 2) an array of integers, from which one value will be randomly returned (a string with two integers separated by "-", ex: "10-100")
# 3) an interval of integers, from which one value will be randomly generated
# This method determines the appropriate case based on the config value and returns an integer value
def getDimension (dimension):

	is_array = (type(dimension) == type([]))
	is_range = (type(dimension) == type('a') and '-' in dimension)
	if is_array:
		return choice(dimension)
	elif is_range:
		range_parts = dimension.split('-')
		range_start = int(range_parts[0])
		range_end   = int(range_parts[1])
		return randint(range_start, range_end)
	else:
		return dimension


# A background color can be declared in three ways
# 1) a basic hex color string, ex. "#FFFFFF"
# 2) the string "random", which will trigger a specific case, automatically generating a hex color string
# 3) an array of hex color strings
# Returns a hex color string, ex. "#FFFFFF"
def getColor (color):

	is_array = (type(color) == type([]))
	if is_array:
		return choice(color)
	elif color == 'random':
		return '#{:06x}'.format(randint(0, 256**3))
	else:
		return color


# In adition to the standard cases covered by the getColor method
# a text color has an extra case, triggered by the use of the string "invert"
# Just like the name sugests, it will return a hex color string 
# corresponding to the inverted value of the given background_color param (also sent as a hex color string)
def getTextColor (color, background_color):

	if color == 'invert':
		return invertHexColor(background_color)
	else:
		return getColor(color)


def invertHexColor (hex_color):
	#strips the "#"
	color_to_convert = hex_color[1:]
	table = str.maketrans('0123456789abcdef', 'fedcba9876543210')
	return '#'+ color_to_convert.lower().translate(table).upper()


# Simple helper method that replaces the "magic" strings "##index", "##width" and "##height"
# with the corresponding values. It can be useful to have the current image size printed on it, for example
def getImageText (text, index, size):

	text = text.replace('##index', str(index))
	text = text.replace('##width', str(size[0]))
	text = text.replace('##height', str(size[1]))
	return text


# The text position can have three values
# "top", "center" and "bottom"
# It will always start 10 pixels from the left and keep a 10 pixel margin from the top/bottom
# depending on the case
def getTextPosition (position, size, background_size):
	
	x = 10
	
	if position == 'top':
		y = 10
	elif position == 'center':
		y = int((background_size[1] - size) / 2)
	else:
		y = background_size[1] - size - 10

	return (x, y)


# Appends the output path and image format to the filename
# in order to generate the full string for the save method.
# Replace "##index" from the filename with current image index, either in the original format or zfilled
# The zfill option is useful if you want to keep the images ordered alphabetically
def getOutputPath (index, settings):

	if settings['zfill']:
		# we apply zfill to the image index
		# so the resulting images will be sorted alphabetically
		zfill_length = len(str(settings['total_images']))
		index_string = str(index).zfill(zfill_length)
	else:
		index_string = str(index)

	filename = settings['filename'].replace('##index', index_string)
	
	return settings['output_path'] + '/' + filename + '.' + settings['format']

# This is where the magic happens
def generateImages ():

	config = getConfig()
	settings = config['settings']

	for index in range(0, settings['total_images']):

		background_size  = getSize(settings['size'])
		background_color = getColor(settings['background_color'])
		
		text_color = getTextColor(settings['text_color'], background_color)
		text_size  = settings['text_size']
		text_font  = ImageFont.truetype('FreeMono.ttf', text_size)
		image_text = getImageText(settings['text'], index, background_size)
		text_position = getTextPosition(settings['text_position'], text_size, background_size)
		
		img = Image.new('RGB', background_size, background_color)

		draw_context = ImageDraw.Draw(img)

		draw_context.text(text_position, image_text, font=text_font, fill=text_color)

		output_path = getOutputPath(index, settings)
		img.save(output_path, settings['format'], quality=settings['quality'])
	
	print ('Finished!')


def main ():
	generateImages()

if __name__ == "__main__":
	main()

