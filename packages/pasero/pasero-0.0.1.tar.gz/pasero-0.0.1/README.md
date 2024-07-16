# pasero

pasero is a PyPI tool to visualize "Number of isolates" or "% Change" against the baseline of "Past two years average". pasero can be used for detecting outbreaks of pathogens and serotypes.
Execute the pip command provided below in your system terminal to install Pasero. 
Note that the symbol ‘$’ signifies the system prompt. Pasero is an interactive system to show either 'Number of isolates' or 'Past two years average' as baseline and '% Change'.

$ pip install pasero

The subsequent illustration showcases a scenario where ‘Salmonella’ is the chosen pathogen and ‘Sundsvall’ is the selected serotype. The ‘Past two years average and % Change’ option was picked, resulting in a graph with two distinct lines.

<pre>
$ pasero
Pathogens:
1. Campylobacter
2. STEC
3. Salmonella
4. Shigella
5. Vibrio
Select a pathogen by number: 3

Serotypes:
1. Africana
2. Agbeni
3. Agona
  ...
32. Stanley
33. Sundsvall
34. Thompson
35. Typhi
36. Typhimurium
37. Uganda
Select up to 4 serotypes by number (separated by space): 33

1. Number of isolates
2. Past two years average and % Change
Select one by number: 2
</pre>
<img src='https://github.com/y-takefuji/pasero/raw/main/Salmonella_Sundsvall.png' width=640 hight=480>

