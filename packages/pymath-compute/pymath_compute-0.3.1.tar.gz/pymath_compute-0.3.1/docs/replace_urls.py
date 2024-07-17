"""
File in Python that include a function that replace all the URLs by a pre-determined url
"""
import os
import re

patterns = [
    r'/favicon.ico', r'/_next/static/',
    r'/projects', r'/banner.png'
]


def replace_patterns(url: str) -> None:
    """Replace the patterns in the URL"""
    # Get a list of all HTML files in the repository
    html_files = []
    for root, _, files in os.walk("."):
        for file in files:
            if file.endswith(".html"):
                html_files.append(f"{root}/{file}")
    # Process each HTML file
    for filename in html_files:
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read()
            # Modify the content using the given patterns
            for pattern in patterns:
                content = re.sub(pattern, f'{url}{pattern}', content)
        # Store the modified content back to the file
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(content)


if __name__ == "__main__":
    replace_patterns(
        os.environ.get("URL", "")
    )
