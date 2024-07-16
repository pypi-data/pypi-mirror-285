import sys
import os
import inspect
import logging
import json
from datetime import datetime, timezone
import psycopg2
from typing import Dict, Set, Optional, Any

executed_lines: Dict[str, Dict[str, Set[int]]] = {}

def trace_calls(frame: Any, event: str, arg: Any) -> Optional[callable]:
    logger.debug(f"trace_calls called with event: {event}")
    
    if event != 'call':
        logger.debug("Event is not 'call', returning None")
        return None
    
    code = frame.f_code
    filename = code.co_filename
    func_name = code.co_name
    
    if filename.startswith(BASE_DIR) and not filename.startswith(VENV_DIR):
        lineno = frame.f_lineno
        executed_lines.setdefault(filename, {}).setdefault(func_name, set())
        logger.info(f"Call to {func_name} in {filename}:{lineno}")
        return trace_lines
    
    logger.debug(f"File {filename} not in project directory, skipping")
    return None

def trace_lines(frame: Any, event: str, arg: Any) -> Optional[callable]:
    if event not in ('line', 'return'):
        return None
    
    code = frame.f_code
    filename = code.co_filename
    func_name = code.co_name
    lineno = frame.f_lineno
    
    if filename.startswith(BASE_DIR) and not filename.startswith(VENV_DIR):
        executed_lines[filename][func_name].add(lineno)
        print(f"{event.capitalize()} {func_name} in {filename}:{lineno}")
    
    return trace_lines

def log_data_change(action: str, data: dict, base_dir: str) -> None:
    log_entry = {
        "action": action,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": data
    }
    log_file_path = os.path.join(base_dir, 'data_changes.json')
    
    try:
        if not os.path.exists(log_file_path):
            with open(log_file_path, 'w') as f:
                json.dump([log_entry], f, indent=4)
        else:
            with open(log_file_path, 'r+') as f:
                try:
                    data_changes = json.load(f)
                except json.JSONDecodeError:
                    data_changes = []
                data_changes.append(log_entry)
                f.seek(0)
                json.dump(data_changes, f, indent=4)
    except IOError as e:
        logger.error(f"Error writing to log file: {e}")

def fetch_cdc_changes(postgres_uri: str, replication_slot: str, base_dir: str) -> None:
    try:
        connection = psycopg2.connect(postgres_uri)
        cursor = connection.cursor()
        cursor.execute(f"SELECT * FROM pg_logical_slot_get_changes('{replication_slot}', NULL, NULL);")
        changes = cursor.fetchall()
        if changes:
            log_file_path = os.path.join(base_dir, 'cdc_changes.json')
            log_entries = []

            for change in changes:
                log_entry = {
                    "lsn": change[0],
                    "xid": change[1],
                    "data": change[2]
                }
                log_entries.append(log_entry)

            if not os.path.exists(log_file_path):
                with open(log_file_path, 'w') as f:
                    json.dump(log_entries, f, indent=4)
            else:
                with open(log_file_path, 'r+') as f:
                    try:
                        cdc_data = json.load(f)
                    except json.JSONDecodeError:
                        cdc_data = []
                    cdc_data.extend(log_entries)
                    f.seek(0)
                    json.dump(cdc_data, f, indent=4)
        
        cursor.close()
        connection.close()
    except (Exception, psycopg2.DatabaseError) as e:
        logger.error(f"Error fetching CDC changes: {e}")

def setup_tracking(base_dir: str, venv_dir: str, log_file_path: str, postgres_uri: str, replication_slot: str):
    global BASE_DIR, VENV_DIR, logger
    BASE_DIR = base_dir
    VENV_DIR = venv_dir

    logging.basicConfig(filename=log_file_path, level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    def before_request():
        sys.settrace(trace_calls)
        fetch_cdc_changes(postgres_uri, replication_slot, BASE_DIR)

    def after_request(response):
        sys.settrace(None)
        
        total_lines = 0
        executed_lines_count = 0
        
        for filename, funcs in executed_lines.items():
            if filename.endswith('app.py'):
                file_lines = []
                with open(filename, 'r') as f:
                    file_lines = f.readlines()
                total_lines += len(file_lines)
                
                for func_name, lines in funcs.items():
                    executed_lines_count += len(lines)
        
        if total_lines > 0:
            coverage_percentage = (executed_lines_count / total_lines) * 100
            print(f"\nOverall coverage for app.py:")
            print(f"Total lines: {total_lines}")
            print(f"Executed lines: {executed_lines_count}")
            print(f"Coverage percentage: {coverage_percentage:.2f}%")
        
        log_file_path = os.path.join(BASE_DIR, 'changes.log')
        with open(log_file_path, 'a') as log_file:
            for filename, funcs in executed_lines.items():
                for func_name, lines in funcs.items():
                    if func_name == 'after_request':
                        continue
                    
                    print(f"\nFunction '{func_name}' in {filename}:")
                    try:
                        func_obj = globals().get(func_name)
                        if func_obj is None:
                            for name, obj in inspect.getmembers(sys.modules[__name__]):
                                if inspect.isfunction(obj) and obj.__name__ == func_name:
                                    func_obj = obj
                                    break
                        if func_obj is None:
                            module_list = list(sys.modules.values())
                            for mod in module_list:
                                for name, obj in inspect.getmembers(mod):
                                    if inspect.isfunction(obj) and obj.__name__ == func_name:
                                        func_obj = obj
                                        break
                        if func_obj:
                            source_lines, start_line = inspect.getsourcelines(func_obj)
                            total_lines_set = set(range(start_line, start_line + len(source_lines)))
                            unused_lines = total_lines_set - lines
                            
                            unused_lines = [
                                line for line in unused_lines
                                if not source_lines[line - start_line].strip().startswith(('@app', 'def', 'class'))
                            ]
                            
                            coverage_percentage = ((len(total_lines_set) - len(unused_lines)) / len(total_lines_set)) * 100
                            
                            print(f"Executed lines: {sorted(lines)}")
                            print(f"Total lines: {sorted(total_lines_set)}")
                            print(f"Unused lines: {sorted(unused_lines)}")
                            
                            log_file.write(f"Function: {func_name} in {filename}\n")
                            log_file.write(f"Coverage percentage: {coverage_percentage:.2f}%\n\n")
                        else:
                            print(f"Could not find function '{func_name}' in the global scope.")
                    except KeyError:
                        print(f"Could not find function '{func_name}' in the global scope.")
        
        return response

    return before_request, after_request
