#####Settings and Dependencies#####
#Ensure all dependencies are installed
import replicate
import re
import time
import random
import os
import string

#Abstract ID Range  
abstractindices =   [35, 46, 53, 54, 61, 64, 68, 69, 82, 86, 94, 96, 108, 113, 115, 118, 124, 126, 149, 152, 153, 154, 157, 165, 172, 186, 198, 200, 222, 225, 234, 242, 267, 268, 269, 270, 277, 280, 282, 288, 291, 294, 296, 300, 301, 304, 320, 333, 338, 339, 342, 351, 356, 360, 361, 373, 377, 381, 382, 384, 394, 398, 401, 403, 407, 420, 424, 436, 441, 450, 454, 464, 468, 472, 474, 483, 487, 488, 498, 499, 513, 519, 521, 529, 550, 553, 555, 557, 558, 559, 561, 570, 586, 590, 592, 603, 606, 609, 614, 627]
#For random sample, set sampletype to "random" for random sample and specify parameters
sampletype = "mrandom"
samplesize = 32
inclusionvalue = 1


#Clear Output Files? Type "Yes" to clear output files
clearoutput = "Yes"

#Input and Output Abstract Text Files, Ensure that Abstracts are Separated with "Parsing Key"
inputtext = r"AbstractTexts\Meijboom_2021.txt"
outputtext = r"Llamaoutput.txt"
condensedoutputtext = r"Llamacondensedoutput.txt"
criteriaoutputtext = r"Llamacriteriaoutput.txt"
with open('baseprompt.txt', encoding = "utf-8") as f:
    baseprompt = f.read()
with open("eligibilitycriteria.txt", encoding = "utf-8") as f:
    eligibility_criteria = f.read()
print(type(baseprompt))
print(type(eligibility_criteria))
#Base Prompt to Ask Llama to Screen Literature Based on Specified Eligiblity Criteria"
numofcriteria = 8
criterialist = [0]

#Intialize API Key"
os.environ["REPLICATE_API_TOKEN"] = ""

#Initialize Time in Seconds to Wait in Between Llama Queries
sleeptime = 1

#Llama Query Settings
temperature = .5
max_tokens = 20
top_p = 1
frequency_penalty = 0
presence_penalty = 0


#####Do not modify the rest of the script#####
#Initialize Criteria Outcome (1 for Meets Criteria, 0 for Does Not Meet)
criteriaoutcome = 0

#Clear Output Text Files
if clearoutput == "Yes":
    with open(outputtext, "w") as file:
        pass
    with open(condensedoutputtext, "w") as file:
        pass
    with open(criteriaoutputtext, "w") as file:
        pass
    with open(outputtext, "a", encoding='utf-8') as file:
        # Write the output to the file
            file.write("Llama Full Output: Abstract, Response")
            file.write("\n")
    #Set up header for ChatGPTcondensedoutput.txt file
    with open(condensedoutputtext, "a", encoding='utf-8') as file:
        # Write the output to the file
            file.write("Llama Condensed Output: Abstract Index, Llama Result, Original Result")
            file.write("\n")
            #Set up header for ChatGPTcondensedoutput.txt file
    with open(criteriaoutputtext, "a", encoding='utf-8') as file:
        # Write the output to the file
            file.write("Llama Criteria Output: Abstract Index, Llama Overall Result, Llama Criteria Result 1, Llama Criteria Result 2 ...")
            file.write("\n")

#Function to see if the first sentence of text contains "not"
# def first_sentence_contains_not(text):
#     # Split the text into sentences using regular expression
#     sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
#     first_sentence = sentences[0] if sentences else ''
#     return 'not' in first_sentence.split()

#Function to add 1's and 0's if there are yes's or no's
def yes_no_to_binary(s: str) -> list[int]:
    # Split the string into words
    translator = str.maketrans('', '', string.punctuation)
    s = s.translate(translator)
    words = s.lower().split()
    # Initialize an empty list to store the results
    result = []
    
    # Loop through the words and append 1 for 'yes' and 0 for 'no'
    for word in words:
        if word == 'yes':
            result.append(1)
        elif word == 'no':
            result.append(0)
            
    return result
#Function to store the original researcher inclusion or exculsion of abstract
labels = []
with open(inputtext, 'r', encoding='utf-8') as file:
    for line in file:
        if "Label Included: 0" in line:
            labels.append(0)
        elif "Label Included: 1" in line:
            labels.append(1)

