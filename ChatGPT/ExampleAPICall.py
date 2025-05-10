from ChatGPT.AIAPI import AIAPI

"""
1. Set OpenAI API key as ENV variable.
2. To interact with ChatGPT. You must specify its role.
3. Set both a system and user message in the AIAPI.py to direct your desired response.
4. Run this file to observe results.

*** Functions getCustomAPIResponse & parse_custom_api_response are used for the custom object which we aren't using at the moment, and simply just want text. ***

EXAMPLE SYSTEM MESSAGE
You are a navigational assistant based in Manhattan, New York. Tailored towards people in wheelchairs.
You are given steps regarding a path.
Output turn-by-turn navigation instructions.

EXAMPLE USER MESSAGE
Route Details : {Pass in the path information details}
"""

# def callCustomObject(ai):
#     apiResponse = ai.getCustomAPIResponse()
#
#     if apiResponse is None:
#         print('API Call Failed\n Exiting ...')
#         exit()
#     else:
#         # Parse the api response into our desired object
#         response = ai.parse_custom_api_response(apiResponse)
#         directionObject = response.dirs
#         startPos = directionObject.start
#         destinationPos = directionObject.destination

def callStandardAPI(ai):
    apiResponse = ai.getAPIResponse()

    if apiResponse is None:
        # Exceptions are printed through the AIAPI to diagnose issues.
        print('API Call Failed\n Exiting ...')
        exit()
    else:
        print(f'ChatGPT Response\n--------------------\n{apiResponse}\n--------------------')

if __name__ == "__main__":
    ai = AIAPI()

    callStandardAPI(ai)

    # callCustomObject()
