import scrapy
from scrapy.spidermiddlewares.httperror import HttpError

from ..settings import URL_BASE
from ..settings import STARTING_SOUL
from ..settings import ENDING_SOUL
from ..settings import MAX_GAP


class PourSoulSpider(scrapy.Spider):
    name = "people"
    url_template = URL_BASE
    key_template = '{}-step-{}'

    def start_requests(self):
        self.ending_soul = ENDING_SOUL
        self.pour_soul = STARTING_SOUL
        self.gaps = []
        self.current_gap = 0
        self.latest_pour_soul_fetched = 0
        step = '1'
        yield scrapy.Request(url=self.url_template.format(step, self.pour_soul), callback=self.parse_page1, errback=self.errback_furry)

    def errback_furry(self, failure):
        if failure.check(HttpError):
            self.gaps.append(self.pour_soul)
            self.pour_soul += 1
            self.current_gap += 1
            if self.current_gap < MAX_GAP:
                yield scrapy.Request(url=self.url_template.format('1', self.pour_soul), callback=self.parse_page1, errback=self.errback_furry)
            else:
                print('gaps {}'.format(self.gaps))
                print('latest soul fetched {}'.format(self.latest_pour_soul_fetched))


    def parse_page1(self, response):
      if self.pour_soul > self.ending_soul:
          print('gaps {}'.format(self.gaps))
          print('latest soul fetched {}'.format(self.latest_pour_soul_fetched))
          return
      key = self.key_template.format(self.pour_soul, '1')
      yield { key: {
        'document_type': response.xpath('//select[@name="tipo_identificacion"]/option[@selected="selected"]/@value').get(),
        'document_number': response.xpath('//input[@name="cedula_nuip"]/@value').get(),
        'document_expedition': response.xpath('//input[@name="fecha_expedicion_cedula_nuip"]/@value').get(),
        'first_name': response.xpath('//input[@name="primer_nombre"]/@value').get(),
        'last_name':  response.xpath('//input[@name="primer_apellido"]/@value').get(),
        'birth_date':  response.xpath('//input[@name="fecha_nacimiento"]/@value').get(),
        'genre': response.xpath('//select[@name="sexo"]/option[@selected="selected"]/@value').get(),
      }}
      self.current_gap = 0
      self.latest_pour_soul_fetched = self.pour_soul
      yield scrapy.Request(url=self.url_template.format('2', self.pour_soul), callback=self.parse_page2)

    def parse_page2(self, response):
      key = self.key_template.format(self.pour_soul, '2')
      yield { key: {
          'email':  response.xpath('//input[@name="correo_electronico_1"]/@value').get(),
          'confirm_email':  response.xpath('//input[@name="correo_electronico_1_validator"]/@value').get(),
          'line_phone_number':  response.xpath('//input[@name="telefono_fijo_1"]/@value').get(),
          'mobile_number':  response.xpath('//input[@name="telefono_celular_1"]/@value').get(),
          'confirm_mobile_number':  response.xpath('//input[@name="telefono_celular_1_validator"]/@value').get(),
          'referer':  response.xpath('//input[@name="referido"]/@value').get(),
          'referer_position': response.xpath('//select[@name="cargo_referido"]/option[@selected="selected"]/@value').get(),

      }}
      yield scrapy.Request(url=self.url_template.format('3', self.pour_soul), callback=self.parse_page3)

    def parse_page3(self, response):
      key = self.key_template.format(self.pour_soul, '3')
      yield { key: {
        'country': response.xpath('//select[@name="pais_residencia"]/option[@selected="selected"]/@value').get(),
        'state': response.xpath('//select[@name="departamento_residencia"]/option[@selected="selected"]/@value').get(),
        'city': response.xpath('//select[@name="municipio_residencia"]/option[@selected="selected"]/@value').get(),
        'address_part_1': response.xpath('//select[@name="direccion_residencia"]/option[@selected="selected"]/@value').get(),
        'address_part_2':  response.xpath('//input[@name="dir2"]/@value').get(),
        'address_part_3':  response.xpath('//input[@name="dir3"]/@value').get(),
        'address_part_4':  response.xpath('//input[@name="dir4"]/@value').get(),
        'ocupation': response.xpath('//select[@name="ocupacion"]/option[@selected="selected"]/@value').get(),
        'title': response.xpath('//select[@name="profesion"]/option[@selected="selected"]/@value').get(),
      }}
      yield scrapy.Request(url=self.url_template.format('4', self.pour_soul), callback=self.parse_page4)

    def parse_page4(self, response):
      key = self.key_template.format(self.pour_soul, '4')
      yield { key: {
        'country': response.xpath('//select[@name="pais"]/option[@selected="selected"]/@value').get(),
        'state': response.xpath('//select[@name="departamento"]/option[@selected="selected"]/@value').get(),
        'city': response.xpath('//select[@name="ciudad"]/option[@selected="selected"]/@value').get(),
        'locality': response.xpath('//select[@name="localidad"]/option[@selected="selected"]/@value').get(),
      }}
      yield scrapy.Request(url=self.url_template.format('5', self.pour_soul), callback=self.parse_page5)

    def parse_page5(self, response):
      key = self.key_template.format(self.pour_soul, '5')
      yield { key: {
        'has_furicarnet': response.xpath('//select[@name="carnet"]/option[@selected="selected"]/@value').get(),
        'wants_furicarnet': response.xpath('//select[@name="send_carnet"]/option[@selected="selected"]/@value').get(),
        'interests': ''.join(response.xpath('//input[@name="category[]"][@checked="checked"]/@value').getall()),
        'other_topic':  response.xpath('//input[@name="otro"]/@value').get(),
        'underrepresented': response.xpath('//select[@name="comunidad"]/option[@selected="selected"]/@value').get(),
      }}
      self.pour_soul += 1
      yield scrapy.Request(url=self.url_template.format('1', self.pour_soul), callback=self.parse_page1, errback=self.errback_furry)
