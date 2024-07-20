import weaviate
import json, os
import pandas as pd
import traceback
import datetime
from flask import request
import loggerutility as logger
import commonutility as common
from weaviate.gql.get import HybridFusion
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.retrievers.weaviate_hybrid_search import WeaviateHybridSearchRetriever
from langchain.schema import Document
from langchain_community.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import DocArrayInMemorySearch
from langchain.indexes import VectorstoreIndexCreator
from langchain_community.embeddings import OpenAIEmbeddings
from .Extract_OCR import Extract_OCR
from pathlib import Path

class Weaviate:
    modelScope              =  "E"
    group_size              =  10000
    entity_type             =  ""
    schema_name             =  ""
    modelParameter          =  ""
    server_url              =  ""
    openAI_apiKey           =  ""
    enterpriseName          =  ""
    entity_type             =  ""
    docType_SchemaName      =  ""
    alphaValue              =  ""
    lookup_type             =  ""
    processingMethod_list   =  "" 
    file_storage_path       =  os.environ.get('de_storage_path', '/flask_downloads')

    def traindata(self, weaviate_jsondata, fileObj=""):
        try:
            logger.log(f'\n Print Weaviate start time for traning : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', "0")
            result                      = ""
            df                          = None
            columnnamelist              = []
            schemaClasslist             = []
            flag                        = ""
            propertyEmpty_flag          = "true"
            weaviate_IndexRespository   = []
            schemaName_Updated          = ""
            
            logger.log("inside Weaviate Hybrid class trainData()","0")
            logger.log(f"jsondata Weaviate Hybrid class trainData() ::: {weaviate_jsondata} ","0")

            if "openAI_apiKey" in weaviate_jsondata and weaviate_jsondata["openAI_apiKey"] != None:
                self.openAI_apiKey = weaviate_jsondata["openAI_apiKey"]           
                logger.log(f"\ntrain_Weaviate Hybrid openAI_apiKey:::\t{self.openAI_apiKey} \t{type(self.openAI_apiKey)}","0")
            
            if "modelParameter" in weaviate_jsondata and weaviate_jsondata["modelParameter"] != None:
                self.modelParameter = json.loads(weaviate_jsondata['modelParameter'])

            if "index_name" in self.modelParameter and (self.modelParameter["index_name"]).strip() != None:
                self.schema_name = (self.modelParameter["index_name"]).capitalize().replace("-","_").strip()
                logger.log(f"\ntrain_Weaviate Hybrid index_name:::\t{self.schema_name} \t{type(self.schema_name)}","0")

            elif "index_name" in weaviate_jsondata and (weaviate_jsondata["index_name"]).strip() != None:
                self.schema_name = (weaviate_jsondata["index_name"]).capitalize().replace("-","_").strip()
                logger.log(f"\ntrain_Weaviate Hybrid index_name:::\t{self.schema_name} \t{type(self.schema_name)}","0")

            if "entity_type" in self.modelParameter and (self.modelParameter["entity_type"]).strip() != None:
                self.entity_type = (self.modelParameter['entity_type']).lower().strip()
                logger.log(f'\n Tranin Weaviate vector entity_type veraible value :::  \t{self.entity_type} \t{type(self.entity_type)}')
            
            if "data_limit" in self.modelParameter and (self.modelParameter["data_limit"]).strip() != None and (self.modelParameter["data_limit"]).strip() != "":
                self.group_size = int(self.modelParameter['data_limit'])
                logger.log(f'\n Tranin Weaviate vector data_limit veraible value :::  \t{self.group_size} \t{type(self.group_size)}')

            if "modelScope" in weaviate_jsondata and weaviate_jsondata["modelScope"] != None:
                self.modelScope = weaviate_jsondata["modelScope"]
                logger.log(f"\ntrain_Weaviate class TrainData modelScope:::\t{self.modelScope} \t{type(self.modelScope)}","0")

            if "enterprise" in weaviate_jsondata and weaviate_jsondata["enterprise"] != None:
                self.enterpriseName = weaviate_jsondata["enterprise"]
                logger.log(f"\nWeaviate Hybrid class TrainData enterprise:::\t{self.enterpriseName} \t{type(self.enterpriseName)}","0")

            if "modelJsonData" in weaviate_jsondata and weaviate_jsondata["modelJsonData"] != None:
                self.dfJson = weaviate_jsondata["modelJsonData"]
            elif "dfJson" in weaviate_jsondata and weaviate_jsondata["dfJson"] != None:
                self.dfJson = weaviate_jsondata["dfJson"]
            logger.log(f"\ntrain_Weaviate Hybrid dfJson:::\t{self.dfJson} \t{type(self.dfJson)}","0")

            if type(self.dfJson) == str :
                parsed_json = json.loads(self.dfJson)
            else:
                parsed_json = self.dfJson

            if "server_url" in weaviate_jsondata and weaviate_jsondata["server_url"] != None:
                self.server_url = weaviate_jsondata["server_url"]
                logger.log(f"\nWeaviate Hybrid class TrainData server_url:::\t{self.server_url} \t{type(self.server_url)}","0")
            
            if "proc_mtd" in weaviate_jsondata and weaviate_jsondata["proc_mtd"] != None:
                self.processingMethod_list = weaviate_jsondata["proc_mtd"].split("-")
                logger.log(f"\nWeaviate Hybrid class TrainData processingMethod:::\t{self.processingMethod_list} \t{type(self.processingMethod_list)}","0")

            # Connection code with Weaviate
            client = weaviate.Client(self.server_url,additional_headers={"X-OpenAI-Api-Key": self.openAI_apiKey})

            logger.log(f'Connection is establish : {client.is_ready()}')

            if self.modelScope == "G" :
                self.enterpriseName = ""

            schemaName_Updated = self.enterpriseName + "_" + self.schema_name + "_" + self.entity_type
            logger.log(f'\nschemaName_Updated ::: \t{schemaName_Updated}')

            if self.schema_name == 'Document':

                if parsed_json[0]["description"] == "":
                    logger.log(f"OCR not avialable Case. \n Generating new OCR and then Training\n")
                    OCR_Text_json = self.get_FileOCR(fileObj)
                    logger.log(f"OCR_Text_json ::: {OCR_Text_json}\n")
                    parsed_json[0]["description"] = OCR_Text_json
                    logger.log(f"parsed_json upadted ::: {parsed_json}")

                copydict = parsed_json.copy()
                parsed_json = {"id" : 'String', "description" : 'String'}
                parsed_json.update(copydict[0]) # To add only document JSON Object 
                
                flag = self.documentTraining(client, parsed_json)
            
            else:
            # Schema Class parameter
                
                
                class_obj = {
                        "class": schemaName_Updated,
                        "vectorizer": "text2vec-openai",
                        "moduleConfig": {
                            "text2vec-openai": {},
                            "generative-openai": {}
                                        }
                            }
                # if schema is present then process should not create new one need to update
                weaviate_IndexRespository = client.schema.get()["classes"]
                schemaClasslist = [i['class'] for i in weaviate_IndexRespository]               
                
                if schemaName_Updated not in schemaClasslist:
                    client.schema.create_class(class_obj) # Schema Class Creation
                    logger.log(f"\n Schema: '{schemaName_Updated}' not present. Creating New !!!\n ")
                    
                    weaviate_IndexRespository = client.schema.get()["classes"]      # Updating variable value after new index creation
                    schemaClasslist = [i['class'] for i in weaviate_IndexRespository]  # Updating variable value after new index creation
                    logger.log(f"\nAvailable schema list::: {schemaClasslist} \n ")

                else:
                    logger.log(f"'{schemaName_Updated}' already present. Loading Now !!!\n ")
                
                for index, schemaObj in enumerate(weaviate_IndexRespository):
                    if schemaName_Updated == weaviate_IndexRespository[index]["class"]:
                        if not len(schemaObj["properties"])  > 0:
                            logger.log(f"Property empty for Weaviate Index '{schemaName_Updated}' case")
                            propertyEmpty_flag = "false"
                    else:
                        logger.log("Schema Name not present")

                if not schemaName_Updated == 'Document' :
                    if propertyEmpty_flag == "true" :
                        client.schema.delete_class(schemaName_Updated)
                        
                        # client.batch.delete_objects(class_name=schemaName_Updated
                        #                                 where={'path': ["organization"],
                        #                                     'operator': 'Equal',
                        #                                     'valueText': str(self.enterpriseName) +"_"+ str(self.entity_type)
                        #                         },
                        #                     )
                        logger.log(f'\n Schema: "{schemaName_Updated}" against records are deleted ')
                    else:
                        logger.log(f'\n {schemaName_Updated} has no filter properties. Skipping records deletion.')

                columnnamelist=list(val for val in parsed_json[0])

                num_groups = len(parsed_json[1:]) // self.group_size + (len(parsed_json[1:]) % self.group_size > 0)
                logger.log(f"num_groups ::: {type(num_groups)} {num_groups}")

                groups = []
                for i in range(num_groups):
                    start_idx = i * self.group_size
                    end_idx = (i + 1) * self.group_size if i < num_groups - 1 else len(parsed_json) 
                    logger.log(f"\n Group '{i}' \t start_idx::: {start_idx} \t end_idx ::: {end_idx}")
                    group_indices = list(range(start_idx, end_idx))
                    groups.append(group_indices)
                    logger.log(f"\n\nGroup '{i}' length::: {len(groups)}\n Total number of rows received:::  {groups}\n\n")
                
                logger.log(f'\n Number of Groups Created {len(groups)}', "0")

                logger.log(f'\n Print Weaviate Traning start time: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', "0")
                
                for val in groups:
                    with client.batch.configure(batch_size=1000) as batch:
                        logger.log(f'\n Print Weaviate Group Traning start time: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', "0")    
                        for indexvalue in val:          #  for each element of the list
                            if not indexvalue == 0:
                                properties = {
                                    "answer": parsed_json[indexvalue][columnnamelist[0]],
                                    "description": parsed_json[indexvalue][columnnamelist[1]],
                                    # "organization": str(self.enterpriseName) +"_"+ str(self.entity_type),
                                }
                                if len(columnnamelist) > 2:
                                    for j,valuedata in enumerate(columnnamelist[2:]):
                                        if valuedata not in parsed_json[indexvalue]:
                                            parsed_json[indexvalue][valuedata]=""
                                        else:
                                            properties[valuedata] = parsed_json[indexvalue][valuedata]
                                
                                client.batch.add_data_object(
                                    properties,
                                    schemaName_Updated,
                                )
                        logger.log(f'\n Print Weaviate Group Traning END time: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', "0")    
                        flag = "SUCCESSFUL"

            if flag == "SUCCESSFUL":
                result = f" {(schemaName_Updated if self.schema_name != 'Document' else self.docType_SchemaName)} Index Creation SUCCESSFUL. "
            else :
                result = f" {(schemaName_Updated if self.schema_name != 'Document' else self.docType_SchemaName)} Index Creation FAILED. "
            
            logger.log(f'\n Print Weaviate END time for traning : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', "0")
            logger.log(f" WEaviate Training final Result::: \n{result}\n ")
            return result
        except Exception as e:
            logger.log(f" {schemaName_Updated} Index Creation FAILED for Enterprise: '{self.enterpriseName}'. ","0")
            logger.log(f"{schemaName_Updated} class trainData() Issue::: \n{e}","0")
            trace = traceback.format_exc()
            descr = str(e)
            errorXml = common.getErrorXml(descr, trace)
            logger.log(f'\n {schemaName_Updated} class trainData() errorXml::: \n{errorXml}', "0")
            raise str(errorXml)
        
    def getLookupData(self):
        
        try:
            logger.log(f'\n Print Weaviate start time for getLookupData : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', "0")
            logger.log("inside Weaviate Hybrid class LookUpData()","0")
            finalResultJson     =  {}
            id_list             =  []
            queryJson           =  ""
            schemaClasslist     =  []
            lookupParam_json    =  {}
            finalResponse       =  ""
            descr               =  ""
            id                  =  ""
            inputQuery          =  ""

            weaviate_json =  request.get_data('jsonData', None)
            weaviate_json = json.loads(weaviate_json[9:])
            logger.log(f"\nWeaviate hybrid class getLookupData() weaviate_json:::\t{weaviate_json} \t{type(weaviate_json)}","0")

            if "openAI_apiKey" in weaviate_json and weaviate_json["openAI_apiKey"] != None:
                self.openAI_apiKey = weaviate_json["openAI_apiKey"]          
                logger.log(f"\nWeaviate hybrid class LookUpData() openAI_apiKey:::\t{self.openAI_apiKey} \t{type(self.openAI_apiKey)}","0")              
            
            if "queryJson" in weaviate_json and weaviate_json["queryJson"] != None:
                queryJson = weaviate_json["queryJson"]
            elif "queryList" in weaviate_json and weaviate_json["queryList"] != None:
                queryJson = weaviate_json["queryList"]   
                logger.log(f"\nWeaviate hybrid class LookUpData() queryJson:::\t{queryJson} has length ::: '{len(queryJson)}'\t{type(queryJson)}","0")
            
            if "index_name" in weaviate_json and weaviate_json["index_name"] != None:
                self.schema_name = (weaviate_json["index_name"]).capitalize().replace("-","_")
                logger.log(f"\nWeaviate hybrid class LookUpData() schema_name:::\t{self.schema_name} \t{type(self.schema_name)}","0")

            if "enterprise" in weaviate_json and weaviate_json["enterprise"] != None:
                self.enterpriseName = weaviate_json["enterprise"]
                logger.log(f"\nWeaviate hybrid class LookUpData() enterprise:::\t{self.enterpriseName} \t{type(self.enterpriseName)}","0")

            if "server_url" in weaviate_json and weaviate_json["server_url"] != None:
                self.server_url = weaviate_json["server_url"]
                logger.log(f"\nWeaviate Hybrid class LookUpData server_url:::\t{self.server_url} \t{type(self.server_url)}","0")

            if "entity_type" in weaviate_json and weaviate_json["entity_type"] != None:
                self.entity_type = (weaviate_json['entity_type']).lower()
                logger.log(f'\n Tranin Weaviate vector entity_type veraible value :::  \t{self.entity_type} \t{type(self.entity_type)}')

            if "modelScope" in weaviate_json and weaviate_json["modelScope"] != None:
                self.modelScope = weaviate_json["modelScope"]
                logger.log(f"\nWeaviate hybrid class LookUpData() modelScope:::\t{self.modelScope} \t{type(self.modelScope)}","0")

            if "lookup_parameter" in weaviate_json and weaviate_json["lookup_parameter"] != None:
                if (type(weaviate_json["lookup_parameter"])  == str) and (len(weaviate_json["lookup_parameter"]) > 0) :
                    lookupParam_json = json.loads(weaviate_json["lookup_parameter"])
                else :
                    lookupParam_json = weaviate_json["lookup_parameter"]

                if lookupParam_json != "":
                    if len(lookupParam_json["alpha"]) > 0 and type(lookupParam_json["alpha"]) == str : 
                        self.alphaValue = float(lookupParam_json["alpha"])
                    else:
                        logger.log(f"\n   Alpha value EMPTY case      \n","0") 
                else:
                    logger.log(f"lookupParam_json Blank CASE:::: {lookupParam_json} ")
                logger.log(f"\nWeaviate hybrid class LookUpData() alphaValue:::\t{self.alphaValue} \t{type(self.alphaValue)}\n","0")
            
            if self.schema_name != "Document":
                self.alphaValue = self.alphaValue if self.alphaValue != "" else 0.6
            else:
                self.alphaValue = self.alphaValue if self.alphaValue != "" else 1

            logger.log(f"\n\n Final alphaValue ::: \t{self.alphaValue}\n")

            if "lookup_type" in weaviate_json and weaviate_json["lookup_type"] != None:
                self.lookup_type = weaviate_json["lookup_type"]
                logger.log(f"self.lookup_type  :::: {self.lookup_type} ")

            if self.modelScope == "G":
                self.enterpriseName = ""
            
            # Connection code with weaviate 

            client = weaviate.Client(self.server_url,additional_headers={"X-OpenAI-Api-Key": self.openAI_apiKey})

            schemaName_Updated = self.enterpriseName + "_" + self.schema_name + "_" + self.entity_type
            logger.log(f'\nschemaName_Updated ::: \t{schemaName_Updated}')
            schemaClasslist = [i['class'] for i in client.schema.get()["classes"]]               

            logger.log(f'Connection is establish : {client.is_ready()}')

            where_filter = {
                "path": ["organization"],
                "operator": "Equal",
                "valueText": str(self.enterpriseName) +"_"+ str(self.entity_type)
                            }
            
            if self.schema_name == 'Document':
                if self.lookup_type == "S" :
                    logger.log("Lookup type 'SEARCH' CASE ")
                    finalResponse = self.documentLookup_search(client , queryJson)
                elif self.lookup_type == "Q" :
                    logger.log("Lookup type 'QUESTION-ANSWERING' CASE ")
                    finalResponse = self.documentLookup_getAnswer(client , queryJson)
                else:
                    logger.log(f'\n\n Unexpected lookup_type recieved ::: \t{self.lookup_type}\n')

                finalResult = str(finalResponse)
                
            else:
                if schemaName_Updated in schemaClasslist:
                    for key in queryJson:
                        if len(queryJson[key]) > 0 and queryJson[key].strip() != "":
                            inputQuery  = queryJson[key].upper().replace("N/A","").replace("."," ").replace(","," ").replace("-"," ").replace("_"," ")
                            response    = (
                                            client.query
                                            .get(schemaName_Updated, ["description", "answer"])     #,"organization"])
                                            # .with_where(where_filter)
                                            .with_hybrid(
                                                            alpha       =  self.alphaValue ,
                                                            query       =  inputQuery ,
                                                            fusion_type =  HybridFusion.RELATIVE_SCORE
                                                        )
                                            .with_additional('score')
                                            .with_limit(15)
                                            .do()
                                            )
                            logger.log(f"Input ::: {inputQuery} \n Responsee:::: {response}")

                            if response != {}:

                                response_List = response['data']['Get'][schemaName_Updated] 
                                finalResultJson[key]= {"material_description": response_List[0]['description'] , "id": response_List[0]['answer'] } if len(response_List) > 0 else {}

                                logger.log(f'\n START time for responseDescription-InputQuery matching  : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
                                for index in range(len(response_List)):
                                    descr               =  response_List[index]['description']
                                    id                  =  response_List[index]['answer']
                                    descr_replaced      =  descr.replace(" ", "") 
                                    inputQuery_replaced =  inputQuery.replace(" ", "")

                                    if descr_replaced == inputQuery_replaced:
                                        logger.log(f"\n Input::: '{inputQuery_replaced}' MATCHEDD with description ::: '{descr_replaced}' \n")
                                        finalResultJson[key]    =  {"material_description": descr, "id": id } 
                                        break
                                    else:
                                        logger.log(f"\n Input '{inputQuery_replaced}' not matched with returned response description '{descr_replaced} '\n ")    
                                logger.log(f'\n END time for responseDescription-InputQuery matching  : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
                                
                    logger.log(f"\n\n FinalResultJson line 390:::{finalResultJson} has length ::: '{len(finalResultJson)}' \t {type(finalResultJson)}\n")
                    finalResult = str(finalResultJson)
                else:
                    logger.log(f"Weaviate class getLookUP()::: \nIndex_Name: {schemaName_Updated} not found in weaviate_IndexList: {schemaClasslist}","0")
                    message = f"Index_Name: '{schemaName_Updated}' not found in weaviate_IndexList. \nAvailable IndexList: {schemaClasslist}"
                    errorXml = common.getErrorXml(message, "")
                    raise Exception(errorXml)

                logger.log(f'\n Print Weaviate END time for getLookupData : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', "0")
                logger.log(f'\n FINAL Result :::{finalResult}', "0")

            logger.log(f"353 Final result:::{finalResult}\n")
            return finalResult
        
        except Exception as e:
            logger.log(f"Weaviate Hybrid class getLookUP() Issue::: \n{e}","0")
            trace = traceback.format_exc()
            descr = str(e)
            errorXml = common.getErrorXml(descr, trace)
            logger.log(f'\n Weaviate hybrid class getLookUP() errorXml::: \n{errorXml}', "0")
            raise str(errorXml)

    def documentTraining(self,client, parsedJson):
        logger.log(f"\nparsed Json::: \n{parsedJson}\n\n")
        logger.log(f'Connection is establish : {client.is_ready()}')
        
        self.docType_SchemaName = self.enterpriseName + "_" + self.schema_name 
        retriever               = ""
        
        retriever = WeaviateHybridSearchRetriever(
                                                    client      = client,
                                                    index_name  = self.docType_SchemaName,
                                                    text_key    = "text",
                                                    attributes  = [],
                                                    metadata    = {"metadata":"doc_id"},
                                                    create_schema_if_missing=True,
                                                )

        OCRText = list(json.loads(parsedJson["description"]).values()) if type(parsedJson["description"]) == str else list(parsedJson["description"].values())
        logger.log(f"OCRText::: \n{OCRText}\n\n{type(OCRText)} ")

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)  # for txtFileObject
        texts = text_splitter.create_documents(OCRText)
        logger.log(f"texts - First 2 chunks::: \n{texts[:2]}\n Divided Chunks length:::\n{len(texts)} ")

        for i in range(len(texts)):
            texts[i].metadata["doc_id"] = str(parsedJson["id"]) + "__" + str(i)
        logger.log(f"\n\n--- Using Langchain approach --- \n\nTexts - Last 2 Chunks::: {texts[-2:]} {type(texts)}\n\n")

        retriever.add_documents(texts)
        logger.log(f"retriever::: {type(retriever)}\n retriever value::: \n{retriever}\n\n")
        if retriever != "":
            message = f"SUCCESSFUL"
        else:
            message = f"UNSUCCESSFUL"
        logger.log(f"Message:::\t Document training {message} for '{self.docType_SchemaName}' ")
        return message
        
    def documentLookup_search(self, client, queryJson):
        id_list             = set()
        chunkResponse_list  = set()
        docType_SchemaName  = self.enterpriseName + "_" + self.schema_name 

        retriever = WeaviateHybridSearchRetriever(
                                                    client      = client,
                                                    index_name  = docType_SchemaName,
                                                    text_key    = "text",
                                                    attributes  = ["doc_id"],
                                                    create_schema_if_missing = True,
                                                    alpha       =  self.alphaValue
                                                )
        
        for key in queryJson:
            
            if len(key) > 0 and key.strip() != "":
                logger.log(f"key::: {key}")
                response = retriever.get_relevant_documents(key)
                logger.log(f"\n\nResponse for query '{key}'::: {type(response)}\n{response}\n")

                if len(response) > 0 :
                    for result in response:
                        chunkResponse_list.add(result.page_content)
                        id_list.add(result.metadata['doc_id'])
                        
                    logger.log(f"\n\nid_list::: \t{id_list}\n\n Chunk Response::: \n{chunkResponse_list}\n\n")

                    id_list = [eachId[ : eachId.find("_")] if "_" in eachId else eachId for eachId in id_list ]
                    logger.log(f"After removing '_' id_list::: \t{id_list} {type(id_list)}")
                    id_list = list(id_list)
                    logger.log(f"After removing duplicates id_list::: \t{id_list} {type(id_list)}")
                    return id_list
    
    def documentLookup_getAnswer(self, client, queryJson):
        try:
            response        = ""
            finalJson       = {}
            doc_id_list     = []
            id_content_json = {} 
            fileName        = "document_instructions.txt"
            finalJson_list  = []

            docType_SchemaName  = self.enterpriseName + "_" + self.schema_name 

            retriever = WeaviateHybridSearchRetriever(
                                                        client      = client,
                                                        index_name  = docType_SchemaName,
                                                        text_key    = "text",
                                                        attributes  = ["doc_id"],
                                                        create_schema_if_missing = True,
                                                        alpha       =  self.alphaValue
                                                    )
            
            embeddings = OpenAIEmbeddings(openai_api_key=self.openAI_apiKey)

            for key in queryJson:
                
                if len(key) > 0 and key.strip() != "":
                    logger.log(f"key::: {key}")

                    logger.log(f'\n\n START Time Similarity Search : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n')
                    retriever = retriever.get_relevant_documents(key)               # used because weaviate vector db was unable to return required 'page_content' key directly
                    db = DocArrayInMemorySearch.from_documents(retriever, embeddings )
                    docs = db.similarity_search(key)
                    logger.log(f"Similarity serach response::: \n\n{docs}\n")       
                    logger.log(f'\n\n END Time Similarity Search : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n')

                    retriever = db.as_retriever()
                    qdocs = "".join([docs[i].page_content for i in range(len(docs))])
                    llm = ChatOpenAI(openai_api_key=self.openAI_apiKey, model_name='gpt-3.5-turbo', temperature=0)

                    with open(fileName, "r") as file :
                        doc_instruction = file.read()
                        logger.log(f"doc_instruction before::: \t{type(doc_instruction)} \n{doc_instruction}")
                        doc_instruction = doc_instruction.replace("<qdocs>", f"{qdocs}").replace("<question>",f"{key}").replace("<docs>", f"{docs}")
                        logger.log(f"doc_instruction after::: \t{type(doc_instruction)} \n{doc_instruction}")

                    logger.log(f'\n\n START Time Document QA : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n')
                    response = llm.call_as_llm(doc_instruction)
                    logger.log(f"response::: \t{type(response)}\n\n{response}\n")
                    logger.log(f'\n\n END Time Document QA : {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n')

                else : 
                    logger.log(f"\n\nEmpty Question case ::: \t'{key}'\n")

            if response != "":
                response = json.loads(response)
                logger.log(f"response after json conversion ::: \t{type(response)}\n\n{response}\n")
                
                for key,value in response.items():
                    if key == "doc_id":
                        logger.log(f"{key} case, value ::{value} ")
                        
                        if type(value) == list :
                            logger.log("'doc_id' value is of type list")
                            for index in range(len(value)):
                                logger.log(f"value index before ::: {value[index]}\n")
                                if "_" in value[index] :
                                    value[index] = value[index][ : value[index].find("_")] 
                                    logger.log(f"value index after ::: {value[index]}\n")
                                id_content_json[value[index]] = response["page_content"][index]
                        
                        elif type(value) == str:
                            logger.log("'doc_id' value is of type str")
                            if "_" in value :
                                logger.log(f"value before ::: {value}\n")
                                value = value[ : value.find("_")] 
                                logger.log(f"value after ::: {value}\n")
                                id_content_json[value] = response["page_content"]
                        
                        else:
                            logger.log("Invalid datatype for 'doc_id' ")
                                
                doc_id_list.append(id_content_json)
                
                finalJson["answer"]      = response["answer"]
                finalJson["doc_id_list"] = doc_id_list

            finalJson_list.append(finalJson)
            logger.log(f"finalJson_list::: \t{type(finalJson_list)}\n\n{finalJson_list}\n")
            return finalJson_list
        
        except Exception as e :
            logger.log(f"\n Issue::: \n{e}\n","0")
            trace = traceback.format_exc()
            descr = str(e)
            errorXml = common.getErrorXml(descr, trace)
            logger.log(f'\n Weaviate hybrid class getLookUP() errorXml::: \n{errorXml}', "0")
            raise str(errorXml)

    def get_FileOCR(self, fileObj):
        try:
            fileName = fileObj.filename                                         # extract filename from file object
            file_path = os.path.join(self.file_storage_path, fileName)
            
            Path(self.file_storage_path).mkdir(parents=True, exist_ok=True)     # Initialize directory
            fileObj.save(file_path)

            logger.log(f"\n fileName ::: \t{fileName}\n filePath ::: \t{file_path}\n File object stored successfully.")

            ext_OCR = Extract_OCR()
            OCR_Text = ext_OCR.get_OCR(file_path, self.processingMethod_list)
            logger.log(f"\nOCR_Text::: \n{OCR_Text}\n")
            return OCR_Text
        
        except Exception as e :
            logger.log(f"\n Issue::: \n{e}\n","0")
            trace = traceback.format_exc()
            descr = str(e)
            errorXml = common.getErrorXml(descr, trace)
            logger.log(f'\n Weaviate hybrid class get_FileOCR() errorXml::: \n{errorXml}', "0")
            raise str(errorXml)

