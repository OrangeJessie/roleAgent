#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import json
from typing import List, Dict, Any, Optional
from urllib.parse import quote
import requests
from bs4 import BeautifulSoup
from .retrieve_related import VectorRetriever

class MCPTools:
    """Model Control Protocol Tools - A collection of utility functions for AI model interactions"""
    
    @staticmethod
    def search_local_database(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search the local vector database for relevant information.
        
        Args:
            query (str): The search query
            top_k (int): Number of top results to return
            
        Returns:
            List[Dict[str, Any]]: List of search results with metadata
        """
        try:
            # 使用 VectorRetriever 进行检索
            retriever = VectorRetriever()
            # 更新配置中的最大结果数
            retriever.max_results = top_k
            # 执行检索
            results = retriever.retrieve(query)
            return results
        except Exception as e:
            return [{"error": str(e)}]
    
    @staticmethod
    def baidu_search(query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """Perform a Baidu search and extract relevant information from the results.
        
        Args:
            query (str): Search query
            max_results (int): Maximum number of results to return
            
        Returns:
            List[Dict[str, str]]: List of search results with title and content
        """
        try:
            # Encode the query for URL
            encoded_query = quote(query)
            url = f"https://www.baidu.com/s?wd={encoded_query}"
            
            # Send request with proper headers
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            # Parse results
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # Extract search results (implementation depends on Baidu's HTML structure)
            # This is a simplified example
            for result in soup.find_all('div', class_='result')[:max_results]:
                title = result.find('h3').get_text() if result.find('h3') else ''
                content = result.find('div', class_='content').get_text() if result.find('div', class_='content') else ''
                results.append({
                    "title": title,
                    "content": content
                })
            
            return results
        except Exception as e:
            return [{"error": str(e)}]
    
    @staticmethod
    def open_calculator() -> Dict[str, Any]:
        """Open macOS Calculator application.
        
        Returns:
            Dict[str, Any]: Status of the operation
        """
        try:
            subprocess.Popen(['open', '-a', 'Calculator'])
            return {"status": "success", "message": "Calculator opened successfully"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def open_calendar() -> Dict[str, Any]:
        """Open macOS Calendar application.
        
        Returns:
            Dict[str, Any]: Status of the operation
        """
        try:
            subprocess.Popen(['open', '-a', 'Calendar'])
            return {"status": "success", "message": "Calendar opened successfully"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def open_notes(content: Optional[str] = None) -> Dict[str, Any]:
        """Open macOS Notes application and optionally create a new note.
        
        Args:
            content (Optional[str]): Content to add to a new note
            
        Returns:
            Dict[str, Any]: Status of the operation
        """
        try:
            if content:
                # Create a new note with content using AppleScript
                apple_script = f'''
                tell application "Notes"
                    activate
                    tell account "iCloud"
                        make new note with properties {{body:"{content}"}}
                    end tell
                end tell
                '''
                subprocess.run(['osascript', '-e', apple_script])
                return {"status": "success", "message": "Notes opened with new content"}
            else:
                # Simply open Notes app
                subprocess.Popen(['open', '-a', 'Notes'])
                return {"status": "success", "message": "Notes opened successfully"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
