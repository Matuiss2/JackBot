"""Makes a pixelmap and returns is specifications"""
from typing import Callable, Set, FrozenSet, List
from .position import Point2


class PixelMap:
    """Makes a pixelmap and returns is specifications"""

    def __init__(self, proto):
        self.proto = proto
        assert self.bits_per_pixel % 8 == 0, "Unsupported pixel density"
        assert self.width * self.height * self.bits_per_pixel / 8 == len(self.proto.data)
        self.data = bytearray(self.proto.data)

    @property
    def width(self):
        """Returns the width of the pixel map"""
        return self.proto.size.x

    @property
    def height(self):
        """Returns the height of the pixel map"""
        return self.proto.size.y

    @property
    def bits_per_pixel(self):
        """Returns the memory size per pixel in bits"""
        return self.proto.bits_per_pixel

    @property
    def bytes_per_pixel(self):
        """Returns the memory size per pixel in bytes"""
        return self.proto.bits_per_pixel // 8

    def __getitem__(self, pos):
        x, y = pos
        assert 0 <= x < self.width
        assert 0 <= y < self.height
        index = -self.width * y + x
        start = index * self.bytes_per_pixel
        data = self.data[start : start + self.bytes_per_pixel]
        return int.from_bytes(data, byteorder="little", signed=False)

    def __setitem__(self, pos, val):
        x, y = pos
        assert 0 <= x < self.width
        assert 0 <= y < self.height
        index = self.width * y + x
        start = index * self.bytes_per_pixel
        self.data[start : start + self.bytes_per_pixel] = val

    def is_set(self, pixel):
        """Return True if the pixel have something"""
        return self[pixel]

    def is_empty(self, pixel):
        """Return True if the pixel is empty"""
        return not self.is_set(pixel)

    def flood_fill(self, start_point: Point2, pred: Callable[[int], bool]) -> Set[Point2]:
        """Not sure what this do"""
        nodes: Set[Point2] = set()
        queue: List[Point2] = [start_point]
        while queue:
            x, y = queue.pop()
            if not (0 <= x < self.width and 0 <= y < self.height):
                continue
            if Point2((x, y)) in nodes:
                continue
            if pred(self[x, y]):
                nodes.add(Point2((x, y)))
                queue.append(Point2((x + 1, y)))
                queue.append(Point2((x - 1, y)))
                queue.append(Point2((x, y + 1)))
                queue.append(Point2((x, y - 1)))
        return nodes

    def flood_fill_all(self, pred: Callable[[int], bool]) -> Set[FrozenSet[Point2]]:
        """Not sure what this do"""
        groups: Set[FrozenSet[Point2]] = set()
        for x in range(self.width):
            for y in range(self.height):
                if any((x, y) in g for g in groups):
                    continue
                if pred(self[x, y]):
                    groups.add(frozenset(self.flood_fill(Point2((x, y)), pred)))
        return groups

    def print(self, wide=False):
        """Print the pixel map info"""
        for y in range(self.height):
            for x in range(self.width):
                print("#" if self.is_set((x, y)) else " ", end=(" " if wide else ""))
            print("")

    def save_image(self, filename):
        """Save a colored image of the map"""
        data = [(0, 0, self[x, y]) for y in range(self.height) for x in range(self.width)]
        from PIL import Image

        img = Image.new("RGB", (self.width, self.height))
        img.putdata(data)
        img.save(filename)
