# -*- coding: cp1252 -*-
from parsimonious.grammar import Grammar
grammar = Grammar(
    """
    document = vitals_line+ / line+
    vitals_line = start_line vital_text special
    line = start_line text* special
    text = space* word* space*
    vital_text = ~".*(Vitals Assessment).*"s
    word = character*
    character = letter / digit / symbol
    letter = ~"[a-z]"i
    digit  = ~"[0-9]"
    symbol = ~"[\[\]{\})(><\'\\".\-:=|,/;%\^?!@#\$\&\*+]"
    special = "\\n" / "\\r" / "\\t"
    space  = " "
    start_line = "" / word


    """)

myfile = open('test.txt','r')


text = myfile.read().replace("°","")
print grammar.parse(text)
