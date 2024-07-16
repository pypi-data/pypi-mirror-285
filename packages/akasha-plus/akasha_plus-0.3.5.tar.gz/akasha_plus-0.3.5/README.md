# akasha-plus

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![python version : 3.9 3.10 3.11](https://img.shields.io/badge/python-3.9%20%7C%203.10%20%7C%203.11-blue)](https://www.python.org/downloads/release/python-390/)

<br/>

Akasha-plus is an external-plugin for [akasha](https://github.com/iii-org/akasha), which includes various kind of extended applications like model quantisation, agent-tools and others.

<br/>
<br/>

# Installation
 For Specific Operating System, remember to run the following command(s) beforehand 
* Debian/Ubuntu
```bash
sudo apt-get install libpq5 -y
```

We recommend using Python 3.9 to run our akasha-plus package. You can use Anaconda to create virtual environment.

```bash
# create virtual environment
conda create --name py3-9 python=3.9
activate py3-9

# install akasha-plus
pip install akasha-plus
```

<br/>
<br/>

# Python API
## Agent Tools
Use customized tools to speed-up application development.
For each tool, there are two ways to use it, include "apply tool function directly" and "use akasha agent". The main difference between these two ways mentioned above is that the first requires the developer to set individual parameters manually, while the second allows for a conversational description, enabling the agent to determine the corresponding parameters on its own automatically.

### Database-Query Tool
This tool is used for question-answering based on specific given database table.

#### Prepare sample data
* Assume a csv file(daily_result.csv) with tabular data which records electric consumption of 3 users(Tim, Joe and Frank) 

| user_id |   report_time  |   update_time   |    kwh   |            appliance_kwh           |
|---------|----------------|-----------------|----------|------------------------------------|
| Tim     | 2024/5/1 00:00 | 2024/5/2 00:00  |  10.04   | 0.0409,0.1301,0.0623,0.0478,0.0041 |
| Joe     | 2024/5/1 00:00 | 2024/5/2 00:00  |  2.96    | 0.0,0.0,0.09919,0.0,0.0            |
| Frank   | 2024/5/1 00:00 | 2024/5/2 00:00  |  15.2    | 0.0,0.117266,0.0,0.031103,0.0      |

* import data into SQLITE database
```python
# !pip install sqlite3 pandas
import pandas as pd
import sqlite3
import os

# read csv as dataframe
df = pd.read_csv('./daily_result.csv')

# Create the table
## define table name, table schema
table_name = 'daily_result'
table_schema = f'''
    CREATE TABLE IF NOT EXISTS {table_name} (
        id INTEGER PRIMARY KEY,
        user_id varchar(100) NOT NULL,
        report_time timestamp NOT NULL,
        update_time timestamp NOT NULL,
        kwh numeric NOT NULL,
        appliance_kwh varchar(500) NOT NULL
    );'''

## build connection
conn = sqlite3.connect('./database.db')
cursor = conn.cursor()
cursor.execute(table_schema)
conn.commit()

# Write data into table
df.to_sql(table_name, conn, if_exists='append', index=False)
conn.commit()
```

#### Apply function directly
```python
# import module
from akasha_plus.agents.tools import set_connection_config, db_query_func
# define question, table_name
question = '請問Tim在5/1用電量最多及最少的電器分別是誰?'
table_name = 'daily_result'
# define column description json (in json-like string or path of json file) if needed
column_description_json = '''{
    "user_id": "用戶帳號",
    "report_time": "數據統計日期",
    "kwh": "總用電度數，包含其他電器",
    "appliance_kwh": "各電器用電占比，為string，值內以逗號分隔依序為電視, 冰箱, 冷氣, 開飲機, 洗衣機"
}'''
# set database connection
connection_config = set_connection_config(sql_type='SQLITE', database='database.db')
# use tool to get answer
answer = db_query_func(question=question, table_name=table_name, simplified_answer=True, connection_config=connection_config, model='openai:gpt-4')
print(answer)
```

#### Use akasha agent
```python
import akasha
from akasha_plus.agents.tools import db_query_tool
agent = akasha.test_agent(verbose=True, tools=[db_query_tool], model='openai-gpt-4')
# put all information in plain language
question = '''
    我要查詢一個"SQLITE"資料庫 名為 "database.db", 裡面有一個table="daily_result",
    欄位意義說明如下:
    ---
    1. user_id: 用戶帳號,
    2. report_time": 數據統計日期,
    3. kwh: 總用電度數，包含其他電器,
    4. appliance_kwh: 各電器用電占比，為string，值內以逗號分隔依序為電視, 冰箱, 冷氣, 開飲機, 洗衣機
    ---
    請問Tim在5/1用電量最多及最少的電器分別是誰?
    '''   
# let akasha agent to consider the rest of the process       
answer = agent(question, messages=[])
print(answer)
```

#### The answer will be like the following:
```shell
5/1當天，Tim用電量最多的電器是冰箱，用電量最少的電器是洗衣機。
```

### Webpage Summary Tool
This tool is used for retrieving summary contents from specific webpage with given url.
#### Apply function directly
```python
from akasha_plus.agents.tools import webpage_summary_func
summarized_result = webpage_summary_func(url='https://www.ptt.cc/bbs/Japan_Travel/M.1719024725.A.44E.html', model='openai:gpt-4')
print(summarized_result) 
```
#### Use akasha agent
```python
import akasha
from akasha_plus.agents.tools import webpage_summary_tool
agent = akasha.test_agent(verbose=True, tools=[webpage_summary_tool], model='openai-gpt-4')
# put all information in plain language
question = '''請告訴我網站 "https://www.ptt.cc/bbs/Japan_Travel/M.1719024725.A.44E.html" 的重點'''   
# let akasha agent to consider the rest of the process       
answer = agent(question, messages=[])
print(answer)
```

#### The answer will be like the following:
```shell
- 2024年，日本觀光業出現「觀光客價格」，引發討論。
- 儘管日本物價水準對比歐美仍低，且實質薪資已連續24個月為負值，但日本仍被視為「廉價」的旅遊目的地。
- 根據日本國家旅遊局統計，2024年3月訪日遊客人數約為308萬人次，首次突破300萬人次。
- 然而，專為觀光客設定的價格，如東京豐洲的海鮮蓋飯價格和商業旅館價格，都比一般價格高。
- 網友們對此有不同看法，有人認為只要學好日文就不會有煩惱，有人則認為全世界都會薛觀光客。
```

### Dialogue Information Collection Tool
This tool is used for collecting information of specific items/categories assigned by user through dialogue. The generated output will be the latest reply in order to continue dialogue for data collection.
#### Apply function directly
```python
from akasha_plus.agents.tools import collect_dialogue_info_func
reply = collect_dialogue_info_func(dialogue_history='''
    由於我們系統回報您的用電量異常升高，我們想了解一下您最近有開關哪些電器呢？'\n 
    我開了冷氣\n
    瞭解，您最近有開冷氣。請問您開冷氣的原因是什麼呢？\n
    天氣很熱\n
    請問除了冷氣以外，您還有開啟其他電器嗎？\n
    沒有\n
    ''', 
    collect_item_statement='想要蒐集使用者操作哪些電器，操作是開還是關，以及其背後的原因', 
    interview_background='系統回報用電量異常升高'
)
print(reply)
```

#### Use akasha agent
```python
import akasha
from akasha_plus.agents.tools import collect_dialogue_info_tool
agent = akasha.test_agent(verbose=True, tools=[collect_dialogue_info_tool], model='openai-gpt-4')
# put all information in plain language
question = '''我收到來自異常偵測模型的警示，發現使用者用電量異常升高，因此想要透過對話蒐集使用者操作哪些電器，操作是開還是關，以及其背後的原因'''   
# let akasha agent to consider the rest of the process       
answer = agent(question, messages=[])
print(answer)
```

#### The answer will be like the following:
```shell
感謝您的回覆，我們已經收到您的資訊。再次感謝您的協助！
{'電器': '冷氣', '操作': '開啟', '原因': '天氣熱'}
```

# Console mode API

### to-gguf
Change model directory downloaded from [huggingface](https://huggingface.co/) into [gguf format](https://huggingface.co/docs/hub/gguf)
<br/>
Usage:
```bash
akasha-plus to-gguf --model "<your-model-directory>" --outtype "<floating-point-precision>" --verbose --pad-vocab
```

### quantize-gguf
Quantize gguf model into smaller bit of precision
<br/>
To successfully quantize model, make sure you have a gguf-formatted model, or use `akasha-plus to-gguf` api to transfer the model into gguf format.
<br/>
Usage:
```bash
akasha-plus quantize-gguf --model "<gguf-model-path>" --method "<quantization-method>" --verbose
```

### quantize-gptq
Quantize model into smaller bit of precision by [auto-gptq](https://github.com/AutoGPTQ/AutoGPTQ)
<br/>
Usage:
```bash
akasha-plus quantize-gptq --model "<model-path>" --bits "<quantizat-bits>"
```
