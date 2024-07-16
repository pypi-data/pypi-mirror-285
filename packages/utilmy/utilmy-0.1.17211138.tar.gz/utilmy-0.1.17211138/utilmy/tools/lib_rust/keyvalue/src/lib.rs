mod db;
use rusqlite::Connection;

use std::{path::Path, time::{Duration, SystemTime, UNIX_EPOCH}};
use crate::db::{get_connection, create_t_binary_table, DBNAME, BINARY_TABLE, TABLE_NAME};

pub struct Sqlite {
    path: String,
    conn: Connection
}


impl Sqlite {
    pub fn new(path: &str) -> Self {
        let _path = Path::new(&path).join(DBNAME);
        let conn = get_connection(_path);
        create_t_binary_table(&conn);
        Sqlite {
            path: path.to_string(),
            conn:conn 
        } 
    }

    pub fn get_path(&self) -> String {
        self.path.clone()
    }

    pub fn set(&self, k: &str, v: &str, ttl: Option<Duration>) -> bool{
        
        let mut ttl = if ttl.is_some() {ttl.unwrap().as_secs()} else {10};
        ttl = ttl.min(i64::MAX as u64);

        let expiry = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_secs()
        .saturating_add(ttl)
        .min(i64::MAX as u64);
        let result = self.conn.execute(
            &format!("INSERT INTO {} (key, value, expire, ttl) values (?, ?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET value=?, expire=?  WHERE key=?
            ", TABLE_NAME),
             rusqlite::params![k, v, expiry, ttl, v, expiry, k]
            );
        true
    }

    pub fn get(&self, key: &str) -> String {
        let expiry = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs()
            .min(i64::MAX as u64);


        let result = self.conn
                                        .prepare(&format!("SELECT value FROM {} where key = '{}' and expire > {};",
                                                TABLE_NAME,
                                                key,
                                                expiry));

        let s = String::from("");

        if result.is_ok() {
            let mut stmt = result.unwrap();

            let mut rows = stmt.query([]).unwrap();
            let row = rows.next();
            let r1 = row.unwrap();
            if r1.is_some() { 
                let r2 = r1.unwrap();
                let s = r2.get(0);

                return s.unwrap()
            }
        }
        s
    }

    pub fn set_binary(&self, k: &str, v: &[u8], ttl: Option<Duration>) -> bool{
        
        let mut ttl = if ttl.is_some() {ttl.unwrap().as_secs()} else {10};
        ttl = ttl.min(i64::MAX as u64);

        let expiry = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_secs()
        .saturating_add(ttl)
        .min(i64::MAX as u64);
        let _ = self.conn.execute(
            &format!("INSERT INTO {} (key, value, expire, ttl) values (?, ?, ?, ?)", BINARY_TABLE),
             rusqlite::params![k, v, expiry, ttl]
            );
        true
    }

    pub fn get_binary(&self, k: &str) -> Option<Vec<u8>> {
        let expiry = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs()
            .min(i64::MAX as u64);

        let result = self.conn.prepare(
            &format!("SELECT value FROM {} where key = '{}' and expire > {};", BINARY_TABLE, k, expiry));



        if result.is_ok() {
            let s = result
                    .unwrap()
                    .query([])
                    .unwrap().next()
                    .unwrap()
                    .unwrap()
                    .get(0)
                    .unwrap();
            return s;
        }
        None
    }


    pub fn exec_sql(&self, query: &str) -> Vec<Vec<String>> {
        let mut stmt = self.conn.prepare(query).unwrap();
        let mut v: Vec<Vec<String>> = Vec::new();
        let count = stmt.column_count();
        let result = stmt.query_map([], |row|{
            let mut vv = Vec::new();
            for i in 0..count {
                vv.push(row.get(i).unwrap());
            }
            Ok(vv)
        });

        for i in result {
            for jj in i {
                v.push(jj.unwrap());
            }
        }
        v
    }



}


#[cfg(test)]
mod tests {
    use std::thread::sleep;

    use super::*;

    #[test]
    fn set_value() {
        let path = "./src";
        let _sqlite = Sqlite::new(path);

        _sqlite.set("Firsttest", "check value test all", Some(Duration::new(5, 0)));
        assert_eq!(_sqlite.get("Firsttest"), "check value test all");
    }

    #[test]
    fn ttl_test() {
        let path = "./src";
        let _sqlite = Sqlite::new(path);

        _sqlite.set("ttl_test", "check value test all", Some(Duration::new(2, 0)));
        sleep(Duration::new(4, 0));
        assert_eq!(_sqlite.get("ttl_test"), "");
    }
}