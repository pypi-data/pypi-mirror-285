import requests
from reds_simple_logger import Logger
logger = Logger()

cara_base_url = "https://cara.twinklerealm.net"

class CaraAPI:
    def __init__(self, api_key):
        self.api_key = api_key

    class ChatFilterResponse:
        def __init__(self, response):
            chatfilter_response_int = response["item1"]
            chatfilter_response_reason = None
            if chatfilter_response_int != 0:
                if chatfilter_response_int == 1:
                    chatfilter_response_reason: str = "1: Bad Word"
                elif chatfilter_response_int == 2 or chatfilter_response_int == 3:
                    chatfilter_response_reason: str = "2: Hidden Badword"
                elif chatfilter_response_int == 4:
                    chatfilter_response_reason: str = "4: NSFW Content"
                elif chatfilter_response_int == 5:
                    chatfilter_response_reason: str = "5: Registered Spam Message"
                elif chatfilter_response_int == 6:
                    chatfilter_response_reason: str = "6: User was flagged for suspicious activity"
                elif chatfilter_response_int == 7:
                    chatfilter_response_reason: str = "7: Bot activity"
                #elif chatfilter_response_int == 8:
                #    chatfilter_response_reason: str = "8: Registered spammer"
                elif chatfilter_response_int == 9:
                    chatfilter_response_reason: str = "9: Forbidden Letter"
            

            self.result: int = response["item1"]
            self.reason: str = chatfilter_response_reason
            self.messageID: int = response["item2"]["messageID"]
            self.analysisSteps: str = response["item2"]["analysisSteps"]
            self.markedAsSpam: bool = response["item2"]["markedAsSpam"]
            self.levenshteinPair: str = response["item2"]["levenshteinPair"]
            self.json: str = response

    def chatfilter(self, message: str, levenshtein: int, FilteredWords, GuildID:int, ChannelID: int, AuthorID: int,
                   MessageID: int, GuildName: str, ChannelName: str, AuthorName: str, GoodWords, log:bool, OnlyASCII:bool = True, ):
        try:
            if log:
                logger.working("CaraAPI: " + "Sending request to API endpoint...")
            if OnlyASCII == True:
                OnlyASCII = "True"
            else:
                OnlyASCII = "False"
            if log:
                logger.waiting("CaraAPI: " + "Waiting for response from endpoint...")

                logger.info("CaraAPI: " + str(self.api_key))
                logger.info("CaraAPI: " + str(message))
                logger.info("CaraAPI: " + str(levenshtein))
                logger.info("CaraAPI: " + str(";".join(FilteredWords)))
                logger.info("CaraAPI: " + str(";".join(GoodWords)))
                logger.info("CaraAPI: " + str(GuildID))
                logger.info("CaraAPI: " + str(ChannelID))
                logger.info("CaraAPI: " + str(AuthorID))
                logger.info("CaraAPI: " + str(MessageID))
                logger.info("CaraAPI: " + str(GuildName))
                logger.info("CaraAPI: " + str(ChannelName))
                logger.info("CaraAPI: " + str(AuthorName))
                logger.info("CaraAPI: " + str(OnlyASCII))
            response = requests.get(
                    f'{cara_base_url}/api/ChatfilterAPI/msg',
                    params={
                        "key": str(self.api_key),
                        "content": str(message),
                        "levenshtein": str(levenshtein),
                        "FilteredWords": str(";".join(FilteredWords)),
                        "GoodWords": str(";".join(GoodWords)),
                        "GuildID": str(GuildID),
                        "ChannelID": str(ChannelID),
                        "AuthorID": str(AuthorID),
                        "MessageID": str(MessageID),
                        "GuildName": str(GuildName),
                        "ChannelName": str(ChannelName),
                        "AuthorName": str(AuthorName),
                        "OnlyASCII": str(OnlyASCII)
                    }
                )
            if response.status_code != 200:
                logger.error("CaraAPI : " + str(response.status_code))
                logger.error("CaraAPI MESSAGE: " + response.text())
                return
            response_json = response.json()
            return self.ChatFilterResponse(response_json)
        except Exception as e:
            logger.error("CaraAPI: " + "Error prossessing request: " + str(e))


    class UserResponse:
        def __init__(self, response):
            self.user_name:str = response["displayName"]
            self.isSpammer:bool = response["isSpammer"]
            self.reason:str = response["spamDetails"]["reason"]

    def get_user(self, user_id: int):
        try:
            response = requests.get(f"{cara_base_url}/api/UserAPI/user",
                                    params={
                                        "key": str(self.api_key),
                                        "UserID": str(user_id)
                                    })
            if response.status_code != 200:
                logger.error("CaraAPI: " + str(response.status_code) +";   " + response.text())
                return
            response_json = response.json()
            return self.UserResponse(response=response_json)
            

        except Exception as e:
            logger.error("CARA API: " + str(e))

    
