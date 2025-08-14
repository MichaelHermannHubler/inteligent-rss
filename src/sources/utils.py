import requests
from typing import Optional
from bs4 import BeautifulSoup

def get_content_from_link(
    url: str,
    tag_name: Optional[str] = None,
    class_name: Optional[str] = None
) -> str:
    """
    Fetches the content of a webpage and extracts text from a specific HTML tag or class name.
    The use of tag_name or class_name is exclusive.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        if tag_name and not class_name:
            elements = soup.find_all(tag_name)
        elif class_name and not tag_name:
            elements = soup.find_all(class_=class_name)
        else:
            raise Exception ("Specify either tag_name or class_name, not both.")

        return elements[-1].get_text(separator='\n', strip=True)
    except requests.exceptions.RequestException as e:
        return f"Error fetching the URL: {e}"
    except Exception as e:
        return f"An error occurred: {e}"