from flask import Blueprint, request, jsonify, send_file, send_from_directory
from datetime import datetime
import json
import os
import pandas as pd
from typing import List, Dict, Any
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_loader import data_loader
import mimetypes
import base64

resources_bp = Blueprint('resources', __name__)

RESOURCES_DIR = os.path.join('data', 'knowledge', 'resources')

def get_file_info(file_path: str) -> Dict[str, Any]:
    """Get information about a file"""
    try:
        stat = os.stat(file_path)
        file_size = stat.st_size
        modified_time = datetime.fromtimestamp(stat.st_mtime)
        
        # Get file extension
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        # Determine file type
        file_type = 'unknown'
        if ext in ['.csv']:
            file_type = 'csv'
        elif ext in ['.json']:
            file_type = 'json'
        elif ext in ['.xlsx', '.xls']:
            file_type = 'excel'
        elif ext in ['.pdf']:
            file_type = 'pdf'
        elif ext in ['.docx', '.doc']:
            file_type = 'word'
        elif ext in ['.txt']:
            file_type = 'text'
        elif ext in ['.md']:
            file_type = 'markdown'
        elif ext in ['.png', '.jpg', '.jpeg', '.gif']:
            file_type = 'image'
        
        return {
            'size': file_size,
            'modified': modified_time.isoformat(),
            'extension': ext,
            'type': file_type,
            'mime_type': mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
        }
    except Exception as e:
        return {
            'size': 0,
            'modified': None,
            'extension': '',
            'type': 'unknown',
            'mime_type': 'application/octet-stream',
            'error': str(e)
        }

@resources_bp.route('/api/resources', methods=['GET'])
def get_resources():
    """Get list of all resource files"""
    try:
        if not os.path.exists(RESOURCES_DIR):
            return jsonify({
                "success": True,
                "data": [],
                "message": "Resources directory not found"
            })
        
        files = []
        for filename in os.listdir(RESOURCES_DIR):
            file_path = os.path.join(RESOURCES_DIR, filename)
            if os.path.isfile(file_path):
                file_info = get_file_info(file_path)
                files.append({
                    'name': filename,
                    'path': file_path,
                    'size': file_info['size'],
                    'modified': file_info['modified'],
                    'extension': file_info['extension'],
                    'type': file_info['type'],
                    'mime_type': file_info['mime_type']
                })
        
        # Sort files by name
        files.sort(key=lambda x: x['name'])
        
        return jsonify({
            "success": True,
            "data": files
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@resources_bp.route('/api/resources/<filename>', methods=['GET'])
def get_resource_file(filename):
    """Get a specific resource file"""
    try:
        file_path = os.path.join(RESOURCES_DIR, filename)
        
        if not os.path.exists(file_path):
            return jsonify({
                "success": False,
                "error": "File not found"
            }), 404
        
        if not os.path.isfile(file_path):
            return jsonify({
                "success": False,
                "error": "Not a file"
            }), 400
        
        # Get file info
        file_info = get_file_info(file_path)
        
        return jsonify({
            "success": True,
            "data": {
                'name': filename,
                'path': file_path,
                'size': file_info['size'],
                'modified': file_info['modified'],
                'extension': file_info['extension'],
                'type': file_info['type'],
                'mime_type': file_info['mime_type']
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@resources_bp.route('/api/resources/<filename>/download', methods=['GET'])
def download_resource_file(filename):
    """Download a resource file"""
    try:
        file_path = os.path.join(RESOURCES_DIR, filename)
        
        if not os.path.exists(file_path):
            return jsonify({
                "success": False,
                "error": "File not found"
            }), 404
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@resources_bp.route('/api/resources/<filename>/view', methods=['GET'])
def view_resource_file(filename):
    """View content of a resource file"""
    try:
        file_path = os.path.join(RESOURCES_DIR, filename)
        
        if not os.path.exists(file_path):
            return jsonify({
                "success": False,
                "error": "File not found"
            }), 404
        
        file_info = get_file_info(file_path)
        file_type = file_info['type']
        
        content = None
        parsed_content = None
        
        # Read file content based on type
        if file_type == 'csv':
            try:
                df = pd.read_csv(file_path)
                content = df.to_string(index=False)
                parsed_content = df.to_dict('records')
            except Exception as e:
                content = f"Error reading CSV: {str(e)}"
        
        elif file_type == 'json':
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    content = json.dumps(data, indent=2)
                    parsed_content = data
            except Exception as e:
                content = f"Error reading JSON: {str(e)}"
        
        elif file_type == 'excel':
            try:
                df = pd.read_excel(file_path)
                content = df.to_string(index=False)
                parsed_content = df.to_dict('records')
            except Exception as e:
                content = f"Error reading Excel: {str(e)}"
        
        elif file_type in ['text', 'markdown']:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                content = f"Error reading text file: {str(e)}"
        
        elif file_type == 'pdf':
            content = "PDF files cannot be displayed as text. Please download the file to view it."
        
        elif file_type == 'word':
            content = "Word documents cannot be displayed as text. Please download the file to view it."
        
        elif file_type == 'image':
            try:
                with open(file_path, 'rb') as f:
                    image_data = base64.b64encode(f.read()).decode('utf-8')
                    content = f"data:{file_info['mime_type']};base64,{image_data}"
            except Exception as e:
                content = f"Error reading image: {str(e)}"
        
        else:
            content = "File type not supported for viewing. Please download the file."
        
        return jsonify({
            "success": True,
            "data": {
                'name': filename,
                'type': file_type,
                'content': content,
                'parsed_content': parsed_content,
                'size': file_info['size'],
                'modified': file_info['modified']
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@resources_bp.route('/api/resources/stats', methods=['GET'])
def get_resources_stats():
    """Get statistics about resource files"""
    try:
        if not os.path.exists(RESOURCES_DIR):
            return jsonify({
                "success": True,
                "data": {
                    "total_files": 0,
                    "total_size": 0,
                    "file_types": {}
                }
            })
        
        total_files = 0
        total_size = 0
        file_types = {}
        
        for filename in os.listdir(RESOURCES_DIR):
            file_path = os.path.join(RESOURCES_DIR, filename)
            if os.path.isfile(file_path):
                total_files += 1
                file_info = get_file_info(file_path)
                total_size += file_info['size']
                
                file_type = file_info['type']
                if file_type in file_types:
                    file_types[file_type] += 1
                else:
                    file_types[file_type] = 1
        
        return jsonify({
            "success": True,
            "data": {
                "total_files": total_files,
                "total_size": total_size,
                "file_types": file_types
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500
