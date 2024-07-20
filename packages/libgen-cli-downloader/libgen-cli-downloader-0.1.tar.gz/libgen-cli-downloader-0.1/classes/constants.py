from pathlib import Path
TABLECOLNAMES = [
    "ID",
    "Author",
    "Title",
    "Year",
    "Pages",
    "Language",
    "Size",
    "Extension",
]

SEARCHOPTIONS = {
    1: "Title",
    2: "Author",
    3: "Series",
    4: "Publisher",
    5: "Year",
    6: "ISBN",
}

DOWNLOADPATH = Path.home() / "Downloads"
WELCOMEMESSAGE = "Welcome to libgen-cli! Search for books by title, author, series, publisher, year, or ISBN.\n"