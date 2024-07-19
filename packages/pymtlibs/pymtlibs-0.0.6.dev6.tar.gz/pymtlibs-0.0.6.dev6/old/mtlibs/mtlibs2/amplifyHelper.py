
import boto3
from gql import gql, Client
# from gql.transport.aiohttp import AIOHTTPTransport
import time
import datetime
import json
from pathlib import Path

import logging
logger = logging.getLogger(__name__)


amplifybackent_client = boto3.client('amplifybackend')

backupDir = Path('xxbackup/')

def datetimeconverter(o):
    if isinstance(o, datetime.datetime):
        return str(o)


class AmplifyApp():
    def __init__(self, appId, appEnvName):
        self.appId = appId
        self.appEnvName = appEnvName

        backend_response = amplifybackent_client.get_backend(AppId=self.appId, BackendEnvironmentName=self.appEnvName)
        self.amplifyMetaConfig = json.loads(backend_response['AmplifyMetaConfig'])

        [(k, v)] = self.amplifyMetaConfig["storage"].items()
        output = v["output"]
        self.bucketName = output["BucketName"]
        
        [(k, v)] = self.amplifyMetaConfig["auth"].items()
        self.userPoolId = v['output']['UserPoolId']
        self.cognito_idp_client = boto3.client('cognito-idp')

        self.session = boto3.Session(
            # aws_access_key_id='<your_access_key_id>',
            # aws_secret_access_key='<your_secret_access_key>'
        )
        self.s3 = self.session.resource('s3')
        self.bucket  = self.s3.Bucket(self.bucketName)


    def debug_showAmplifyAppInfo(self):
        """显示"""
        backend_response = amplifybackent_client.get_backend(AppId=self.appId, BackendEnvironmentName=self.appEnvName)

        self.amplifyMetaConfig = json.loads(backend_response['AmplifyMetaConfig'])
        # print(self.amplifyMetaConfig)

    async def s3_put_object(self,key,content):
        object = self.s3.Object(self.bucketName, key)
        return object.put(Body=content)
 

    def getGraphqlApiEndPoint(self):
        backend_response = amplifybackent_client.get_backend(AppId=self.appId, BackendEnvironmentName=self.appEnvName)
        amplifyMetaConfig = json.loads(backend_response['AmplifyMetaConfig'])
        graphqlApi = [v for key, v in amplifyMetaConfig['api'].items() if v["service"] == "AppSync"][:1]

        # 获取 graphql url 和 apikey
        return {
            "GraphQLAPIEndpointOutput": graphqlApi[0]['output']['GraphQLAPIEndpointOutput'],
            "GraphQLAPIKeyOutput": graphqlApi[0]['output']['GraphQLAPIKeyOutput'],
            "GraphQLAPIIdOutput": graphqlApi[0]['output']['GraphQLAPIIdOutput'],

        }

    async def graphqlQuery(self, query):
        graphqlApiOutput = self.getGraphqlApiEndPoint()
        transport = AIOHTTPTransport(url=graphqlApiOutput["GraphQLAPIEndpointOutput"],
                                     headers={
            "x-api-key": graphqlApiOutput["GraphQLAPIKeyOutput"]
        })
        async with Client(
            transport=transport,
            fetch_schema_from_transport=True,
        ) as session:
            query = gql(query)
            return await session.execute(query)

    async def _listStorageKeys(self):
        """
            试验：列出 s3中的文件。
        """
        [(k, v)] = self.amplifyMetaConfig["storage"].items()
        output = v["output"]
        bucketName = output["BucketName"]
        Region = output["Region"]

        s3 = boto3.resource('s3')
        bucket = s3.Bucket(bucketName)
        for obj in bucket.objects.all():
            print(obj.key)
        # print(bucketName,Region)

    async def export_ddb(self):
        """ 导出数据库到s3"""
        graphqlApiOutput = self.getGraphqlApiEndPoint()
        apiId = graphqlApiOutput["GraphQLAPIIdOutput"]
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        tables = list(dynamodb.tables.all())
        appTables = [v for v in tables if v.name.endswith(f"-{apiId}-{self.appEnvName}")]

        logger.info(f"准备备份数据库到{self.bucketName}")
        for table in appTables:
            if table.item_count <= 0:
                print(f"无数据，跳过备份 {table.name}")
            else:
                print("准备备份：{table.name}-count:{table.item_count}")
                # print(appTables)
                response = table.scan()
                data = response['Items']

                while 'LastEvaluatedKey' in response:
                    response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                    data.extend(response['Items'])

                strData=time.strftime("%Y%m%d")
                  
                tableName2=table.name[:-len(f"-{apiId}-{self.appEnvName}")]
                s3key = f"{backupDir}/ddb/{strData}/{tableName2}"
                content = json.dumps(data,indent=2)
                await self.s3_put_object(s3key,content)
                logger.info(f"完成：size:{len(content)},{s3key}")

    async def import_ddb(self):
        """从s3导入数据库"""
        # response = self.s3.list_objects_v2(Bucket=self.bucketName, Prefix= f"{backupDir}/ddb/")
        s3Objects = self.bucket.objects.filter(Prefix=f"{backupDir}/ddb/")
        # s3Objects = self.bucket.objects.all()
        for object in s3Objects:
            srcKey = object.key
            logger.info(f"key:{object.key}")

    async def _list_cognito_users(self, next_pagination_token='', Limit=60):
        [(k, v)] = self.amplifyMetaConfig["auth"].items()
        userPoolId = v['output']['UserPoolId']
        AppClientIDWeb = v['output']['AppClientIDWeb']
        appClientID = v['output']['AppClientID']
        identityPoolId = v['output']['IdentityPoolId']

        # cognito_idp_client = boto3.client('cognito-idp')
        # userPoolId = v['output']['UserPoolId']
        response = self.cognito_idp_client.list_users(
            UserPoolId=userPoolId,
            #AttributesToGet = ['name'],
            Limit=Limit,
            PaginationToken=next_pagination_token
        ) if next_pagination_token else self.cognito_idp_client.list_users(
            UserPoolId=userPoolId,
            #AttributesToGet = ['name'],
            Limit=Limit
        )
        return response["Users"]

    def addUser(self, username, password, userAttributes):
        # sub 不能设置
        _userAttributes = [v for v in userAttributes if v["Name"] != "sub"]
        response = self.cognito_idp_client.admin_create_user(
            UserPoolId=self.userPoolId,
            Username=username,
            UserAttributes=_userAttributes,
            # ValidationData=[
            #     {
            #         'Name': 'string',
            #         'Value': 'string'
            #     },
            # ],
            TemporaryPassword='888888abc',
            ForceAliasCreation=False,
            # MessageAction='RESEND'|'SUPPRESS',
            # DesiredDeliveryMediums=[
            #     'EMAIL',
            # ],
            # ClientMetadata={
            #     'string': 'string'
            # }
        )
        response2 = self.cognito_idp_client.admin_set_user_password(
            UserPoolId=self.userPoolId,
            Username=username,
            Password=password,
            Permanent=True
        )

    async def getUser(self, username: str):
        # cognito_idp_client = boto3.client('cognito-idp')
        try:
            response = self.cognito_idp_client.admin_get_user(
                UserPoolId=self.userPoolId,
                Username=username
            )
            return response
        except self.cognito_idp_client.exceptions.UserNotFoundException as e:
            return None

    # async def userExists(self, username:str) -> bool:
    #     user = await self.getUser(username)
    #     # print(user)
    #     return user.get("Username",None)

    def datetimeconverter(o):
        if isinstance(o, datetime.datetime):
            return str(o)

    async def export_users(self):
        """
            导出用户，目前测试阶段，仅处理第一页
        """
        [(k, v)] = self.amplifyMetaConfig["auth"].items()
        userPoolId = v['output']['UserPoolId']
        users = await self._list_cognito_users()
        jsonStr = json.dumps(users, indent=4, default=datetimeconverter)
        # 导出到本机文件
        exportTo = Path(backupDir).joinpath(userPoolId, "user.export.json")
        # Path(exportTo).parent.mkdir(exist_ok=True)
        # with open(exportTo, 'w') as f:
        #     f.write(jsonStr)

        # 导出到amplify自带的s3存储
        s3Key = str(exportTo)
        logger.info(f"total users: {len(users)},  backup file size: {len(jsonStr)}, \nexport to: {s3Key}")
        await self.s3_put_object(s3Key,jsonStr)


    async def import_users(self):
        """
            导入用户，目前测试阶段，仅处理第一页
        """
        [(k, v)] = self.amplifyMetaConfig["auth"].items()
        userPoolId = v['output']['UserPoolId']
        file = Path(backupDir).joinpath(userPoolId, "user.export.json")
        with open(file, 'r') as f:
            userlist = json.loads(f.read())
            for u in userlist:
                username = u["Username"]
                if await self.getUser(username):
                    logger.info("用户存在，跳过导入")
                else:
                    logger.info("导入用户 %s" % u["Username"])
                    password = "feihuo321"
                    userAttributes = u["Attributes"]
                    self.addUser(username, password, userAttributes)

    async def export_all(self):
        """
            导出所有数据到s3中，（目前仅包含数据库和用户资料。）
        """
        logger.info("☀️开始导出用户资料")
        await self.export_users()
        logger.info("☀️开始导出数据库")
        await self.export_ddb()
