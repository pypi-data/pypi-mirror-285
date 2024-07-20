from . import constants
import requests
from tqdm import tqdm
from api.libgen_search import LibgenSearch

class Download:
    def __init__(self, item) -> None:
        self.libgen = LibgenSearch()
        self.block_size = 1024
        self.downloadPath = constants.DOWNLOADPATH
        self.item = item
        self.title = item["Title"] + "." + item["Extension"]

    def setMirrors(self):
        try:
            mirrors = self.libgen.resolve_download_links(self.item)
        except:
            print("Failed to get download link")
            return
        return mirrors
    
    def choseMirror(self):
        mirrors = self.setMirrors()

        print(f"Choose a mirror to download the {self.title} from:")

        for index, mirror in enumerate(mirrors):
            print(f"{index + 1}. {mirror}")

        choice = int(input("Enter the mirror number:"))
        return mirrors[list(mirrors.keys())[choice - 1]]
    
    def download(self):
        try:
            downloadMirror = self.choseMirror()
        except Exception as e:
            print("getMirrors failed")
            print(f"Failed to download the file: {e}")
            return
        
        try:
            response = requests.get(downloadMirror, stream=True)
        except Exception as e:
            print(f"requests.get failed {e}")
            
            return
        
        try:
            totalSize = int(response.headers.get("content-length", 0))

            with tqdm(total=totalSize, unit="B", unit_scale=True) as progress_bar:
                with open(self.downloadPath / self.title, "wb") as file:
                    for data in response.iter_content(self.block_size):
                        progress_bar.update(len(data))
                        file.write(data)
        except Exception as e:
            print("download failed")
            print(f"Failed to download the file: {e}")
            return

        