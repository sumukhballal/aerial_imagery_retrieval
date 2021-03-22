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
    tile_x=pixels[0]/256
    tile_y=pixels[1]/256

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
def get_image(url):

    response=requests.get(url, stream=True)

    # Write image to directory


    return image



def download_images(tile_left, tile_right, level):

    quad_key=get_quad_key((), level)
    tile_image=get_image("http://h0.ortho.tiles.virtualearth.net/tiles/h"+quad_key+".jpeg?g=131")




if __name__ == '__main__':
    #Take input
    input_object=input_main()
    # Get the pixel locations
    pixel_left=get_pixel_xy(input_object.left_latitude, input_object.left_longitude, input_object.level)
    pixel_right=get_pixel_xy(input_object.right_latitude, input_object.right_longitude, input_object.level)
    # Get the tile locations
    tile_left=get_tile_position(pixel_left)
    tile_right=get_tile_position(pixel_right)
    # Download Image
    download_images(tile_left, tile_right, input_object.level)




