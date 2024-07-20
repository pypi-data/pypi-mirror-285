import rasterio
import numpy as np


class IndexCalculation:
    """
    # Contact:
        email: Jesus Aguirre @jaguirre@a4agro.com
        Github: JesusxAguirre


    # Class summary
       This algorithm consists in calculating vegetation indices, these
        indices can be used for precision agriculture for example (or remote
        sensing). There are functions to define the data and to calculate the
        implemented indices.

    # Vegetation index
        https://en.wikipedia.org/wiki/Vegetation_Index
        A Vegetation Index (VI) is a spectral transformation of two or more bands
        designed to enhance the contribution of vegetation properties and allow
        reliable spatial and temporal inter-comparisons of terrestrial
        photosynthetic activity and canopy structural variations

    # Information about channels (Wavelength range for each)
        * nir - near-infrared
            https://www.malvernpanalytical.com/br/products/technology/near-infrared-spectroscopy
            Wavelength Range 700 nm to 2500 nm
        * Red Edge
            https://en.wikipedia.org/wiki/Red_edge
            Wavelength Range 680 nm to 730 nm
        * red
            https://en.wikipedia.org/wiki/Color
            Wavelength Range 635 nm to 700 nm
        * blue
            https://en.wikipedia.org/wiki/Color
            Wavelength Range 450 nm to 490 nm
        * green
            https://en.wikipedia.org/wiki/Color
            Wavelength Range 520 nm to 560 nm


    # IMPORTANT
    this is a class especially uses form 8bands images from planet subscrition imagery sr

        Band 1 : coastal blue
        Band 2 : blue
        Band 3 : greenI
        band 4 : green
        Band 5 : yellow
        Band 6 : red
        Band 7 : RedEdge
        Band 8 : Near-Infrared



    """

    def __init__(
        self,
        image_file: str,
    ):
        self.image_file = image_file
        self.band_red = None
        self.band_nir = None
        self.band_green = None
        self.band_greenI = None
        self.ndvi = None
        self.ndwi = None
        self.ndbi = None
        self.extract_8b(self.image_file)

    def calculate_ndvi(self):
        np.seterr(divide="ignore", invalid="ignore")
        self.ndvi = (self.band_nir.astype(float) - self.band_red.astype(float)) / (
            self.band_nir + self.band_red
        )
        return self.ndvi

    def calculate_ndwi(self):
        "(Float(nir) - Float(green)) / (Float(nir) + Float(green))"

        np.seterr(divide="ignore", invalid="ignore")
        self.ndwi = (self.band_nir - self.band_green) / (
            self.band_nir + self.band_green
        )
        return self.ndwi

    def calculate_gndvi(self):
        "(Float(nir) - Float(greenI)) / (Float(nir) + Float(greenI))"

        np.seterr(divide="ignore", invalid="ignore")
        self.gndvi = (self.band_nir - self.band_greenI) / (
            self.band_nir + self.band_greenI
        )
        return self.gndvi

    def calculate_cgi(self):
        "(Float(nir) / Float(greenI)) - 1"

        np.seterr(divide="ignore", invalid="ignore")
        self.cgi = (self.band_nir / self.band_greenI) - 1
        return self.cgi

    def calculate_ndre(self):
        "(Float(nir) - Float(redEdge)) / (Float(nir) + Float(redEdge))"

        np.seterr(divide="ignore", invalid="ignore")
        self.ndre = (self.band_nir - self.band_redEdge) / (
            self.band_nir + self.band_redEdge
        )
        return self.ndre

    def calculate_5_index(self) -> tuple:
        """This function calculates the five vegetation indices

        Returns:
            tuple: (ndvi, ndwi, gndvi, cgi, ndre)
        """

        ndvi = self.calculate_ndvi()
        ndwi = self.calculate_ndwi()
        gndvi = self.calculate_gndvi()
        cgi = self.calculate_cgi()
        ndre = self.calculate_ndre()

        return (ndvi, ndwi, gndvi, cgi, ndre)

    def extract_8b(self, image_file: str):
        try:
            with rasterio.open(image_file) as src:
                self.band_red = src.read(6)
                self.band_nir = src.read(8)
                self.band_green = src.read(4)
                self.band_greenI = src.read(3)
                self.band_redEdge = src.read(7)

                return (
                    self.band_red,
                    self.band_nir,
                    self.band_green,
                    self.band_greenI,
                    self.band_redEdge,
                )
        except:
            raise ValueError("No se encontró el archivo de imagen")
