import requests, json, traceback
from flask import request
import loggerutility as logger
import commonutility as common
import os
from openai import OpenAI

class Insight:
    userId = ""
    def getCompletionEndpoint(self):
        try:
            jsonData = request.get_data('jsonData', None)
            jsonData = json.loads(jsonData[9:])
            logger.log(f"\njsonData openAI class::: {jsonData}","0")

            licenseKey      = jsonData['license_key']
            insightInput    = jsonData['insight_input']
            enterpriseName  = jsonData['enterprise']  
            
            if 'userId' in jsonData.keys():
                self.userId = jsonData['userId'] 

            fileName        = enterpriseName + "_insightData.txt"
            client = OpenAI(
                                api_key = licenseKey 
                            )
            
            logger.log(f"\n\njsonData openAI class fileName::: \t{fileName}\n","0")
            
            if os.path.exists(fileName):
                openAI_trainingData = open(fileName,"r").read()
            else:
                openAI_trainingData = open("insightData.txt","r").read()
            
            logger.log(f"\n\nopenAI_trainingData before conversion :::::: {type(openAI_trainingData)} \n{openAI_trainingData}\n","0")
            openAI_trainingData = openAI_trainingData.replace("<insight_input>", insightInput)
            logger.log(f"\n\nopenAI_trainingData after replacing <insight_input> :::::: \n{openAI_trainingData} \n{type(openAI_trainingData)}","0")
            messageList = json.loads(openAI_trainingData)
            logger.log(f"\n\nmessageList after conversion :::::: {messageList} \n{type(messageList)}","0")
            
            logger.log(f"\n\nfinal messageList :::::: {messageList}","0")

            if self.userId and self.userId != "":
                response = client.chat.completions.create(
                                                            model="gpt-3.5-turbo",
                                                            messages= messageList,
                                                            temperature=0.25,
                                                            max_tokens=350,
                                                            top_p=0.5,
                                                            frequency_penalty=0,
                                                            presence_penalty=0,
                                                            user=self.userId,
                                                            )
            else:
                response = client.chat.completions.create(
                                                         	model="gpt-3.5-turbo",
                                                        	messages= messageList,
                                                        	temperature=0.25,
                                                        	max_tokens=350,
                                                        	top_p=0.5,
                                                        	frequency_penalty=0,
                                                        	presence_penalty=0,
                                                    		)
            logger.log(f"\n\nResponse openAI ChatCompletion endpoint::::: {response} \n{type(response)}","0")
            finalResult=str(response.choices[0].message.content)
            logger.log(f"\n\nOpenAI ChatCompletion endpoint finalResult ::::: {finalResult} \n{type(finalResult)}","0")
            return finalResult
        
        except Exception as e:
            logger.log(f'\n In getCompletionEndpoint exception stacktrace : ', "1")
            trace = traceback.format_exc()
            descr = str(e)
            returnErr = common.getErrorXml(descr, trace)
            logger.log(f'\n Print exception returnSring inside getCompletionEndpoint : {returnErr}', "0")
            return str(returnErr)
