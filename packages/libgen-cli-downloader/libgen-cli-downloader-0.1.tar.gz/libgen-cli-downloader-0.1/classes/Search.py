from api.libgen_search import LibgenSearch
from beautifultable import BeautifulTable
from . import constants

class Search:
    def __init__(self) -> None:
        self.libgenSearch = LibgenSearch()

    def setSearchResult(self, search_term: str, search_type: str) -> list:
        return self.libgenSearch.search(search_term, search_type=search_type)

    def getSearchResult(self,results):
        table = BeautifulTable()
        for index, item in enumerate(results):

            item["ID"] = index + 1
            table.columns.header = constants.TABLECOLNAMES
            table.rows.append([item[name] for name in constants.TABLECOLNAMES])
            table.columns.width = [4,14,22,6,6,10,6,6]
        print(table)
