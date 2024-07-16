use std::path::PathBuf;

use rusqlite::Connection;


pub const DBNAME: &str = "localcache.db";
pub const TABLE_NAME: &str = "local_cache";
pub const BINARY_TABLE: &str = "t_binary";



fn create_cache_table_if_not_exist(connection: &Connection) {
    let query = &format!(r#"select * from {} limit 1;"#, TABLE_NAME);
    let is_table = connection.execute(query, ());

    if is_table.is_err() {
        let query = format!(r#"
        begin transaction;
        create table if not exists {} (
            key Text,
            value Text,
            expire integer not null,
            ttl integer not null,
            CONSTRAINT key_unique UNIQUE (key)
        );
        commit;
        "#, TABLE_NAME);

        let result = connection.execute_batch(&query);
        if result.is_err() {
            println!("{:#?}", result);
        }
    }
}

pub fn create_t_binary_table(connection: &Connection) {
    let query = format!(r#"select * from {} limit 1;"#, BINARY_TABLE);
    let is_table = connection.execute(&query, ());

    if is_table.is_err() {
        let query = format!(r#"
        begin transaction;
        create table if not exists {} (
            key Text,
            value Blob,
            expire integer not null,
            ttl integer not null,
            CONSTRAINT key_unique UNIQUE (key)
        );
        commit;
        "#, BINARY_TABLE);

        let result = connection.execute_batch(&query);
        if result.is_err() {
            println!("{:#?}", result);
        }
    }
}

pub fn get_connection(path: PathBuf) -> Connection {
    let connection = Connection::open(path).unwrap();
    create_cache_table_if_not_exist(&connection);
    connection
}
