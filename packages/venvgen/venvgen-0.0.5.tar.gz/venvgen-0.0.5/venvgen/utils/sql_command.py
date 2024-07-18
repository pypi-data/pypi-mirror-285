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
    modify_type VARCHAR(30) NOT NULL,
    modify_time DATETIME NOT NULL,
    modified_by VARCHAR(20) NOT NULL,
    FOREIGN KEY (venv_id) REFERENCES venv_info(id) ON DELETE NO ACTION
);
'''

create_venv_insert_trigger_log_sql = '''
CREATE TRIGGER IF NOT EXISTS venv_insert_info_trigger
AFTER INSERT ON venv_info
FOR EACH ROW
BEGIN 
    INSERT INTO venv_log(venv_id, modify_type, modify_time, modified_by)
    VALUES (NEW.id, 'INSERT VENV', DATETIME('now', 'localtime'), 'USER');
END;
'''

create_venv_update_status_trigger_log_sql = '''
CREATE TRIGGER IF NOT EXISTS venv_status_update_trigger
AFTER UPDATE OF connect_status ON venv_info
FOR EACH ROW
BEGIN
    INSERT INTO venv_log(venv_id, modify_type, modify_time, modified_by)
    VALUES (NEW.id, 'UPDATE CONNECTION STATUS', DATETIME('now', 'localtime'), 'SYSTEM');
END;
'''




insert_into_venv_info_sql = '''
INSERT INTO venv_info(project_path, venv_name, created_date, requirement_file, connect_status, last_modified) 
VALUES (?, ?, ?, ?, ?, ?);
'''

update_connect_status_venv_info_sql = '''
UPDATE venv_info
SET connect_status = ?,
    last_modified = ?
WHERE id = ?;
'''


select_all_venv_view = '''
SELECT id AS [VENV ID],
       venv_name AS [VENV],
       created_date AS [CREATED DATE],
       connect_status AS [CONNECTION STATUS],
       project_path AS [PROJECT DIR],
       last_modified AS [LAST MODIFIED]
FROM   venv_info;
'''

select_latest_create_date_venv_view = '''
SELECT id AS [VENV ID],
       venv_name AS [VENV],
       created_date AS [CREATED DATE],
       connect_status AS [CONNECTION STATUS],
       project_path AS [PROJECT DIR],
       last_modified AS [LAST MODIFIED]
FROM   venv_info
ORDER BY created_date DESC;
'''

select_top_latest_create_data_venv_view = '''
SELECT id AS [VENV ID],
       venv_name AS [VENV],
       created_date AS [CREATED DATE],
       connect_status AS [CONNECTION STATUS],
       project_path AS [PROJECT DIR],
       last_modified AS [LAST MODIFIED]
FROM   venv_info
ORDER BY created_date DESC
LIMIT ?;
'''

select_top_latest_modified_data_venv_view = '''
SELECT id AS [VENV ID],
       venv_name AS [VENV],
       created_date AS [CREATED DATE],
       connect_status AS [CONNECTION STATUS],
       project_path AS [PROJECT DIR],
       last_modified AS [LAST MODIFIED]
FROM   venv_info
ORDER BY last_modified DESC
LIMIT ?;
'''

select_top_earliest_create_data_venv_view = '''
SELECT id AS [VENV ID],
       venv_name AS [VENV],
       created_date AS [CREATED DATE],
       connect_status AS [CONNECTION STATUS],
       project_path AS [PROJECT DIR],
       last_modified AS [LAST MODIFIED]
FROM   venv_info
ORDER BY created_date
LIMIT ?;
'''

select_top_earliest_modified_data_venv_view = '''
SELECT id AS [VENV ID],
       venv_name AS [VENV],
       created_date AS [CREATED DATE],
       connect_status AS [CONNECTION STATUS],
       project_path AS [PROJECT DIR],
       last_modified AS [LAST MODIFIED]
FROM   venv_info
ORDER BY last_modified
LIMIT ?;
'''

select_specific_venv = '''
SELECT id AS [VENV ID],
       venv_name AS [VENV],
       created_date AS [CREATED DATE],
       connect_status AS [CONNECTION STATUS],
       project_path AS [PROJECT DIR],
       last_modified AS [LAST MODIFIED]
FROM   venv_info
WHERE  id = ?;
'''