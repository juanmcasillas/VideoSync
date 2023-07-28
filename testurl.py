
from urllib.request import Request, urlopen
import io
from PIL import Image, ImageDraw

# Function to get the page content
def get_page_content(url, head=None):
    """
    Function to get the page content
    """
    if not head:
        head = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive',
        #'refere': 'https://example.com',
        #'cookie': """your cookie value ( you can get that from your web page) """
        }


    req = Request(url, headers=head)
    return urlopen(req)






if __name__ == "__main__":
    url = "https://b.tile.openstreetmap.org/19/255800/197938.png"
    fd = get_page_content(url)
    image_file = io.BytesIO(fd.read())
    fd.close()
    
    tileimage = Image.open(image_file)
    tileimage.save("demo","PNG")
    
    