#####Settings and Dependencies#####
#Ensure all dependencies are installed
import openai
from openai import OpenAI
import re
import time
import random

#Abstract ID Range  
abstractindices =   [5, 19, 20, 49, 51, 83, 109, 115, 168, 173, 219, 314, 337, 345, 381, 397, 411, 415, 447, 448, 460, 463, 476, 483, 511, 516, 521, 522, 528, 534, 540, 545, 564, 581, 584, 595, 601, 613, 627, 647, 680, 694, 699, 747, 758, 768, 791, 803, 804, 866, 877, 888, 898, 903, 905, 912, 924, 977, 992, 1002, 1017, 1037, 1053, 1059, 1061, 1096, 1105, 1111, 1118, 1126, 1145, 1166, 1180, 1189, 1208, 1219, 1222, 1223, 1225, 1244, 1255, 1256, 1275, 1279, 1287, 1307, 1321, 1322, 1347, 1349, 1364, 1367, 1376, 1396, 1397, 1415, 1453, 1462, 1463, 1467]
#For random sample, set sampletype to "random" for random sample and specify parameters
sampletype = "mrandom"
samplesize = 32
inclusionvalue = 1

#Clear Output Files? Type "Yes" to clear output files
clearoutput = "Yes"

#Input and Output Abstract Text Files, Ensure that Abstracts are Separated with "Parsing Key"
inputtext = r"AbstractTexts\Bannach-Brown_2019.txt"
outputtext = r"ChatGPToutput.txt"
condensedoutputtext = r"ChatGPTcondensedoutput.txt"
criteriaoutputtext =  r"ChatGPTcriteriaoutput.txt"

#Base Prompt to Ask ChatGPT to Screen Literature Based on Specified Eligiblity Criteria"
with open('baseprompt.txt', encoding = "utf-8") as f:
    baseprompt = f.read()
with open("eligibilitycriteria.txt", encoding = "utf-8") as f:
    eligibility_criteria = f.read()
numofcriteria = 9

#Intialize API Key"
openai.api_key = ""

#Initialize Time in Seconds to Wait in Between ChatGPT Queries to Meet OpenAI's Token Usage Limit
sleeptime = 1

#ChatGPT Query Settings
temperature = 0
max_tokens = 1000
top_p = 1
frequency_penalty = 0
presence_penalty = 0
  

#####Do not modify the rest of the script#####
#Initialize Token Counts and Criteria Outcome (1 for Meets Criteria, 0 for Does Not Meet)
prompttokensused = 0
completiontokensused = 0
totaltokensused = 0
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
            file.write("ChatGPT Full Output: Abstract, Response")
            file.write("\n")
    #Set up header for ChatGPTcondensedoutput.txt file
    with open(condensedoutputtext, "a", encoding='utf-8') as file:
        # Write the output to the file
            file.write("ChatGPT Condensed Output: Abstract Index, ChatGPT Result, Original Result")
            file.write("\n")
            #Set up header for ChatGPTcondensedoutput.txt file
    with open(criteriaoutputtext, "a", encoding='utf-8') as file:
        # Write the output to the file
            file.write("ChatGPT Criteria Output: Abstract Index, ChatGPT Overall Result, ChatGPT Criteria Result 1, ChatGPT Criteria Result 2 ...")
            file.write("\n")

#Function to add 1's and 0's if there are yes's or no's
def yes_no_to_binary(s: str) -> list[int]:
    # Split the string into words
    words = s.split()
    # Initialize an empty list to store the results
    result = [] 
    # Loop through the words and append 1 for 'yes' and 0 for 'no'
    for word in words:
        if word == 'Yes':
            result.append(1)
        elif word == 'No':
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

client = OpenAI(
    organization='',
    project='',
    api_key= '')

#Feed in abstracts into ChatGPT
for i, text in enumerate(abstracts):
  
  #Create and output prompt for abstract
  abstract = abstracts[i]

  fullprompt = baseprompt + "\nHere is the eligibility criteria:\n" + eligibility_criteria + "\nHere is the abstract:\n" + abstract
  print(fullprompt)

  #Generate Response from OpenAI ChatGPT
  response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
      {
        "role": "user",
        "content": fullprompt
        }
      ],
    temperature=temperature,
    max_tokens= int(max_tokens),
    top_p=top_p,
    frequency_penalty=frequency_penalty,
    presence_penalty=presence_penalty,
    stream=False
  ) 

  #Print ChatGPT Output
  print(response)
  print(response.choices[0].message.content)

  #Boolean Variable to Store If Abstract Meets Criteria
  criterialist = yes_no_to_binary(response.choices[0].message.content)
  
  #Print if Abstract Meets Criteria
  if criterialist[0]==1:
      criteriaoutcome = 1
      print("Meets Criteria")
  else:
      criteriaoutcome = 0
      print("Does Not Meet Criteria")

  #Keep track of total tokens used
  prompttokensused += response.usage.prompt_tokens
  completiontokensused += response.usage.completion_tokens
  totaltokensused += response.usage.total_tokens
  
  #Write abstract and responses to output text file"
  with open(outputtext, "a", encoding='utf-8') as file:
        # Write the output to the file
        file.write("\n"+f"--- Abstract {abstractindices[i]} ---"+"\n")
        file.write("\n")
        file.write(abstract)
        file.write("\n")
        file.write("\n"+ f"--- Response {abstractindices[i]} ---"+"\n")
        file.write(response.choices[0].message.content +"\n")
  
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

  #Pause to delay submitting requests to OpenAI"
  time.sleep(sleeptime)

  print(criterialist)

end_time = time.time()
elapsed_time = (end_time - start_time)/60

converted_abstractlist = map(str,abstractindices)
result_abstractlist = ', '.join(converted_abstractlist)

print("Total Prompt Tokens Used: " + str(prompttokensused))
print("Total Completion Tokens Used: " + str(completiontokensused))
print("Total Tokens Used: " + str(totaltokensused))
print("Elapsed Time in Minutes: " + str(elapsed_time) )
print("Abstract List: [" + str(result_abstractlist) + "]")

with open(outputtext, "a", encoding='utf-8') as file:
    file.write("\nTotal Prompt Tokens Used: " + str(prompttokensused) + "\n")
    file.write("Total Completion Tokens Used: " + str(completiontokensused) + "\n")
    file.write("Total Tokens Used: " + str(totaltokensused) + "\n")
    file.write("Elapsed Time in Minutes: " + str(elapsed_time) + "\n")
    file.write("Abstract List: [" + str(result_abstractlist) + "]" + "\n")
    file.write("Prompt Template: " + "\n" + fullprompt)