import json
import lmdb
import os
import shutil

class ConfigDB():

    # 数据库路径
    db_path = os.path.join(os.getcwd(),'db')
    # 数据库名称
    db_name = ''
    # 数据库打开文件对象
    env = None
    

    def __init__(self,path = None,db_path_name = 'db',db_name=b'tmp',size=256,max_dbs = 128):
        """配置数据库

        Args:
            db_path (str, optional): 数据库路径,默认当前文件路径下. Defaults to None.
            db_path_name (str, optional): 数据库名. Defaults to 'db'.
            db_name (bytes, optional): 命名数据库. Defaults to b'tmp'.
            size (int, optional): 数据库大小(以M为单位). Defaults to 256.
            max_dbs (int, optional): 最多命名数据库数量. Defaults to 128.
        """        
        if path:
            self._path = path
        else:
            self._path = os.getcwd()

        self.db_name = db_name
        self.db_path = os.path.join(self._path,db_path_name)
        self.env = lmdb.open(self.db_path, map_size=1024*1024*size, max_dbs=max_dbs)

    def write(self, key:str , value:str | dict, db_name = None) -> bool:
        """添加键值对

        Args:
            key (str): 键.
            value (str | dict): 值.
            db_name (_type_, optional): 命名数据库. Defaults to None.

        Returns:
            bool: 添加结果.
        """ 
        try:
            if db_name is None:
                db_name = self.db_name
            db = self.env.open_db(db_name)
            with self.env.begin(db=db, write=True) as txn:
                key = key.encode()
                if type(value) == dict:
                    try:
                        value = json.dumps(value).encode()
                    except Exception:
                        value = value.encode()
                else:
                    value = value.encode()
                txn.put(key, value)
            return True
        except Exception:
            return False

    def read(self,key:str, db_name = None) -> str|dict|bool:
        """获取键值对

        Args:
            key (str): 键.
            db_name (_type_, optional): 命名数据库. Defaults to None.

        Returns:
            result: str OR json OR False.
        """
        try:
            if db_name is None:
                db_name = self.db_name
            db = self.env.open_db(db_name)
            result = None
            with self.env.begin(db=db) as txn:
                result = txn.get(key.encode())
                if result:
                    result = result.decode()
            if result is not None and "{" in result:
                try:
                    result = json.loads(result)
                except Exception:
                    pass
            return result
        except Exception:
            return False
    
    def delete(self, key:str, db_name = None) -> bool:
        """删除键值对

        Args:
            key (str): 键.
            db_name (_type_, optional): 命名数据库. Defaults to None.

        Returns:
            bool: 删除结果.
        """
        try:
            if db_name is None:
                db_name = self.db_name
            db = self.env.open_db(db_name)
            result = None
            with self.env.begin(db=db,write=True) as txn:
                result = txn.delete(key.encode())
            return result
        except lmdb.Error as e:
            return False
    
    def updata(self, key:str , value:str | dict, db_name = None) -> bool:
        """更新键值

        Args:
            key (str): 键.
            value (str | dict): 值.
            db_name (_type_, optional): 命名数据库. Defaults to None.

        Returns:
            bool: 更新结果.
        """        
        try:
            if db_name is None:
                db_name = self.db_name
            db = self.env.open_db(db_name)
            with self.env.begin(db=db, write=True) as txn:
                key = key.encode()
                if type(value) == dict:
                    try:
                        value = json.dumps(value).encode()
                    except Exception:
                        value = value.encode()
                else:
                    value = value.encode()
                txn.put(key, value, overwrite=True)
            return True
        except lmdb.Error as e:
            return False

    def get(self, keys:list[str], db_name = None) -> tuple:
        """查找内部键值

        Args:
            keys (list[str]): 按层级顺序键.
            value (str | dict): 值.
            db_name (_type_, optional): 命名数据库. Defaults to None.

        Returns:
            result: (结果状态, 层级 or None, 结果).
        """       
        try: 
            key_length = len(keys) 
            if key_length < 1:
                return None
            result =  self.read(keys[0], db_name)
            if result:
                if type(result) == dict and key_length > 1:
                    for index,key in keys[1:]:
                        if key in result:
                            result = result[key]
                        else:
                            return (False,index + 1,key)
                    return (True,key_length,result)
                else:
                    return (True,None,result)
            else:
                return (None,None,None)
        except Exception:
            return (False,None,None)
    
    def set(self, keys:list[str] , value:str | dict, db_name = None) -> bool:
        """设置内部键值

        Args:
            keys (list[str]): 按层级顺序键.
            value (str | dict): 值.
            db_name (_type_, optional): 命名数据库. Defaults to None.

        Returns:
            bool: 设置结果.
        """        
        try:

            def ensure_dict_keys_exist(json_obj, keys, value):
                """生成嵌套字典

                Args:
                    json_obj (_type_): 字典对象
                    keys (_type_): 键列表
                    value (_type_): 键值
                """                
                current_level = json_obj
                keys_length = len(keys)
                index = 0
                for key in keys:
                    if key not in current_level:
                        if index == keys_length - 1:
                            current_level[key] = value
                        else:
                            current_level[key] = {}
                    else:
                        if type(current_level[key]) != dict:
                            if index == keys_length - 1:
                                current_level[key] = value
                            else:
                                current_level[key] = {}
                        else:
                            if index == keys_length - 1:
                                current_level[key] = value
                    index += 1
                    current_level = current_level[key]

            key_length = len(keys) 
            if key_length < 1:
                return None
            result = self.read(keys[0], db_name)
            if result:
                if type(result) == dict and key_length > 1:
                    ensure_dict_keys_exist(result, keys[1:], value)
                    return self.updata(keys[0],result, db_name)
                else:
                    return self.updata(keys[0],result, db_name)
            else:
                m_key = keys[0]
                v_key = {}
                ensure_dict_keys_exist(v_key, keys[1:], value)
                return self.write(m_key,v_key, db_name)
        except Exception as e:
            return False

    def remove(self, keys:list[str], db_name = None) -> bool:
        """移除某个内部键

        Args:
            keys (list[str]): 按层级顺序键.
            db_name (_type_, optional): 命名数据库. Defaults to None.

        Returns:
            bool: 移除结果
        """        
        try:
            def remove_last_key_if_exists(dict_obj, keys_sequence):
                current_level = dict_obj
                for key in keys_sequence[:-1]:  # 遍历除了最后一个键的所有键
                    if key in current_level:
                        current_level = current_level[key]
                    else:
                        return  False# 如果某个键不存在，则退出函数
                # 删除最后一个键
                if keys_sequence[-1] in current_level:
                    del current_level[keys_sequence[-1]]
                return  True
            
            result = self.read(keys[0], db_name)
            if result:
                keys_length = len(keys)
                if type(result) == dict and keys_length > 1:
                    r = remove_last_key_if_exists(result,keys[1:])
                    if r:
                        return self.updata(keys[0],result, db_name)
                    else:
                        return False
                elif  keys_length == 1:
                    return self.delete(keys[0], db_name)
                else:
                    return False
            else:
                return False
        except Exception:
            return False

    def env_close(self) -> bool:
        """关闭数据库环境

        Returns:
            bool: 关闭结果
        """        
        try:
            self.env.close()
            return True
        except Exception:
            return False

    def get_limit(self, start:int = 0, limit:int = 100, db_name:str = None) -> dict:
        """获取指定位置和数量的键值对

        Args:
            start (int): 开始位置. Defaults to 0.
            limit (int, optional): 数量. Defaults to 100.
            db_name (str, optional): 命名数据库. Defaults to None.


        Returns:
            json: 结果集
        """        
        try:
            if db_name is None:
                db_name = self.db_name
            db = self.env.open_db(db_name)
            result = {}
            with self.env.begin(db=db) as txn:
                # 创建游标
                cursor = txn.cursor()
                # 遍历指定数量的键值对
                count = 0
                end = start + limit - 1
                for key, value in cursor:
                    if count >= start:
                        value = value.decode('utf-8')
                        if value is not None and "{" in value:
                            try:
                                value = json.loads(value)
                            except Exception:
                                pass
                        result[key.decode('utf-8')] = value
                    if count == end:
                        break
                    count += 1

            return result
        except Exception:
            return False

    def get_sum(self, db_name:str = None) -> int:
        """获取存储键值对总数

        Args:
            db_name (str, optional): 命名数据库. Defaults to None.

        Returns:
            int: 总数
        """        
        try:
            if db_name is None:
                db_name = self.db_name
            db = self.env.open_db(db_name)
            result = 0
            with self.env.begin(db=db) as txn:
                stats = txn.stat()
                result = stats['entries']
            return result
        except Exception:
            return False

    @staticmethod    
    def cleanup(db_path:str = None) -> bool:
        """删除整个数据库

        Args:
            db_path (str, optional): 数据库路径,默认使用初始路径. Defaults to None.

        Returns:
            bool: 执行结果
        """           
        if db_path is None:
            db_path = ConfigDB.db_path
        if os.path.exists(db_path):
            try:
                shutil.rmtree(db_path)
                return True
            except OSError as e:
                return False

if __name__ == "__main__":
    # ConfigDB.cleanup()
    db = ConfigDB()
    # for i in range(1000):
    #     db.write('a'+str(i),{'a':1,'b':{'c':2,'d':{"e":{"f":123,"g":None}}}})
    # print(db.read('a'))
    # print(db.remove(['a','b','d','e','f']))
    # print(db.read('a'))
    print(db.get_sum())
    print(len(db.get_limit(1000,100).keys()))
