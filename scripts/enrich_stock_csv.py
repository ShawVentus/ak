
import csv
import re
import argparse
import logging
from pathlib import Path
from typing import Dict, Optional, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_markdown(md_path: str) -> Dict[str, Dict[str, str]]:
    """
    Parses the markdown file to extract function details.
    Returns a dictionary keyed by function name.
    """
    if not Path(md_path).exists():
        logger.error(f"Markdown file not found: {md_path}")
        return {}

    logger.info(f"Parsing markdown file: {md_path}")
    
    data = {}
    current_func = None
    
    # State tracking
    # 0: Searching for "接口:"
    # 1: Found Interface, searching for "描述:", "限量:", "输入参数"
    # 2: In Input Table
    
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Regex patterns
    # Matches "接口: stock_name" or "接口: stock_name " (ignoring trailing spaces)
    interface_pattern = re.compile(r'^接口:\s*([a-zA-Z0-9_]+)')
    desc_pattern = re.compile(r'^描述:\s*(.+)')
    limit_pattern = re.compile(r'^限量:\s*(.+)')
    input_start_pattern = re.compile(r'^输入参数')
    
    # Storage for current processing item
    item = {'desc': '', 'limit': '', 'inputs': ''}
    input_table_lines = []
    in_input_table = False
    looking_for_input_table = False  # New flag: set after seeing "输入参数"

    for i, line in enumerate(lines):
        line = line.rstrip()
        
        # 1. Detect Interface Start
        match = interface_pattern.match(line)
        if match:
            # Save previous item if exists
            if current_func:
                if in_input_table:
                     item['inputs'] = '\n'.join(input_table_lines)
                data[current_func] = item.copy()

            # Reset for new item
            current_func = match.group(1).strip()
            item = {'desc': '', 'limit': '', 'inputs': ''}
            input_table_lines = []
            in_input_table = False
            looking_for_input_table = False
            continue

        if not current_func:
            continue

        # 2. Capture Description
        match_desc = desc_pattern.match(line)
        if match_desc:
            item['desc'] = match_desc.group(1).strip()
            continue

        # 3. Capture Limit
        match_limit = limit_pattern.match(line)
        if match_limit:
            item['limit'] = match_limit.group(1).strip()
            continue

        # 4. Detect "输入参数" header -> prepare to capture table
        if input_start_pattern.match(line):
            looking_for_input_table = True
            in_input_table = False
            continue
        
        # 5. Detect "输出参数" header -> STOP capturing input table
        if line.startswith('输出参数'):
            if in_input_table:
                item['inputs'] = '\n'.join(input_table_lines)
                in_input_table = False
            looking_for_input_table = False
            continue

        # 6. Capture Input Parameters Table (only if we are looking for it)
        if looking_for_input_table and '|' in line:
            if not in_input_table:
                in_input_table = True
            input_table_lines.append(line)
        elif in_input_table and '|' not in line:
            # If we were in a table and encounter a non-table line (not starting with |)
            # This might be an empty line or something else
            if line.strip() == "":
                # Empty line might end the table, but let's continue looking
                pass
            else:
                # Non-empty, non-table line -> stop capturing
                item['inputs'] = '\n'.join(input_table_lines)
                in_input_table = False
                looking_for_input_table = False


    # Save the last item
    if current_func:
        if in_input_table:
             item['inputs'] = '\n'.join(input_table_lines)
        data[current_func] = item.copy()
        
    logger.info(f"Parsed {len(data)} interfaces from markdown.")
    return data

def enrich_csv(input_csv: str, md_data: Dict[str, Dict[str, str]], output_csv: str):
    if not Path(input_csv).exists():
        logger.error(f"Input CSV not found: {input_csv}")
        return

    logger.info(f"Enriching CSV: {input_csv} -> {output_csv}")
    
    enriched_count = 0
    missing_count = 0
    
    with open(input_csv, 'r', encoding='utf-8') as f_in, \
         open(output_csv, 'w', encoding='utf-8', newline='') as f_out:
        
        reader = csv.DictReader(f_in)
        
        # Define new fieldnames
        # User requested: 子分类,接口名称 (Function),说明 (Description),详细描述, 限量, 输入参数
        # Original keys might vary, let's detect them.
        original_fields = reader.fieldnames
        if not original_fields:
            logger.error("CSV file is empty or missing headers.")
            return

        # Map known headers
        # Expecting: 子分类, 接口名称 (Function), 说明 (Description)
        # We will preserve original headers and append new ones? 
        # User specified exact headers: "子分类,接口名称 (Function),说明 (Description),详细描述, 限量, 输入参数"
        
        new_fields = [
            '子分类', 
            '接口名称 (Function)', 
            '说明 (Description)', 
            '详细描述', 
            '限量', 
            '输入参数'
        ]
        
        writer = csv.DictWriter(f_out, fieldnames=new_fields)
        writer.writeheader()
        
        for row in reader:
            func_name = row.get('接口名称 (Function)', '').strip()
            
            # Lookup in markdown data
            # Try exact match first, then case-insensitive
            info = md_data.get(func_name)
            if not info:
                # Try case insensitive
                for k in md_data:
                    if k.lower() == func_name.lower():
                        info = md_data[k]
                        break
            
            desc_detail = ''
            limit = ''
            input_args = ''
            
            if info:
                enriched_count += 1
                desc_detail = info['desc']
                limit = info['limit']
                input_args = info['inputs']
            else:
                missing_count += 1
                logger.warning(f"Metadata not found for function: {func_name}")

            # Construct new row
            new_row = {
                '子分类': row.get('子分类', ''),
                '接口名称 (Function)': func_name,
                '说明 (Description)': row.get('说明 (Description)', ''),
                '详细描述': desc_detail,
                '限量': limit,
                '输入参数': input_args
            }
            writer.writerow(new_row)
            
    logger.info(f"Processing complete. Enriched: {enriched_count}, Missing: {missing_count}")

def main():
    parser = argparse.ArgumentParser(description="Enrich stock CSV with markdown details.")
    parser.add_argument('--input', required=True, help="Path to input CSV")
    parser.add_argument('--docs', required=True, help="Path to documentation Markdown")
    parser.add_argument('--output', required=True, help="Path to output CSV")
    
    args = parser.parse_args()
    
    md_data = parse_markdown(args.docs)
    enrich_csv(args.input, md_data, args.output)

if __name__ == "__main__":
    main()
