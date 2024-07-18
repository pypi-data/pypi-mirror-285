import os
import pandas as pd
import sys

def fp_interpreter(file_path):
    """Using pandas, transforms the csv file into a dataframe. The dataframe is then turned into a list that is iterated through in the doc_scanner function."""
    df = pd.read_csv(file_path, header=None)
    forbidden_phrases_csv = df[0].tolist()
    return forbidden_phrases_csv

def doc_scanner(forbidden_phrases, doc):
    """This function scans each line in the html file 'doc' and ensures there are no instances of any forbidden words or phrases from the 'forbidden_phrases' list."""
    with open(doc, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    results = []
    for phrase in forbidden_phrases:
        forbidden_phrase_lower = phrase.lower()
        for i in range(len(lines)):
            line = lines[i]
            line_lower = line.lower()
            index = 0
            while True:
                # This checks for multiple instances of the same forbidden phrase on a single line in the HTML doc. The find method starts from index;
                # at each instance of a forbidden phrase, the loop calls the find method again from the ending index of the previously found forbidden phrase.
                # If the find method finds no forbidden phrases, index will == -1, which will break the infinite while loop.
                index = line_lower.find(forbidden_phrase_lower, index)
                if index == -1:
                    break
                fp_result2 = phrase + " : line " + str(i + 1)
                results.append(fp_result2)
                index += len(forbidden_phrase_lower)
    return results

current_dir = os.path.dirname(__file__)
forbidden_phrases_path = os.path.join(current_dir, "..", "data", "Style Guide Phrases.csv") #Add a csv file in the data folder and change the file name in the quotes here to change the default CSV file. 
forbidden_phrases_default = fp_interpreter(forbidden_phrases_path)
example_doc= "C:\\Code Repository\\Code Bin Python\\example.html"

'''
Testing:
finalresult = doc_scanner(forbidden_phrases_csv, example_doc)
#print(finalresult)
'''

if __name__ == "__main__":
    default_or_not = input("Use default csv file of forbidden phrases? (respond Y or N): ", )
    if default_or_not.lower() == "y":
        doc = input("Enter path of html file: ").strip('"').strip()
        finalresult = doc_scanner(forbidden_phrases_default, doc)
        if len(finalresult) > 0:
            for result in finalresult:
                print(result)
        else:
            print("No forbidden words/phrases found.")
        sys.exit()
    if default_or_not.lower( )== "n":
        forbidden_phrases_custom = input("Enter path of your custom csv file: ").strip('"').strip()
        doc = input("Enter path of HTML file: ").strip('"').strip()
        forbidden_phrases_custom = fp_interpreter(forbidden_phrases_custom)
        finalresult = doc_scanner(forbidden_phrases_custom, doc)
        if len(finalresult) > 0:
            for result in finalresult:
                print(result)
        else:
            print("No forbidden words/phrases found.")
        sys.exit()
    else:
        print("Invalid argument(s). Please check GitHub documentation for more information on argument formatting.")
        sys.exit()