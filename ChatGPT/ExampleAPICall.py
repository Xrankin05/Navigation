from ChatGPT.AIAPI import AIAPI

"""
1. Set OpenAI API key as ENV variable.
2. You are able to customize an object that ChatGPT returns.
3. Returns sample Business object with two attributes. name and address as Strings.
"""

def callCustomObject():
    apiResponse = ai.getCustomAPIResponse()

    if apiResponse is None:
        print('API Call Failed\n Exiting ...')
        exit()
    else:
        response = ai.parse_custom_api_response(apiResponse)
        directionObject = response.dirs
        startPos = directionObject.start
        destinationPos = directionObject.destination

def callStandardAPI():
    apiResponse = ai.getAPIResponse()

    if apiResponse is None:
        print('API Call Failed\n Exiting ...')
        exit()
    else:
        print(f'ChatGPT Response\n--------------------{apiResponse}--------------------')

if __name__ == "__main__":
    ai = AIAPI()

    # callStandardAPI()

    # callCustomObject()
