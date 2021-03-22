from math import cos, pi, sin, log
import requests
import numpy
import cv2 as cv

class input_o:
    def __init__(self, left_latitude, left_longitude, right_latitude, right_longitude, level):
        self.left_latitude=left_latitude
        self.left_longitude=left_longitude
        self.right_latitude=right_latitude
        self.right_longitude=right_longitude
        self.level=level


# Take input
def input_main():
    print("Enter Ground resolution! Between 1 and 23! ")
    level=int(input())
    print("Enter left top corner coordinates! \n Latitude: \n")
    latitude_1=float(input())
    print("Longitude: \n")
    longitude_1=float(input())
    print("Enter bottom right corner coordinates! \n Latitude: \n")
    latitude_2=float(input())
    print("Longitude: \n")
    longitude_2=float(input())
    return input_o(latitude_1, longitude_1, latitude_2, longitude_2, level)

## Get map size from level
def get_map_size(level):
    return int(256*2**level)

## Get Map scale
def get_map_scale(latitude, level, dpi):
    return float((get_ground_resolution(latitude, level) * dpi)/0.0254)

## Clip the input number to a max or min value
def clip(number, min_value, max_value):
    return min(max(number, min_value), max_value)


## Get ground resolution
def get_ground_resolution(latitude, level):
    latitude=clip(latitude, -85.05113, 85.05113)
    return float(cos(latitude*pi/180)*2*pi*6378137/get_map_size(level))


## Get pixel coordinates
def get_pixel_xy(latitude, longitude, level):
    latitude=clip(latitude, -85.05113, 85.05113)
    longitude=clip(longitude, 0, 180)

    x=(longitude+180)/360
    sin_lat=sin(latitude * pi/180)
    y=0.5-log((1+sin_lat)/(1-sin_lat))/(4*pi)
    map_size=get_map_size(level)

    pixel_x=int(clip(x * map_size + 0.5, 0, map_size-1))
    pixel_y=int(clip(y * map_size + 0.5, 0, map_size-1))

    return (pixel_x,pixel_y)


## Get tile position
def get_tile_position(pixels):
    tile_x=int(pixels[0]/256)
    tile_y=int(pixels[1]/256)

    return (tile_x, tile_y)

## Get quad key string
def get_quad_key(tiles, level):

    quad_key=""

    while level>0:
        mask=1<<(level-1)
        d=0
        if((tiles[0] & mask)!=0):
            d+=1
        if((tiles[1] & mask)!= 0):
            d+=2

        quad_key = quad_key + str(d)
        level=level-1

    return quad_key


# Get a image with quad key
def get_image(url, image_name):

    response=requests.get(url)
    print("Downloaded tile : "+image_name)
    # Write image to directory
    with open("tiles/"+image_name, "wb") as f:
        f.write(response.content)

    image=numpy.asarray(bytearray(response.content), dtype="uint8")

    return cv.imdecode(image, cv.IMREAD_COLOR)




def download_images(tile_left, tile_right, level):

    i=1
    y_image_list=[]
    for i_y in range(tile_left[1], tile_right[1]+1):
        x_image_list=[]
        for i_x in range(tile_left[0], tile_right[0]+1):
            quad_key=get_quad_key((i_x, i_y), level)
            image_array=get_image("http://h0.ortho.tiles.virtualearth.net/tiles/h"+quad_key+".jpeg?g=131", "tile_"+str(i)+".jpeg")
            x_image_list.append(image_array)
            i=i+1
        x_image_concatenated=numpy.concatenate(x_image_list,1)
        y_image_list.append(x_image_concatenated)

    return y_image_list



def correct_inputs(x, y):
    right_1=max(x[1],y[1])
    right_0=max(x[0],y[0])
    left_0=min(x[0],y[0])
    left_1 = min(x[1], y[1])

    x=(left_0, left_1)
    y=(right_0, right_1)

    return (x, y)


def stitch_images(images):
    images=numpy.concatenate(images, 0)
    cv.imwrite("final_stitched_image.jpeg", images)


if __name__ == '__main__':
    #Take input
    input_object=input_main()
    # Get the pixel locations
    print("Get Pixel locations! ")
    pixel_left=get_pixel_xy(input_object.left_latitude, input_object.left_longitude, input_object.level)
    pixel_right=get_pixel_xy(input_object.right_latitude, input_object.right_longitude, input_object.level)
    # Get the tile locations
    print("Get Tile locations! ")
    tile_left=get_tile_position(pixel_left)
    tile_right=get_tile_position(pixel_right)
    # Correct the inputs
    print("Correct the inputs! ")
    pixel_left, pixel_right=correct_inputs(pixel_left, pixel_right)
    tile_left, tile_right=correct_inputs(tile_left, tile_right)
    # Download Image
    print("Download the tiles! ")
    images=download_images(tile_left, tile_right, input_object.level)
    # Stitch images
    print("Stitching the downloaded tiles! ")
    stitch_images(images)



