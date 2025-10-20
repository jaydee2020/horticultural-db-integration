"""
sci_name_parser Module

This module provides functions to parse scientific plant names and integrate the parsed components into pandas DataFrames.
The functions rely on the positions of the name parts,
so the scientifc name to be parsed must be in the standard format: Genus (hybrid designation: ×) species (infraspecies designation: subspecies, variety, form) infraspecies.

Functions:
    parse_scientific_name(scientific_name, ingnore_form=False): Parses a scientific name string into its constituent parts (genus, species, infraspecies, etc.) and determines its taxonomic rank.
    generate_scientific_columns(row, scientific_name_col, ignore_form=False): Applies the parse_scientific_name function to a DataFrame row and adds new columns for each parsed component.

Dependencies:
    pandas

Example Usage:
    # Assuming you have a pandas DataFrame named 'df' with a column named 'scientific_name'
    # from sci_name_parser import generate_scientific_columns
    # df = df.apply(generate_scientific_columns, axis=1, scientific_name_col='scientific_name')
"""

def generate_scientific_columns(row, scientific_name_col, ignore_form=False):
  """Generates new columns in a DataFrame row based on a scientific name.

  Args:
    row: A pandas DataFrame row.
    scientific_name_col: The name of the column in the row containing the scientific name.
    ignore_form: A boolean indicating whether to ignore the 'f.' abbreviation for form (default: False).

  Returns:
    The modified DataFrame row with added columns for parsed scientific name components.
  """
  parsed_scientific_name = parse_scientific_name(row[scientific_name_col], ignore_form)
  for key in parsed_scientific_name:
    row[key] = parsed_scientific_name[key]
  return row

def parse_scientific_name(scientific_name, ingnore_form=False):
  """Parses a scientific name string into its constituent parts and determines its taxonomic rank.

  Args:
    scientific_name: A string containing the scientific name to parse.
    ingnore_form: A boolean indicating whether to ignore the 'f.' abbreviation
                  for form, which can be confused with bibliographic information
                  (default: False).

  Returns:
    A dictionary containing the parsed components of the scientific name,
    including 'taxon_rank', 'genus', 'species', 'genus_hybrid', 'species_hybrid',
    'infraspecies', 'variety', 'subspecies', and 'form'. Returns None if the
    input scientific name is empty.
  """

  #define the various abbreviations that can appear in a scientific name
  hybrid = ['×','\u00D7']
  abbreviation_ignore = ['cv','cv.','var','var.','sp','sp.','ssp','ssp.','sbsp','sbsp.','subsp','subsp.','X','x','×','\u00D7','f.']

  Taxon_Rank = ''
  Genus = ''
  Species = ''
  Genus_Hybrid = ''
  Species_Hybrid = ''
  Infraspecies = ''
  Variety = ''
  Subspecies = ''
  Form = ''

  #ensure correct use of the multiplication sign for hybrids
  scientific_name_clean = scientific_name.replace(' x ',' × ').replace(' X ',' × ')

  #break the scientific name into parts
  scientific_name_tokens=scientific_name_clean.split()

  if len(scientific_name_tokens) == 0:
    return None

  #determine the plant classification based on the scientific name structure:

  #check for special case of genus hybrid e.g. '×genus species'
  if (scientific_name_tokens[0][0] in ['×','\u00D7']) & (len(scientific_name_tokens[0]) != 1):
    Genus_Hybrid = '\u00D7'
    scientific_name_tokens[0] = scientific_name_tokens[0][1:]

  Genus = scientific_name_tokens[0]

  #check for 'Genus'
  if (len(scientific_name_tokens) == 1):
    Taxon_Rank='Genus'
  #check for e.g. 'Genus cv.'
  elif ((len(scientific_name_tokens) == 2) & (scientific_name_tokens[1] in abbreviation_ignore)):
    Taxon_Rank='Genus'
    scientific_name_tokens.pop(1)

  #check for species hybrid
  if any('\u00D7' in item for item in scientific_name_tokens):
    Species_Hybrid = '\u00D7'
    scientific_name_tokens = list(filter(None,[token.replace('×', '') for token in scientific_name_tokens]))

  #the processed scientific name will now start with 'Genus species' or 'Genus'

  #if 'Genus species' update the species
  if len(scientific_name_tokens) > 1 :
    Species = scientific_name_tokens[1]
    Taxon_Rank = 'Species'

  #check for variety e.g. 'Genus species var. variety'
  try:
    if ('var.' in scientific_name_tokens):
        Infraspecies = Variety = scientific_name_tokens[scientific_name_tokens.index('var.')+1]
        Taxon_Rank = 'Variety'
    elif ('var' in scientific_name_tokens):
        Infraspecies = Variety = scientific_name_tokens[scientific_name_tokens.index('var')+1]
        Taxon_Rank = 'Variety'
  except IndexError:
    print('variety index out of range: ',scientific_name)

  #check for subspecies e.g. 'Genus species subsp. subspecies'
  try:
    if ('subsp.' in scientific_name_tokens):
      Infraspecies = Subspecies = scientific_name_tokens[scientific_name_tokens.index('subsp.')+1]
      Taxon_Rank='Subspecies'
    elif ('ssp.' in scientific_name_tokens):
      Infraspecies = Subspecies = scientific_name_tokens[scientific_name_tokens.index('ssp.')+1]
      Taxon_Rank = 'Subspecies'
    elif ('sbsp.' in scientific_name_tokens):
      Infraspecies = Subspecies = scientific_name_tokens[scientific_name_tokens.index('sbsp.')+1]
      Taxon_Rank = 'Subspecies'
    elif ('subsp' in scientific_name_tokens):
      Infraspecies = Subspecies = scientific_name_tokens[scientific_name_tokens.index('subsp')+1]
      Taxon_Rank = 'Subspecies'
  except IndexError:
    print('subspecies index out of range: ',scientific_name)

  #check for form e.g. 'Genus species f. form'
  #form can be ignored if the scientific name includes bibliographic information
  #where 'f.' is also used as an abbreviation for 'fils'
  if not ingnore_form:
    try:
      if ('f.' in scientific_name_tokens):
        Infraspecies =  Form = scientific_name_tokens[scientific_name_tokens.index('f.')+1]
        Taxon_Rank = 'Form'
    except IndexError:
        print('form index out of range: ',scientific_name)

  parsed_scientific_name = {'taxon_rank': Taxon_Rank,
                            'genus': Genus,
                            'species': Species,
                            'genus_hybrid': Genus_Hybrid,
                            'species_hybrid': Species_Hybrid,
                            'infraspecies': Infraspecies,
                            'variety': Variety,
                            'subspecies': Subspecies,
                            'form': Form
                            }

  return parsed_scientific_name
