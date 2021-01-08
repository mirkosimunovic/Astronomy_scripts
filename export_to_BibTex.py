"""
interfaces to the adsws export service
"""
import ads
import json
import six
import os

from ads.base import APIResponse, BaseQuery
from ads.config import EXPORT_URL


class ExportResponse(APIResponse):
    """
    Data structure that represents a response from the ads export service
    """
    def __init__(self, http_response):
        self._raw = http_response.text
        self.result = http_response.json()['export']

    def __str__(self):
        if six.PY3:
            return self.__unicode__()
        return self.__unicode__().encode("utf-8")

    def __unicode__(self):
        return self.result


class ExportQuery(BaseQuery):
    """
    Represents a query to the adsws export service
    """

    HTTP_ENDPOINT = EXPORT_URL
    FORMATS = ['bibtex', 'bibtexabs', 'ads','endnote', 'aastex',
               'ris', 'icarus', 'mnras', 'soph', 'votable']

    def __init__(self, bibcodes, format="bibtex"):
        """
        :param bibcodes: Bibcodes to send to in the export query
        :type bibcodes: list or string
        :param format: format to export to
        """
        assert format in self.FORMATS, "Format must be one of {}".format(
            self.FORMATS)

        self.format = format

        self.response = None  # current ExportResponse object
        if isinstance(bibcodes, six.string_types):
            bibcodes = [bibcodes]
        self.bibcodes = bibcodes
        self.json_payload = json.dumps({"bibcode": bibcodes})

    def execute(self):
        """
        Execute the http request to the export service
        :return ads-classic formatted export string
        """
        url = os.path.join(self.HTTP_ENDPOINT, self.format)
        self.response = ExportResponse.load_http_response(
            self.session.post(url, data=self.json_payload)
        )
        return self.response.result


if __name__ == '__main__':
    

    # Read the file with all the \bibitem lines
    with open("bibitems.txt",'r') as file:
        lines = file.readlines()


    newfile = open("MyBibliography.bib","w")


    # Split the lines and collect the information about Journal, Volume and Page
    for line in lines:
        txt1 = line.split('\\')[-1]
        txt2 = txt1.split(',')
        bibstem,volume,page = txt2[0],txt2[1],txt2[2][:-1]

        # Execute the Query 
        paper = list(ads.SearchQuery(bibstem=bibstem,volume=volume,page=page))
        try:
            #Get the Bibcode
            bibcode = str(paper[0].bibcode)
            print(bibcode)


            # Query the bibcode and get the export citation
            query = ExportQuery(bibcode,format="bibtex")
            result = query.execute()
            newfile.write(result)


        except:
            print("Paper not Found:",bibstem,volume,page)


    newfile.close()




    # query = ExportQuery("2018MNRAS.473.2590B",format="bibtex")
    # result = query.execute()
    # print(result)

