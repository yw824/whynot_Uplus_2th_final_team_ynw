### pages의 파일 별 기능 
- Chatbot.py : ~241231 MockUp 페이지 위한 Streamlit 페이지 
    - Deprecated 
- model_query.py : 연결되는 
- temp_query-test.py
- credentials.py : AWS RDS 연결에 필요한 정보들을 담은 파일 
    - .gitignore에 적용됨 
    ```
    user_id = "$your_user_id"
    user_pw = "$your_user_pw"
    endpoint = "$your-database.ap-northeast-2.rds.amazonaws.com"
    port = "$your_port_num"
    db = "$your_database_name"
    ```