import random

class ImageTrainingSet(object):

    def __init__(self, olsh, imgwidth=512, imgheight=512):
        """Opens an image .dat file at the path given by `olsh`."""
        if isinstance(olsh, str):
            self.olsh = open(olsh)
        elif isinstance(olsh, list):
            self.olsh = olsh
        self.imgwidth = imgwidth
        self.imgheight = imgheight
        self.__parse_olsh()

    def __parse_olsh(self):
        self.images = []
        for i,line in enumerate(self.olsh):
            row = [float(px) for px in line.strip().split(' ') if px]
            ex = i / self.imgheight
            y = i % self.imgheight
            if y == 0: # start of a new image
                self.images.append([])
            self.images[ex].append(row)

    def get_example(self, width, height):
        """Returns an array of `width`-times-`height` pixel values (floats)
        from a randomly `width`-by-`height` region of a randomly chosen
        image."""
        img = random.choice(self.images)
        startx = random.randint(0, self.imgwidth - width)
        starty = random.randint(0, self.imgheight - height)
        pixels = []
        for y in xrange(starty, starty+height):
            pixels.extend(img[y][startx:startx+width])
        return pixels



import unittest
class ImageTrainingSetTest(unittest.TestCase):
    sample_dat = ["3.4344572e-001  2.0327842e-001  2.7077097e-000\n", "0.3 0.4 0.5\n",
                  "1.2344572e-001  4.1327842e-001  1.8077097e-000\n", "0.6 0.7 0.5\n"]

    def setUp(self):
        self.ts = ImageTrainingSet(self.sample_dat, imgwidth=3, imgheight=2)

    def test_parses_sample_dat(self):
        expected = [[[0.34344572, 0.20327842, 2.7077097], [0.3, 0.4, 0.5]],
                     [[0.12344572, 0.41327842, 1.8077097], [0.6, 0.7, 0.5]]]
        self.assertEqual(len(self.ts.images), 2)
        for i,image in enumerate(expected):
            for j,row in enumerate(image):
                for k,px in enumerate(row):
                    self.assertAlmostEqual(self.ts.images[i][j][k], px)

    def test_parses_olsh(self):
        olsh = ImageTrainingSet('olsh.dat', imgwidth=512, imgheight=512)
        ex = olsh.get_example(8, 8)
        self.assertEqual(len(ex), 64)

    def test_get_example_dimensions(self):
        ex = self.ts.get_example(2, 2)
        self.assertEqual(len(ex), 4)

if __name__ == "__main__":
    unittest.main()
    #ts = ImageTrainingSet('olsh.dat', imgwidth=512, imgheight=512)
    #print ts.get_example(8,8)
