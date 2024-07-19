import openeo
import functions as fn

datacube_object = fn.gpr_mapper(sensor = "SENTINEL2_L1C",
               bounding_box = [-4.555088206458265,42.73294534602729,-4.487270722962762,42.7707921305888],
               temporal_extent = ["2021-01-01", "2021-12-31"],
               bands = ['B02', 'B03', 'B04', 'B05', 'B06', 'B07', 'B08','B8A' ,'B11', 'B12'])

datacube_object.construct_datacube("dekad","mean")

datacube_object.process_map("FVC","Sgolay")





