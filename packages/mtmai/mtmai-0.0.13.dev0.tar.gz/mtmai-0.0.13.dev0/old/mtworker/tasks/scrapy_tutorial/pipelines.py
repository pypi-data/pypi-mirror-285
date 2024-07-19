from itemadapter import ItemAdapter
import httpx
import psycopg2

class ScrapyTutorialPipeline:
    def process_item(self, item, spider):
        return item


class ScrapyPipeLine2:
    def process_item(self, item, spider):
        callback_url = spider.settings.get("MTX_ITEM_CALLBACK_URL")
        if not callback_url:
            print("缺少callback_url 参数")
            return

        # print(f"callback_url: {callback_url}, item: {item}" )
        httpx.post(callback_url,data=item)
        return item
    
    
from itemadapter import ItemAdapter

connstr = "postgresql://mt:JPZfzJlLqkSIm9P52BAGrQ@mtxtrpcv3-3690.6xw.cockroachlabs.cloud:26257/defaultdb?sslmode=verify-full"

# 使用 cockroachlabs 不顺畅，
class PostgresDemoPipeline:
    def __init__(self):
        print("PostgresDemoPipeline init")
        try:
            
            # connstr = "postgresql://mt:FW6XDkdHPCPnkqeUJ4uwyg@stung-king-3229.6xw.cockroachlabs.cloud:26257/defaultdb"
            ## Connection Details
            # hostname = 'localhost'
            # username = 'postgres'
            # password = '*******' # your password
            # database = 'quotes'

            ## Create/Connect to database
            self.connection = psycopg2.connect(connstr)
            with self.connection.cursor() as cur:
                cur.execute("SELECT now()")
                res = cur.fetchall()
                self.connection.commit()
                print("数据库结果。。。。。。。。。。。。。。。。。。。。。。。")
                print(res)
            ## Create cursor, used to execute commands
            self.cur = self.connection.cursor()
            
            # Create quotes table if none exists
            print("Create quotes table if none exists")
            
            with self.connection.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS crawlitem_demo(
                        id serial PRIMARY KEY, 
                        content text,
                        tags text,
                        author VARCHAR(255)
                    )
                    """)
                self.connection.commit()
                print("数据库结果。。。。。。。。。。。。。。。。。。。。。。。")
                print(res)
            # self.connection.commit()
            print("PostgresDemoPipeline init 完成")
        except Exception as e:
            print("出错")
            print(e)
    def process_item(self, item, spider):
        print("process_item save to pgdb")
        self.connection = psycopg2.connect(connstr)
        self.cur = self.connection.cursor()
        try:
            self.cur = self.connection.cursor()
            ## Define insert statement
            self.cur.execute(""" insert into crawlitem_demo (content, tags, author) values (%s,%s,%s)""", (
                "content1", 
                "tags1",
                "author1"
            ))

            ## Execute insert of data into database
            self.connection.commit()
            print("已经提交到数据库")
        except Exception as e:
            print("提交到数据库出错")
            print(e)
        
        return item
    
    def close_spider(self, spider):
        print("close_spider")
        ## Close cursor & connection to database 
        self.cur.close()
        self.connection.close()