# Get all indices of desired number
inclusion_indices = [index for index, value in enumerate(labels) if value == inclusionvalue]

#If user designated sample as random, set abstractindicies to sampled_indicies
if sampletype == "random":
    # Check if we have at least the sample size
    if len(inclusion_indices) < samplesize:
        print(f"There are fewer than {samplesize} {inclusion_indices} in the list.")
    else:
        # Sample indices
        sampled_indices = random.sample(inclusion_indices, samplesize)
        sampled_indices.sort()
        print(sampled_indices)
        print(len(inclusion_indices))
        abstractindices = [x+1 for x in sampled_indices]

# Open the file to read its contents and parse out the abstract text file into individual abstracts
with open(inputtext, 'r', encoding='utf-8') as file:
    data = file.read()

#Establish pattern for every piece of text between "Title:" and "Label Included"
pattern = re.compile(r'(Title:.*?)(?=Label Included:)', re.DOTALL)
matches = pattern.findall(data)
texts = [match.strip() for match in matches]

# Get the abstracts in the specified range from abstractstart to abstractend  
abstracts = [texts[i-1] for i in abstractindices]

# Print the abstracts
# for i, text in enumerate(abstracts):
#     print(f"Text {abstractindices[i]}: {text}\n")

start_time = time.time()

#Feed in abstracts into Llama
for i, text in enumerate(abstracts):
  
  #Create and output prompt for abstract
  abstract = abstracts[i]
  fullprompt = baseprompt + "\nHere is the eligibility criteria: " + eligibility_criteria + "\nHere is the abstract: " + abstract
  print(fullprompt)

  #Generate Response from Llama

  input = {
    "prompt": fullprompt,
    "prompt_template": "<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\nYou are a helpful assistant<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n",
    "temperature": 0
  }
  output = replicate.run(
    "meta/meta-llama-3-70b-instruct",
    input=input
  )
  #The meta/llama-3-70b-chat model can stream output as it's running.
  #The predict method returns an iterator, and you can iterate over that output.
  #   for item in output:
  #     print(item)
  response = "".join(output)
  print(response)
  
  #Boolean Variable to Store If Abstract Meets Criteria
  criterialist = yes_no_to_binary(response)
  print(criterialist)

  #Print if Abstract Meets Criteria
  if criterialist[0]==1:
      criteriaoutcome = 1
      print("Meets Criteria")
  else:
      criteriaoutcome = 0
      print("Does Not Meet Criteria")

  #Write abstract and responses to output text file"
  with open(outputtext, "a", encoding='utf-8') as file:
        # Write the output to the file
        file.write("\n"+f"--- Abstract {abstractindices[i]} ---"+"\n")
        file.write("\n")
        file.write(abstract)
        file.write("\n")
        file.write("\n"+ f"--- Response {abstractindices[i]} ---"+"\n")
        file.write(response + "\n")
  
  #Write 1 or 0 If Abstract Meets Criteria
  with open(condensedoutputtext, "a", encoding='utf-8') as file:
       # Write the output to the file
        file.write(f"{abstractindices[i]}, " + str(criteriaoutcome) + ", " + str(labels[abstractindices[i]-1]))
        file.write("\n")

  #Write 1 or 0 For Each Criteria
  converted_criterialist = map(str, criterialist[0:numofcriteria+1])
  result_criterialist = ', '.join(converted_criterialist)
  with open(criteriaoutputtext, "a", encoding='utf-8') as file:
       # Write the output to the file
        file.write(f"{abstractindices[i]}, " + result_criterialist)
        file.write("\n")
  #Pause to delay submitting requests
  time.sleep(sleeptime)

end_time = time.time()
elapsed_time = (end_time - start_time)/60

converted_abstractlist = map(str,abstractindices)
result_abstractlist = ', '.join(converted_abstractlist)

print("Elapsed Time in Minutes: " + str(elapsed_time) )
print("Abstract List: [" + str(result_abstractlist) + "]")

with open(outputtext, "a", encoding='utf-8') as file:
    file.write("Elapsed Time in Minutes: " + str(elapsed_time) + "\n")
    file.write("Abstract List: [" + str(result_abstractlist) + "]" + "\n")
    file.write("Prompt Template: " + "\n" + fullprompt)