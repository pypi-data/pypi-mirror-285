import akasha
import pandas as pd
import os
import re
import json
import requests
import psycopg2
import sqlite3
import pymssql
import mysql.connector

from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Union

DEFAULT_MODEL = 'openai:gpt-4'
VERBOSE = True

def set_connection_config(sql_type:str, database:str, user:str='', password:str='', host:str='', port:str=''):
    connection_config = {}
    connection_config['SQL_TYPE'] = sql_type
    connection_config['DB_NAME'] = database
    if user:
        connection_config['DB_USER'] = user
    if password:
        connection_config['DB_PASSWORD'] = password
    if host:
        connection_config['DB_HOST'] = host
    if port:
        connection_config['DB_PORT'] = port
    return connection_config

def _get_data(sql_cmd:str, connection_config:Dict[str, str]={}) -> pd.DataFrame:
    sql_type = connection_config.get('SQL_TYPE', 'SQLITE').upper()
    database = connection_config.get('DB_NAME', 'database.db')
    user = connection_config.get('DB_USER', '')
    password = connection_config.get('DB_PASSWORD', '')
    host = connection_config.get('DB_HOST', '')
    port = connection_config.get('DB_PORT', '')
    if sql_type == 'POSTGRESQL':
        conn = psycopg2.connect(
            database=database, 
            user=user, 
            password=password, 
            host=host, 
            port=port
        ) 
    elif sql_type == 'MYSQL':
        conn = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
    elif sql_type == 'MSSQL':
        conn = pymssql.connect(
            server=f'{host}:{port}', 
            user=user, 
            password=password, 
            database=database
        )
    elif sql_type == 'SQLITE':
        conn = sqlite3.connect(database)
    else:
        raise ValueError(f'Unsupported SQL_TYPE={sql_type}')
    try:
        # Execute the SQL command and fetch the data
        df = pd.read_sql_query(sql_cmd, conn)
    finally:
        # Ensure the connection is closed
        conn.close()
    return df

def _get_table_schema(table_name:str, connection_config:Dict[str, str]={}) -> pd.DataFrame:
    sql_type = connection_config.get('SQL_TYPE', 'SQLITE').upper()
    database = connection_config.get('DB_NAME', 'database.db')
    if sql_type in ('POSTGRESQL', 'MSSQL'):
        sql = f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table_name}';"
    elif sql_type == 'MYSQL':
        sql = f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table_name}' and table_schema = '{database}';"
    elif sql_type == 'SQLITE':
        sql = f"SELECT name AS column_name, type AS data_type FROM pragma_table_info('{table_name}');"
    else:
        raise ValueError(f'Unsupported SQL_TYPE={sql_type}')
    return _get_data(sql, connection_config=connection_config)

