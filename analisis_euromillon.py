from scrapy.spiders import Spider
from scrapy.crawler import CrawlerProcess
from scrapy.selector import Selector
from scrapy.item import Field
from scrapy.item import Item
from scrapy.loader.processors import MapCompose
from scrapy.loader import ItemLoader
import datetime
import re


class CombinacionEuromillon(Item):
    numeros = Field()
    estrellas = Field()
    el_millon = Field()
    fecha_sorteo = Field()


class EuromillonSpider(Spider):
    name = "EuromillonSpider"
    start_urls = ["https://www.euromillones.com.es/historico/resultados-euromillones-2020.html"]
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/71.0.3578.80 Chrome/71.0.3578.80 Safari/537.36'
    }    

    def parse(self,response):
        sel = Selector(response) 
        x = re.search(r"(\d{4})\.html$", response.request.url)
        anyo = int(x.group(1))
        sorteos = sel.xpath('//table[@class="histoeuro"]/tbody/tr')
        conv_mes = {'ene':1,'feb':2,'mar':3,'abr':4,'may':5,'jun':6,'jul':7,'ago':8,'sep':9,'oct':10,'nov':11,'dic':12}
        for i, sorteo in enumerate(sorteos):
            if i in [0,1] or sorteo.xpath('./td[last()]/text()').get() is None:
                continue
             
            lista_numeros = list()
            lista_numeros.append(sorteo.xpath('./td[last()-7]/text()').get())
            lista_numeros.append(sorteo.xpath('./td[last()-6]/text()').get())
            lista_numeros.append(sorteo.xpath('./td[last()-5]/text()').get())
            lista_numeros.append(sorteo.xpath('./td[last()-4]/text()').get())
            lista_numeros.append(sorteo.xpath('./td[last()-3]/text()').get())
            lista_estrellas = list()
            lista_estrellas.append(sorteo.xpath('./td[last()-2]/text()').get())
            lista_estrellas.append(sorteo.xpath('./td[last()-1]/text()').get())
            parseo_fecha = re.search(r"(\d{1,2})-(\w{3})",sorteo.xpath('./td[last()-8]/text()').get())
            dia = int(parseo_fecha.group(1))
            mes_abrv = parseo_fecha.group(2)
            mes = conv_mes.get(mes_abrv)
            fecha_sorteo = datetime.datetime(anyo,mes,dia)
            
            item = ItemLoader(CombinacionEuromillon(), sorteo)
            item.add_value('numeros', lista_numeros)
            item.add_value('estrellas', lista_estrellas)            
            item.add_xpath('el_millon','./td[last()]/text()')
            item.add_value('fecha_sorteo',fecha_sorteo)
            yield item.load_item()
            print('---')


if __name__=="__main__":
    process= CrawlerProcess()
    process.crawl(EuromillonSpider)
    process.start()