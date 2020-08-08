#!/usr/bin/env python3

"""
Dependencies:
    * apt install imagemagick
"""

from PIL import Image

import argparse


def tile_is_same(tile, new_tile):
    """Not all transparent pixels were made equal.
    Can't use ImageChops' difference function because they compare all
    channels even when the pixel is totally transparent.

    Our difference function will consider two pixel to be identical when
    alpha = 0, regardless of the values in the other channels.
    """

    # Image size check
    if tile.size != new_tile.size:
        return False

    for y in xrange(tile.height):
        for x in xrange(tile.width):
            tile_pixel = tile.getpixel((x, y))
            new_tile_pixel = new_tile.getpixel((x, y))

            if tile_pixel[3] == 0 and new_tile_pixel[3] == 0:
                continue

            if tile_pixel != new_tile_pixel:
                return False
    return True


def create_tile_list(im, tile_w, tile_h):
    """Returns list of tile images that comprise the input image.
    If the image is not a multiple of tile size, the right col and bottom row
    areas of the image will not be tiled.
    Redundant tiles are deduplicated.

    Args:
        im (Image): Input image
        tile_w (int): Tile width in pixels
        tile_h (int): Tile height in pixels
    Returns:
        tile_list (list): List of Image tiles.
    """
    tile_list = []
    im_w, im_h = im.size
    for y in xrange(0, (im_h / tile_h)):
        for x in xrange(0, (im_w / tile_w)):
            left = x * tile_w
            upper = y * tile_h
            right = left + tile_w
            lower = upper + tile_h
            new_tile = im.crop((left, upper, right, lower))

            # Only add unique tiles to list
            add_tile = True
            for tile in tile_list:
                if tile_is_same(tile, new_tile):
                    add_tile = False
                    break

            if add_tile:
                tile_list.append(new_tile)

    print('Number of Tiles: ' + str(len(tile_list)))
    return tile_list


def save_to_tileset(tile_list, tile_w, tile_h, output_path):
    """
    Args:
        tile_list (list): List of PIL Images, each represents a tile.
        tile_w (int): Tile width in pixels
        tile_h (int): Tile height in pixels
        output_path (str): Relative path
    Returns:
        None
    """
    TILES_IN_ROW = 16
    if len(tile_list) < TILES_IN_ROW:
        tileset_w = len(tile_list) * tile_w
    else:
        tileset_w = TILES_IN_ROW * tile_w
    tileset_h = int((len(tile_list) / TILES_IN_ROW) + 1) * tile_h
    tileset = Image.new('RGBA', (tileset_w, tileset_h))

    for i, tile in enumerate(tile_list):
        x = (i % TILES_IN_ROW) * tile_w
        y = (i / TILES_IN_ROW) * tile_h
        tileset.paste(tile, (x, y))

    tileset.save(output_path)
    print('Done. Your tileset was saved to ' + output_path)


def main():
    parser = argparse.ArgumentParser(description='Image to tileset converter')
    parser.add_argument('-i', action='store', dest='image_path', type=str,
                        required=True, help='Relative path to image. Expects \
                        png.')
    parser.add_argument('-o', action='store', dest='output_path', type=str,
                        required=True, help='Relative path to the output \
                        tileset. Outputs a PNG.')
    parser.add_argument('-x', action='store', dest='tile_width', type=int,
                        required=False, default=8, help='Size of tile width in \
                        pixels.')
    parser.add_argument('-y', action='store', dest='tile_height', type=int,
                        required=False, default=8, help='Size of tile width in \
                        pixels.')
    args = parser.parse_args()

    im = Image.open(args.image_path)
    tiles = create_tile_list(im, args.tile_width, args.tile_height)
    save_to_tileset(tiles, args.tile_width, args.tile_height, args.output_path)
    im.close()


if __name__ == '__main__':
    main()