#%% Function
def db_query_func(question: str, table_name: str, column_description_json:Union[str, dict]=None, simplified_answer:bool=False, connection_config:Dict[str,str]={}, model:str=DEFAULT_MODEL):
    ak = akasha.Doc_QA(model=model, verbose=VERBOSE)
    sql_type = connection_config.get('SQL_TYPE', 'SQLITE').upper()
    # table structure
    table_schema_df = _get_table_schema(table_name=table_name, connection_config=connection_config)
    columns = ','.join(table_schema_df['column_name'].tolist())
    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # column description
    if column_description_json is not None:
        try:
            if isinstance(column_description_json, dict):
                column_description = column_description_json
            elif isinstance(column_description_json, str): 
                if column_description_json.endswith('.json'):
                    with open(column_description_json, 'r') as f:
                        column_description = json.load(f)
                else:
                    column_description = json.loads(column_description_json)
        except Exception as e:
            print('Error:', e)
            column_description = {}
    else:
        column_description = {}
    # sample data
    ROW_LIMIT = 1
    ## row where fewest columns are null
    top_or_not = f'TOP {ROW_LIMIT}' if sql_type == 'MSSQL' else ''
    order_by_columns_fewest = 'ORDER BY (' + '+'.join([f'CASE WHEN {col} IS NULL THEN 1 ELSE 0 END' for col in table_schema_df['column_name']]) + ') ASC' if table_schema_df.shape[0] > 0 else ''
    limit_or_not = f'LIMIT {ROW_LIMIT}' if sql_type != 'MSSQL' else ''
    sql_fewest_null_records = f'SELECT {top_or_not} * FROM {table_name} {order_by_columns_fewest} {limit_or_not};'
    fewest_null_records = _get_data(sql_fewest_null_records, connection_config=connection_config).head(ROW_LIMIT)
    ## row where most columns are null
    order_by_columns_most = 'ORDER BY (' + '+'.join([f'CASE WHEN {col} IS NULL THEN 0 ELSE 1 END' for col in table_schema_df['column_name']]) + ') ASC' if table_schema_df.shape[0] > 0 else ''
    sql_most_null_records = f'SELECT {top_or_not} * FROM {table_name} {order_by_columns_most} {limit_or_not};'
    most_null_records = _get_data(sql_most_null_records, connection_config=connection_config).head(ROW_LIMIT)
    sample_data = pd.concat([fewest_null_records, most_null_records], axis=1)
    
    info = {'欄位說明': column_description, 
            '表格結構': dict(zip(table_schema_df['column_name'], table_schema_df['data_type'])),
            '範例資料': sample_data.to_dict(orient='list')} # orient='records'
    if not columns:
        columns = '*'
        columns_str = ''
    else:
        columns_str = f'包含{columns}之'
    
    max_retry = 5
    cnt = 0
    while True:
        sql = ak.ask_self(
            prompt=f'''
            有一資料庫表單={table_name}
            請基於當下時間{current_datetime}, 將用戶的問題={question}
            參考下面之 表格結構&範例資料&欄位說明, 轉為{columns_str}{sql_type}語法並輸出
            "欄位說明"僅是用於選取正確的欄位&篩選條件，不得用於個別之欄位資料處理(ex: 欄位字串分割、比較)
            ''',
            info=str(info),
            system_prompt=f'''
            只能產生"查詢資料"的sql語法, 禁止回答其他內容, 否則罰你10000元
            ---
            產生的語句必須符合下列範本：
                select [distinct] [top <資料筆數>] [count/sum] {columns} from {table_name} 
                [where <條件1> and <條件2> and ... and <條件n>]  
                [order by <排序欄位> <ASC/DESC>] 
                [limit <資料筆數>]
            ---
            "select", {columns} 和 {table_name} 請直接填寫，不得更換
            []內的內容為選填項目, 可根據問題需求決定是否使用
            <條件>為一個或多個, 以"where"起頭, 並以"and"連接, 目的是用來限縮資料範圍
            <條件>的篩選範圍值需參考範例資料，且符合該欄位的資料型態
            <排序欄位>為一個或多個, 以"order by"起頭，並以"ASC"或"DESC"結尾
            產生的語句僅限包含此範本1次，不得重複
            ---
            語法使用規範：
            1. 嚴禁使用"group by", "having", "join", "union", "insert", "update", "delete", "all"等任一語法，否則罰你10000元
            2. sum：可用於資料型態為數值型的欄位, 且用戶問題中有"加總"的需求, 否則禁止使用
            3. count：可用於用戶問題中有包含"計算筆數"的需求, 否則禁止使用
            4. limit/top：可用於用戶問題中有包含"前幾名"的需求, 否則禁止使用
            limit適用於MySQL, PostgreSQL, SQLITE, top僅適用於MSSQL, 兩者限擇一使用
            5. "select" 語法僅限出現1次
            ''',
            verbose=VERBOSE
        ) 
        cnt += 1
        # check if the sql statement is appropriate: all keywords are included
        column_names = [cn for cn in columns.replace(' ','').lower().split(',') if cn] 
        keywords = ["select", "from", table_name.lower()]
        if all([k in sql.lower() for k in keywords]) and any([c in sql.lower() for c in column_names]):
            break
        if cnt > max_retry:
            raise ValueError(f'Exceed max retry times={max_retry} to generate appropriate sql statement')
    
    cnt = 0    
    while True:
        try:
            data = _get_data(sql, connection_config=connection_config)
            break
        except pd.errors.DatabaseError:
            # remove "group by", "having", "join", "union", "insert", "update", "delete", "all" keywords
            keywords = ["group by", "having", "join", "union", "insert", "update", "delete", "all"]
            pattern = r'\b(' + '|'.join(re.escape(keyword) for keyword in keywords) + r')\b'
            match = re.search(pattern, sql, re.IGNORECASE)
            if match:
                sql = sql[:match.start()]
            # remove "select" after the first one
            pattern = r'\bselect\b'
            matches = list(re.finditer(pattern, sql, re.IGNORECASE))
            if len(matches) >= 2:    
                sql = sql[:matches[1].start()]
            # remove other characters before "select"
            pattern = r'\bselect\b'
            match = re.search(pattern, sql, re.IGNORECASE)
            if match:
                sql = sql[match.start():]
            # remove all `
            sql = sql.replace('`', '')
        
        cnt += 1
        if cnt > max_retry:
            raise ValueError(f'Exceed max retry times={max_retry} to get data from database')
            
    answer = ak.ask_self(
        prompt=f'''
        請根據資料庫查詢的結果，回答使用者的問題
        ---
        查詢表格：{table_name}
        查詢結果：\n{data}\n
        使用者問題：{question}
        ''',
        info=str(info),
        system_prompt='''
        請直接針對用戶問題進行回答，禁止回答其他內容
        若回答之數據有經過計算過程，請詳述其計算過程
        有關數值的大小比較結果之論述，請自我檢查是否正確再輸出
        ''',
        verbose=VERBOSE
    )
    if simplified_answer:
        answer = ak.ask_self(
            prompt=f'''請根據下面論述，摘取結論\n---\n{answer}''',
            system_prompt=f'''
            請針對使用者問題：{question}
            取出結論，並以string形式回答
            禁止換句話說
            禁止回答其他內容
            禁止更換數值結果
            數據值不得省略或改為文字論述
            ---
            結論摘取要點：
            1. 排除計算過程
            2. 呈現計算結果
            ''',
            verbose=VERBOSE
        )
    return answer

