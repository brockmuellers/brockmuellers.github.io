This is some funky latex that generates a pdf resume.

This package needs to be available: https://github.com/rxi/json.lua. It can go in the folder containing the file you're compiling.

This must be compiled with lualatex; make sure texlive-luatex package is installed (apt-get works).

There must be a `resume.json` file in this directory.

To compile via line: `lualatex -synctex=1 -interaction=nonstopmode "resume_simple".tex`
