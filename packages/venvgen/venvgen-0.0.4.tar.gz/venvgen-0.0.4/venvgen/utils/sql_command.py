create_venv_info_sql = '''
CREATE TABLE IF NOT EXISTS venv_info(
    id INTEGER PRIMARY KEY ASC AUTOINCREMENT,
    project_path VARCHAR(300) NOT NULL,
    venv_name VARCHAR(200) NOT NULL,
    created_date DATE NOT NULL,
    requirement_file VARCHAR(300),
    connect_status VARCHAR(20) NOT NULL,
    last_modified DATETIME NOT NULL,
    UNIQUE(project_path, venv_name)
);
'''

create_venv_log_sql = '''
CREATE TABLE IF NOT EXISTS venv_log(
    id INTEGER PRIMARY KEY ASC AUTOINCREMENT,
    venv_id INTEGER NOT NULL,
    modify_type VARCHAR(20) NOT NULL,
    modify_time DATETIME NOT NULL,
    FOREIGN KEY (venv_id) REFERENCES venv_info(id)
);
'''

insert_into_venv_info_sql = '''
INSERT INTO venv_info(project_path, venv_name, created_date, requirement_file, connect_status, last_modified) 
VALUES (?, ?, ?, ?, ?, ?);
'''

update_connect_status_venv_info_sql = '''
UPDATE venv_info
SET connect_status = ?,
    last_modified = ?
WHERE venv_name = ?;
'''


select_all_venv_view = '''
SELECT venv_name as [VENV],
       created_date AS [CREATED DATE],
       connect_status AS [CONNECTION STATUS],
       project_path AS [PROJECT DIR],
       last_modified AS [LAST MODIFIED]
FROM   venv_info;
'''

select_latest_create_date_venv_view = '''
SELECT venv_name as [VENV],
       created_date AS [CREATED DATE],
       connect_status AS [CONNECTION STATUS],
       project_path AS [PROJECT DIR],
       last_modified AS [LAST MODIFIED]
FROM   venv_info
ORDER BY created_date DESC;
'''