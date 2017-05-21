from xml.etree import ElementTree
import requests
import urllib
import json

class Enhancer(object):
    namespaces = {'tcx':'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2',
                  'ae2':'http://www.garmin.com/xmlschemas/ActivityExtension/v2',
                  '':'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2'}
    API_KEY='XXXXXX'
    API_URL='http://elevation.mapzen.com/height'

    def __init__(self,  input, output):
        self.input = input
        self.output = output
        self.points = {}
        for (k,v) in self.namespaces.items():
            ElementTree.register_namespace(k,v)

    def parse_xml(self):
        self.etree = ElementTree.parse(self.input)
        self.xml_points = self.etree.findall('.//tcx:Trackpoint', self.namespaces)

    def get_all_points(self):
        for p in self.xml_points:
            longitude = p.find('./tcx:Position/tcx:LongitudeDegrees')
            latitude = p.find('./tcx:Position/tcx:LatitudeDegrees')
            if longitude is not None and latitude is not None:
                self.ponts[(longitude.text, latitude.text)] = None

    def _build_request_url(self):
        shape_list = [{"lat": k[1], "lon": k[0]} for k in self.points.keys()]
        params=urllib.parse.urlencode({'json':json.dupms(shape_list), 'api_key':self.API_KEY})
        return '{}?{}'.format(self.API_URL,params)


    def get_altitudes(self):
        try:
            resp = requests.get(self._build_request_url())
            json = resp.json
        except:
            json = {}
        else:
            shape = json.get('shape')
            height = json.get('height')
            if shape and height:
                res = zip([(x.get('lon'), x.get('lat')] for x in shape, height))
                for point,height in res:
                    self.points[res[point]] = res[height]

    def append_altitudes(self):
        for p in self.xml_points:
            altitude = ElementTree.Etree('AltitudeMeters')
            longitude = p.find('./tcx:Position/tcx:LongitudeDegrees')
            latitude = p.find('./tcx:Position/tcx:LatitudeDegrees')
            altitude.text =self.points[longitude.text, latitude.text]
            p.append(altitude)

    def write(self)
        self.etree.write(self.output)