def webpage_summary_func(url:str, summary_len:int=100, extract_topics:List[str]=[], list_result:bool=True, model:str=DEFAULT_MODEL):
    # parse url
    try:
        response = requests.get(url)
        response.raise_for_status()  
        soup = BeautifulSoup(response.content, 'html.parser')
        article = soup.get_text()
        
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        article = '' 
        return '' 
    
    # summarize
    hint_extract_topics = ''
    if len(extract_topics) > 0:
        extract_topics_str = '\n'.join(f'* {extract_topics}')
        hint_extract_topics = f'重點論述擷取標的：\n{extract_topics_str}\n若無法擷取上述標的，請放棄擷取，否則罰你10000元。'
    if len(article) <= summary_len:
        summary = article
    else:
        chunk_size = 500
        sum_ak = akasha.summary.Summary(chunk_size=chunk_size, model=model, verbose=VERBOSE)
        summary = sum_ak.summarize_articles(articles=article, 
                                            summary_type="map_reduce", 
                                            summary_len=summary_len, 
                                            chunk_overlap=min(len(article)//10, chunk_size/2),
                                            system_prompt=f'''
                                            先移除主文以外的文字，再進行重點論述擷取，最後以中文方式進行摘要。
                                            ---
                                            主文定義：文章的主要內容，不含頁首、尾、參考資料、廣告、網頁標籤等。
                                            ---
                                            {hint_extract_topics}
                                            擷取到的重點論述不來自主文，罰你10000元。
                                            ---
                                            摘要規範：
                                            * 摘要結果須為原文的保留或縮減，不可新增不存在於原文的內容
                                            * 請保留語句之人、事、時、地、物等專有名詞，不可刪除、更名或轉為代名詞
                                            * 數據、年份等數字需與原文完全相同，不可任意更改
                                            * 文意須盡可能對齊原文
                                            ''') 
    if summary and list_result:
        ak = akasha.Doc_QA(model=model, verbose=VERBOSE)
        summary = ak.ask_self(
            prompt = '將下列文字以轉為條列式格式，並以"-"區分各條重點，記得保留原文論述語句架構',
            info = summary,
            system_prompt = f'''
                            超過{summary_len}字，罰你10000元
                            不是中文，罰你10000元
                            出現重複文意，罰你10000元
                            刪減原文，罰你10000元
                            '''
        )    
    return summary
    
def collect_dialogue_info_func(dialogue_history:str, collect_item_statement:str, interview_background:str, model:str=DEFAULT_MODEL):
    ak = akasha.Doc_QA(model=model, verbose=VERBOSE)
    collect_items_comma_split_str = ak.ask_self(
        prompt = '''
        根據下列敘述，列出待蒐集資訊之項目
        ''',
        info = collect_item_statement,
        system_prompt = '''
        若不符合以下任一規定，罰你10000元
        ---
        1. 輸出的項目必須存在於敘述中，不得自行新增或刪減
        2. 項目間以逗號(,)分隔，不得使用其他符號
        3. 各項目請精簡為單一名詞，不得包含形容詞或動詞，但若有多個項目精簡後出現相同名詞，則可使用形容詞或動詞區分
           ex: 使用者操作的電器 --> 電器, 操作是開還是關 --> 操作, 其背後的原因 --> 原因
        '''
    )    
    print(f'輸出的項目為:{collect_items_comma_split_str}')
    collect_items = collect_items_comma_split_str.split(',')
    
    collect_items_string = "\n".join([f"{i+1}. {c}" for i, c in enumerate(collect_items)])
    consecutive_invalid_reply_tolerance = 1
    end_dialogue_limit = 2
    ak = akasha.Doc_QA(model=model, verbose=VERBOSE)
    reply = ak.ask_self(
        prompt=f'''
        請根據下列對話紀錄，判斷目前項目還缺少的資訊並做出提問
        若沒有對話紀錄，則告知本訪談是基於{interview_background}，並提問第一個項目
        若所有資訊都搜集到，就詢問是否還有其他須回覆的項目
        若收到的回覆為沒有，則結束訪問並感謝客戶協助，並根據訪談結果，輸出{collect_items}之key-value pair
        ''',
        info=str(dialogue_history),
        system_prompt=f'''
            你是一位活潑的客服人員，需要聯繫客戶以訪談紀錄該客戶回報的資訊。
            需要問出的資訊項目如下：
            {collect_items_string}
            ---
            以上是你需要問到的資訊
            提問原則：
            (a) 一次只能針對一個問題提問
            (b) 提問範疇僅限於上述所列的資訊項目
            (c) 請有禮貌小心的提問，但禁止說您好
            (d) 表達須精簡且專注在問題上，不要透漏提問資訊以外的任何內容，包含提問身分表明或提問目的
            (e) 只能針對缺少的資訊提問，不要重複問到已經回答過的問題
            (f) (可能多個)名稱若有類似讀音的錯字，請提醒客戶確認是否正確
            
            請根據客戶最近的回答內容，做出適當回應：
            ---
            (1) 無待回報事項：感謝客戶的回覆
            (2) "沒有、不知道、忘記了"：詢問是否有其他待回報事項，連續超過{end_dialogue_limit}次則同(1)回覆
            (3) 內容不明確、看不懂、不具體：追問或提出建議猜測，超過{consecutive_invalid_reply_tolerance}次則同(2)回覆，連續超過{end_dialogue_limit}次則表達自己理解能力不足，再同(1)回覆
            (4) 與需求不符：向客戶表達疑惑並確其回答是否正確，超過{consecutive_invalid_reply_tolerance}次則同(2)回覆，連續超過{end_dialogue_limit}次則表達自己理解能力不足，再同(2)回覆
            (5) 內容消極、反感、無意願：先道歉，再同(1)回覆
            (6) 客戶提出疑問：表達歉意，重申訪問目的，並再次提問
            ---
            不要連續複述客戶的回答超過2次
            出現問題描述以外的文字(亂碼或人類看不懂的語法)，罰你10000元
            '''
    )
    return reply     
#%% Tools
db_query_tool = akasha.create_tool(
    tool_name='db_query_tool',
    tool_description='''
    This is the tool to answer question based on database query, the parameters are: 
    1. question: str, the question asked by the user, required
    2. table_name: str, the table name to query, required
    3. column_description_json: str, the path of json file which contains description of each columns in the table, 
       or the json string of the description for each column, eg. {"column1": "description1", "column2": "description2"}
       optional, default is None
    4. simplified_answer: bool, whether to simplify the answer, optional, default is False
    5. connection_config: Dict[str, str], the connection configuration of the database 
       including keys such as:(sql_type, database, user, password, host and port), 
       optional, default is {}\n''' + f'''
    6. model: str, the model to use for answering, optional, default is '{DEFAULT_MODEL}' 
    ---
    Please try to find the parameters when using this tool, required parameters must be found, optional parameters can be ignored and use default value if not found.
    the "question" MUST BE THE SAME through the whole process.
    ''',
    func=db_query_func)

webpage_summary_tool = akasha.create_tool(
    tool_name='webpage_summary_tool',
    tool_description=f'''
    This is the tool to summary article crawled from a webpage, the parameters are: 
    1. url: str, the url of the webpage, required
    2. summary_len: str, the length of summary, optional, default is 100
    3. extract_topics: List[str], the key topics to extract, 
       eg. ["topic1", "topic2"], optional, default is []
    4. list_result: bool, whether to list the summarized result, optional, default is True
    5. model: str, the model to use for summarizing, optional, default is '{DEFAULT_MODEL}'
    ---
    Please try to find the parameters when using this tool, required parameters must be found, optional parameters can be ignored and use default value if not found.
    ''',
    func=webpage_summary_func)

collect_dialogue_info_tool = akasha.create_tool(
    tool_name='webpage_summary_tool',
    tool_description=f'''
    This is the tool to collect information of assigned items from user through dialogue, the parameters are: 
    1. dialogue_history: str, the (previous) dialogue history from user and service-desk, required
    2. collect_item_statement: str, the target items to collect from user, required
    3. interview_background: str, the background of the interview, required
    4. model: str, the model to use for dialogue, optional, default is '{DEFAULT_MODEL}'
    ---
    Please try to find the parameters when using this tool, required parameters must be found, optional parameters can be ignored and use default value if not found.
    ''',
    func=collect_dialogue_info_func)

#%% main
if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv(override=True)
    
    # # FUNCTION TEST
    ## DB QUERY
    question = '請問user_1在5/1用電量最多及最少的電器分別是誰?'
    table_name = 'daily_result_bth'
    column_description_json = '''{
        "user_id": "用戶帳號",
        "report_time": "數據統計日期",
        "kwh": "總用電度數，包含其他電器",
        "appliance_kwh": "各電器用電占比，為string，值內以逗號分隔依序為電視, 冰箱, 冷氣, 開飲機, 洗衣機"
    }'''
    connection_config = set_connection_config(sql_type='SQLITE', database='database.db', user='', password='', host='', port='')
    print(db_query_func(question, table_name, column_description_json, simplified_answer=True, connection_config=connection_config))
    
    # ## SUMMARY
    # summarized_result = webpage_summary_func(url='https://www.ptt.cc/bbs/Tech_Job/M.1719665577.A.A92.html')
    # print(summarized_result)
    
    # ## DIALOGUE
    # reply = collect_dialogue_info_func(dialogue_history='''
    #                                    由於我們系統回報您的用電量異常升高，我們想了解一下您最近有開關哪些電器呢？'\n 
    #                                    我開了冷氣\n
    #                                    瞭解，您最近有開冷氣。請問您開冷氣的原因是什麼呢？\n
    #                                    天氣很熱\n
    #                                    請問除了冷氣以外，您還有開啟其他電器嗎？\n
    #                                    沒有\n
    #                                    ''', 
    #                                    collect_item_statement='想要蒐集使用者操作哪些電器，操作是開還是關，以及其背後的原因', 
    #                                    interview_background='系統回報用電量異常升高')
    # print(reply)
    
    # # AGENT TEST
    # ag = akasha.test_agent(verbose=VERBOSE,
    #                        tools=[
    #                            collect_dialogue_info_tool,
    #                            db_query_tool,
    #                            webpage_summary_tool,
    #                         ],
    #                        model=DEFAULT_MODEL,
    #                        # system_prompt='請勿重複',
    #                     )
    # questions = ['請告訴我網站 "https://www.ptt.cc/bbs/Tech_Job/M.1719665577.A.A92.html" 的重點',
    #              '''
    #              我要查詢一個"SQLITE"資料庫 名為 "database.db", 裡面有一個table="daily_result_bth",
    #              欄位意義說明如下:
    #              ---
    #              1. user_id: 用戶帳號,
    #              2. report_time": 數據統計日期,
    #              3. kwh: 總用電度數，包含其他電器,
    #              4. appliance_kwh: 各電器用電占比，為string，值內以逗號分隔依序為電視, 冰箱, 冷氣, 開飲機, 洗衣機
    #              ---
    #              請問user_1在5/1用電量最多及最少的電器分別是誰?
    #              ''',
    #              '我收到來自異常偵測模型的警示，發現使用者用電量異常升高，因此想要透過對話蒐集使用者操作哪些電器，操作是開還是關，以及其背後的原因'
    #              ]
    # for idq, q in enumerate(questions):
    #     print(f'原始問題：{q}\n---\n回答：{ag(q, messages=[])}\n\n')