from ChatGPT.AIAPI import AIAPI

"""
1. Set OpenAI API key as ENV variable.
2. You are able to customize an object that ChatGPT returns.
3. Returns sample direction object with two attributes. Start and destination as Strings.
"""

if __name__ == "__main__":
    ai = AIAPI()
    apiResponse = ai.getAPIResponse()

    if apiResponse is None:
        print("There was a server error! Sorry, see you soon!")
        exit()
    else:
        response = ai.parse_api_response(apiResponse)
        directionObject = response.dirs
        startPos = directionObject.start
        destinationPos = directionObject.destination
