import inspect, os, shutil

from django.test import TestCase, Client
from django.core.files import File
from django.core.urlresolvers import reverse

from raster.models import RasterLayer, LegendSemantics, LegendEntry, Legend
from django.test.utils import override_settings

@override_settings(RASTER_TILE_CACHE_TIMEOUT=0)
class RasterTmsTests(TestCase):

    def setUp(self):
        # Instantiate Django file instances with nodes and links
        self.pwd = os.path.dirname(os.path.abspath(
            inspect.getfile(inspect.currentframe())))

        sourcefile = File(open(os.path.join(self.pwd, 'raster.tif.zip')))

        # Create raster layer
        self.rasterlayer = RasterLayer.objects.create(
            name='Raster data',
            description='Small raster for testing',
            datatype='ca',
            srid='3086',
            nodata='0',
            rasterfile=sourcefile)

        self.tile = self.rasterlayer.rastertile_set.filter(is_base=False).first()
        self.tile_url = url = reverse('algebra', kwargs={'z': self.tile.tilez, 'y': self.tile.tiley, 'x': self.tile.tilex, 'format': '.png'})

        self.client = Client()

    def tearDown(self):
        shutil.rmtree(os.path.dirname(os.path.join(
            self.pwd, '../..', self.rasterlayer.rasterfile.name)))
        self.rasterlayer.rastertile_set.all().delete()

    def test_basic_algebra_request(self):
        response = self.client.get(self.tile_url + '?layers={0}&formula=a'.format(self.rasterlayer.id))
        self.assertEqual(response.status_code, 200)
