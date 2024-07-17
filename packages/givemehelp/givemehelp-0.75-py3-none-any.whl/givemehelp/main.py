import openai
import subprocess
import requests
import google.generativeai as genai
import spacy
import sys
from jsonschema import validate



def retreiveSecretKey():
    schema = {
        "type": "object",
        "properties": {
            "openAIsecret": {
            "type": "string",
            "minLength": 56,
            "maxLength": 56
            },
            "geminiAIsk": {
            "type": "string",
            "minLength": 39,
            "maxLength": 39    
            }
        },
        "required": ["openAIsecret", "geminiAIsk"]
    }


    if len(sys.argv) != 3:
        print("Command to use: givemehelp <interpreter> <path_to_program>")#
    else:
        response = requests.get("https://rgwge4ffdqvnmylps4jm3ybbkq0togzi.lambda-url.eu-west-2.on.aws/")
        response_payload = response.json()
        try:
            validate(instance=response_payload, schema=schema)
        except:
            print("Validation error occured")

        openAIsecret = response_payload.get("openAIsecret")
        geminiAIsecret = response_payload.get("geminiAIsk")
        run_program(sys.argv[1], sys.argv[2],openAIsecret,geminiAIsecret)


def genAIErrorMessage(error_message,openAIsecret,geminiAIsecret):
    ## Open AI response
    openai.api_key = openAIsecret
    chat_complete = openai.ChatCompletion.create(model="gpt-3.5-turbo",messages=[{"role":"user","content":(error_message)}])
    openAIresponse = chat_complete.choices[0].message.content

    ## Google Gemini response
    genai.configure(api_key=geminiAIsecret)
    model = genai.GenerativeModel('gemini-1.5-flash')
    query = error_message
    response = model.generate_content(query)
    geminiresponse = response.text

    viewErrormessages(geminiresponse, openAIresponse)


def viewErrormessages(geminiresponse, openAIresponse):    
    # Similarity calculator
    nlp = spacy.load('en_core_web_md')
    doc1 = nlp(' '.join(openAIresponse))
    doc2 = nlp(' '.join(geminiresponse))
    print("The similarity between the responses are ",doc1.similarity(doc2))
    print("1 - Open AI")
    print("2 - Google Gemini")
    print("3 - All")
    selection = input("Which reponse would you like to view? ")
    if selection == "1":
        print("###########  Open AI  ###########")
        print(openAIresponse)
    if selection == "2":
        print("###########  Google Gemini  ########### ")
        print(geminiresponse)
    if selection == "3":
        print("###########  Open AI  ###########")
        print(openAIresponse)
        print(" ")
        print(" ")
        print("###########  Google Gemini ###########")
        print(geminiresponse)

    
def run_program(interpreter, file_path,openAIsecret,geminiAIsecret):
    try:
        result = subprocess.run(
            [interpreter, file_path],
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            genAIErrorMessage(result.stderr,openAIsecret,geminiAIsecret)
        else:
            print("Program output:")
            print(result.stdout)

    except Exception as e:
        print(f"An exception occurred: {e}")
