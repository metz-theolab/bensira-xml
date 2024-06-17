"""Convert Ben Sira XML to HTML for proof-reading.
"""
from pathlib import Path
from xml.etree import ElementTree


if __name__ == "__main__":
    for file_path in Path("../tei_files").glob("*.xml"):
        print(f"Converting {file_path} to HTML...")
        parsed_manuscript = ElementTree.parse(file_path).getroot()
        
        # Create a new HTML file
        with open(f"htmls/{Path(file_path).stem}.html", "w") as html_file:
            # Iterate over the XML elements
            for element in parsed_manuscript.iter():
                if element.tag == "ms":
                    html_file.write(f"<!DOCTYPE html>\n<html>\n<head>\n<title>{element.attrib['name']}</title>\n</head>\n<body><h1>{element.attrib['name']}</h1>\n")

                if element.tag == "div":
                    if element.attrib["type"] == "chap":
                        html_file.write(f"<h2>Chapter {element.attrib['n']}</h2>\n")
                    elif element.attrib["type"] == "verse":
                        html_file.write(f"<h3>Verse {element.attrib['n']}</h3>\n")
                elif element.tag == "w" and element.text:
                    html_file.write(f"{element.text} ")
                elif element.tag == "w" and element.tail:
                    html_file.write(f"{element.tail} ")