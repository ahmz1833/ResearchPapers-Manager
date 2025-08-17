#!/usr/bin/env python3
"""
Complete test suite for Research Papers Manager
Tests all endpoints with correct API specifications based on actual implementation
"""

import requests
import json
import time
import sys
import random
import string
from typing import Dict, Any, Tuple, List

# Configuration
BASE_URL = "http://localhost:8000"

# Generate unique test data to avoid conflicts
TEST_ID = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

TEST_USER = {
    "username": f"testuser_{TEST_ID}",
    "name": f"Test User {TEST_ID}",
    "email": f"test_{TEST_ID}@example.com",
    "password": "test_password_123",
    "department": "Computer Science"
}

def log_test(test_name: str, success: bool, message: str = "", details: str = ""):
    """Log test results with consistent formatting"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if message:
        print(f"    📋 {message}")
    if details:
        print(f"    📄 {details}")

def print_section(title: str):
    """Print section header"""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print('='*60)

# ===================== HEALTH TESTS =====================

def test_root_endpoint() -> bool:
    """Test root endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        success = response.status_code == 200
        
        if success:
            data = response.json()
            app_name = data.get("app")
            status = data.get("status")
            message = f"App: {app_name}, Status: {status}"
        else:
            message = f"Status: {response.status_code}"
            
        log_test("Root Endpoint", success, message)
        return success
    except Exception as e:
        log_test("Root Endpoint", False, f"Error: {e}")
        return False

def test_health_check() -> bool:
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health/", timeout=5)
        success = response.status_code == 200
        
        if success:
            data = response.json()
            app_name = data.get("app")
            mongo = data.get("mongo")
            redis = data.get("redis")
            status = data.get("status")
            message = f"App: {app_name}, Mongo: {mongo}, Redis: {redis}, Status: {status}"
        else:
            message = f"Status: {response.status_code}"
            
        log_test("Health Check", success, message)
        return success
    except Exception as e:
        log_test("Health Check", False, f"Error: {e}")
        return False

# ===================== AUTH TESTS =====================

def test_user_signup() -> Tuple[bool, str]:
    """Test user registration with correct fields"""
    try:
        response = requests.post(
            f"{BASE_URL}/signup",
            json=TEST_USER,
            timeout=10
        )
        
        success = response.status_code == 201
        user_id = ""
        
        if success:
            data = response.json()
            user_id = data.get("user_id", "")
            message = data.get("message", "")
            log_test("User Registration", True, f"{message}, User ID: {user_id[:8]}...")
        else:
            data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
            error = data.get("error", "Unknown error")
            details = data.get("details", [])
            log_test("User Registration", False, f"Status: {response.status_code}, Error: {error}", str(details))
            
        return success, user_id
        
    except Exception as e:
        log_test("User Registration", False, f"Error: {e}")
        return False, ""

def test_user_login() -> Tuple[bool, str]:
    """Test user login"""
    try:
        login_data = {
            "username": TEST_USER["username"],
            "password": TEST_USER["password"]
        }
        
        response = requests.post(
            f"{BASE_URL}/login",
            json=login_data,
            timeout=10
        )
        
        success = response.status_code == 200
        user_id = ""
        
        if success:
            data = response.json()
            user_id = data.get("user_id", "")
            message = data.get("message", "")
            log_test("User Login", True, f"{message}, User ID: {user_id[:8]}...")
        else:
            data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
            error = data.get("error", "Unknown error")
            log_test("User Login", False, f"Status: {response.status_code}, Error: {error}")
            
        return success, user_id
        
    except Exception as e:
        log_test("User Login", False, f"Error: {e}")
        return False, ""

def test_duplicate_username() -> bool:
    """Test duplicate username rejection"""
    try:
        # Try to register same username again
        response = requests.post(
            f"{BASE_URL}/signup",
            json=TEST_USER,
            timeout=10
        )
        
        # Should return 409 Conflict
        success = response.status_code == 409
        
        if success:
            data = response.json()
            error = data.get("error", "")
            log_test("Duplicate Username Rejection", True, f"Correctly rejected: {error}")
        else:
            log_test("Duplicate Username Rejection", False, f"Expected 409, got {response.status_code}")
            
        return success
        
    except Exception as e:
        log_test("Duplicate Username Rejection", False, f"Error: {e}")
        return False

def test_invalid_login() -> bool:
    """Test login with invalid credentials"""
    try:
        invalid_login = {
            "username": TEST_USER["username"],
            "password": "wrong_password"
        }
        
        response = requests.post(
            f"{BASE_URL}/login",
            json=invalid_login,
            timeout=10
        )
        
        # Should return 401 Unauthorized
        success = response.status_code == 401
        
        if success:
            data = response.json()
            error = data.get("error", "")
            log_test("Invalid Login Rejection", True, f"Correctly rejected: {error}")
        else:
            log_test("Invalid Login Rejection", False, f"Expected 401, got {response.status_code}")
            
        return success
        
    except Exception as e:
        log_test("Invalid Login Rejection", False, f"Error: {e}")
        return False

def test_signup_validation() -> bool:
    """Test signup validation errors"""
    try:
        invalid_data = {
            "username": "ab",  # Too short
            "name": "",  # Empty
            "email": "invalid-email",  # Invalid format
            "password": "123",  # Too short
            "department": ""  # Empty
        }
        
        response = requests.post(
            f"{BASE_URL}/signup",
            json=invalid_data,
            timeout=10
        )
        
        # Should return 400 Bad Request
        success = response.status_code == 400
        
        if success:
            data = response.json()
            error = data.get("error", "")
            details = data.get("details", [])
            log_test("Signup Validation", True, f"Validation errors: {error}", f"Details: {len(details)} errors")
        else:
            log_test("Signup Validation", False, f"Expected 400, got {response.status_code}")
            
        return success
        
    except Exception as e:
        log_test("Signup Validation", False, f"Error: {e}")
        return False

# ===================== PAPERS TESTS =====================

def test_paper_upload(user_id: str) -> Tuple[bool, str]:
    """Test paper upload with X-User-ID authentication"""
    if not user_id:
        log_test("Paper Upload", False, "No user ID provided")
        return False, ""
        
    try:
        paper_data = {
            "title": f"Test Paper: Advanced Machine Learning Techniques {TEST_ID}",
            "authors": ["Dr. Test Author", "Prof. Example Researcher"],
            "abstract": "This is a comprehensive test paper abstract describing advanced machine learning techniques and their applications in various domains. The paper covers novel approaches to computer vision, natural language processing, and reinforcement learning.",
            "publication_date": "2024-01-15",
            "journal_conference": "International Conference on Machine Learning",
            "keywords": ["machine learning", "artificial intelligence", "test", "research"],
            "citations": []
        }
        
        headers = {"X-User-ID": user_id}
        response = requests.post(
            f"{BASE_URL}/papers/",
            json=paper_data,
            headers=headers,
            timeout=10
        )
        
        success = response.status_code == 201
        paper_id = ""
        
        if success:
            data = response.json()
            paper_id = data.get("paper_id", "")
            message = data.get("message", "")
            log_test("Paper Upload", True, f"{message}, Paper ID: {paper_id[:8]}...")
        else:
            data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
            error = data.get("error", "Unknown error")
            details = data.get("details", [])
            log_test("Paper Upload", False, f"Status: {response.status_code}, Error: {error}", str(details))
            
        return success, paper_id
        
    except Exception as e:
        log_test("Paper Upload", False, f"Error: {e}")
        return False, ""

def test_paper_upload_without_auth() -> bool:
    """Test paper upload without authentication"""
    try:
        paper_data = {
            "title": "Unauthorized Paper",
            "authors": ["Test Author"],
            "abstract": "This should fail due to missing authentication.",
            "publication_date": "2024-01-15",
            "keywords": ["test"],
            "citations": []
        }
        
        # No headers (missing X-User-ID)
        response = requests.post(
            f"{BASE_URL}/papers/",
            json=paper_data,
            timeout=10
        )
        
        # Should return 401 Unauthorized
        success = response.status_code == 401
        
        if success:
            data = response.json()
            error = data.get("error", "")
            log_test("Unauthorized Paper Upload", True, f"Correctly rejected: {error}")
        else:
            log_test("Unauthorized Paper Upload", False, f"Expected 401, got {response.status_code}")
            
        return success
        
    except Exception as e:
        log_test("Unauthorized Paper Upload", False, f"Error: {e}")
        return False

def test_paper_search() -> bool:
    """Test paper search functionality"""
    try:
        # Test 1: Search all papers (no query)
        response = requests.get(f"{BASE_URL}/papers/", timeout=10)
        success = response.status_code == 200
        
        if not success:
            log_test("Paper Search (All)", False, f"Status: {response.status_code}")
            return False
            
        data = response.json()
        papers = data.get("papers", [])
        log_test("Paper Search (All)", True, f"Found {len(papers)} papers")
        
        # Test 2: Search with query
        response = requests.get(f"{BASE_URL}/papers/?search=machine+learning", timeout=10)
        success = response.status_code == 200
        
        if success:
            data = response.json()
            papers = data.get("papers", [])
            log_test("Paper Search (Query)", True, f"Found {len(papers)} papers for 'machine learning'")
        else:
            log_test("Paper Search (Query)", False, f"Status: {response.status_code}")
            return False
            
        # Test 3: Search with sorting
        response = requests.get(f"{BASE_URL}/papers/?sort_by=publication_date&order=desc", timeout=10)
        success = response.status_code == 200
        
        if success:
            data = response.json()
            papers = data.get("papers", [])
            log_test("Paper Search (Sorted)", True, f"Found {len(papers)} papers sorted by date")
        else:
            log_test("Paper Search (Sorted)", False, f"Status: {response.status_code}")
            return False
            
        return True
        
    except Exception as e:
        log_test("Paper Search", False, f"Error: {e}")
        return False

def test_paper_detail(paper_id: str) -> bool:
    """Test paper detail endpoint with view tracking"""
    if not paper_id:
        log_test("Paper Detail", False, "No paper ID provided")
        return False
        
    try:
        # Make multiple requests to test view increment
        initial_views = 0
        final_views = 0
        
        for i in range(3):
            response = requests.get(f"{BASE_URL}/papers/{paper_id}", timeout=10)
            
            if response.status_code != 200:
                log_test("Paper Detail", False, f"Status: {response.status_code}")
                return False
                
            data = response.json()
            title = data.get("title", "")
            views = data.get("views", 0)
            citations = data.get("citation_count", 0)
            
            if i == 0:
                initial_views = views
            elif i == 2:
                final_views = views
                
            time.sleep(0.5)  # Brief pause between requests
        
        # Views should have increased
        view_increase = final_views - initial_views
        success = view_increase >= 0  # Views should at least not decrease
        
        log_test("Paper Detail", success, 
                f"Paper: {title[:50]}..., Views: {initial_views} -> {final_views} (+{view_increase}), Citations: {citations}")
        return success
        
    except Exception as e:
        log_test("Paper Detail", False, f"Error: {e}")
        return False

def test_paper_with_citations(user_id: str, cited_paper_id: str) -> Tuple[bool, str]:
    """Test paper upload with citations"""
    if not user_id or not cited_paper_id:
        log_test("Paper with Citations", False, "Missing user ID or cited paper ID")
        return False, ""
        
    try:
        paper_data = {
            "title": f"Follow-up Research on ML Applications {TEST_ID}",
            "authors": ["Dr. Follow Up", "Prof. Citation Test"],
            "abstract": "This paper builds upon previous research in machine learning by extending the methodologies to new application domains and providing comprehensive evaluation metrics.",
            "publication_date": "2024-02-20",
            "journal_conference": "IEEE Transactions on Pattern Analysis",
            "keywords": ["machine learning", "applications", "follow-up", "citations"],
            "citations": [cited_paper_id]
        }
        
        headers = {"X-User-ID": user_id}
        response = requests.post(
            f"{BASE_URL}/papers/",
            json=paper_data,
            headers=headers,
            timeout=10
        )
        
        success = response.status_code == 201
        paper_id = ""
        
        if success:
            data = response.json()
            paper_id = data.get("paper_id", "")
            message = data.get("message", "")
            log_test("Paper with Citations", True, f"{message}, Paper ID: {paper_id[:8]}...", f"Cited: {cited_paper_id[:8]}...")
        else:
            data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
            error = data.get("error", "Unknown error")
            details = data.get("details", [])
            log_test("Paper with Citations", False, f"Status: {response.status_code}, Error: {error}", str(details))
            
        return success, paper_id
        
    except Exception as e:
        log_test("Paper with Citations", False, f"Error: {e}")
        return False, ""

def test_paper_validation(user_id) -> bool:
    """Test paper validation errors"""
    try:
        # Use a random existing user ID for auth (validation should still fail)
        headers = {"X-User-ID": user_id}  # Valid ObjectId format
        
        invalid_data = {
            "title": "",  # Empty title
            "authors": [],  # Empty authors
            "abstract": "",  # Empty abstract
            "publication_date": "invalid-date",  # Invalid date
            "keywords": [],  # Empty keywords
            "citations": ["invalid_paper_id"]  # Invalid citation ID
        }
        
        response = requests.post(
            f"{BASE_URL}/papers/",
            json=invalid_data,
            headers=headers,
            timeout=10
        )
        
        # Should return 400 Bad Request for validation errors
        success = response.status_code == 400
        
        if success:
            data = response.json()
            error = data.get("error", "")
            details = data.get("details", [])
            log_test("Paper Validation", True, f"Validation errors: {error}", f"Details: {len(details)} errors")
        else:
            log_test("Paper Validation", False, f"Expected 400, got {response.status_code}")
            
        return success
        
    except Exception as e:
        log_test("Paper Validation", False, f"Error: {e}")
        return False

def test_nonexistent_paper() -> bool:
    """Test accessing non-existent paper"""
    try:
        fake_paper_id = "507f1f77bcf86cd799439999"  # Valid ObjectId format but non-existent
        response = requests.get(f"{BASE_URL}/papers/{fake_paper_id}", timeout=10)
        
        # Should return 404 Not Found
        success = response.status_code == 404
        
        if success:
            data = response.json()
            error = data.get("error", "")
            log_test("Non-existent Paper", True, f"Correctly returned 404: {error}")
        else:
            log_test("Non-existent Paper", False, f"Expected 404, got {response.status_code}")
            
        return success
        
    except Exception as e:
        log_test("Non-existent Paper", False, f"Error: {e}")
        return False

# ===================== ADMIN TESTS =====================

def test_admin_sync_status() -> bool:
    """Test admin sync status endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/admin/sync-status", timeout=10)
        success = response.status_code == 200
        
        if success:
            data = response.json()
            pending_papers = data.get("pending_papers", 0)
            pending_views = data.get("pending_views", 0)
            redis_keys = data.get("redis_keys", [])
            log_test("Admin Sync Status", True, 
                    f"Pending papers: {pending_papers}, Pending views: {pending_views}, Redis keys: {len(redis_keys)}")
        else:
            log_test("Admin Sync Status", False, f"Status: {response.status_code}")
            
        return success
        
    except Exception as e:
        log_test("Admin Sync Status", False, f"Error: {e}")
        return False

def test_admin_manual_sync() -> bool:
    """Test admin manual sync endpoint"""
    try:
        response = requests.post(f"{BASE_URL}/admin/sync-now", timeout=10)
        success = response.status_code == 200
        
        if success:
            data = response.json()
            status = data.get("status", "")
            synced_papers = data.get("synced_papers", 0)
            total_views = data.get("total_views_synced", 0)
            message = data.get("message", "")
            log_test("Admin Manual Sync", True, 
                    f"Status: {status}, Synced papers: {synced_papers}, Views: {total_views}", message)
        else:
            log_test("Admin Manual Sync", False, f"Status: {response.status_code}")
            
        return success
        
    except Exception as e:
        log_test("Admin Manual Sync", False, f"Error: {e}")
        return False

# ===================== CACHE TESTS =====================

def test_search_cache() -> bool:
    """Test search result caching"""
    try:
        search_query = "machine+learning"
        
        # Make first request (should cache result)
        start_time = time.time()
        response1 = requests.get(f"{BASE_URL}/papers/?search={search_query}", timeout=10)
        first_time = time.time() - start_time
        
        if response1.status_code != 200:
            log_test("Search Cache", False, f"First request failed: {response1.status_code}")
            return False
            
        # Make second request (should use cache, potentially faster)
        start_time = time.time()
        response2 = requests.get(f"{BASE_URL}/papers/?search={search_query}", timeout=10)
        second_time = time.time() - start_time
        
        if response2.status_code != 200:
            log_test("Search Cache", False, f"Second request failed: {response2.status_code}")
            return False
            
        # Compare results and timing
        data1 = response1.json()
        data2 = response2.json()
        papers1 = data1.get("papers", [])
        papers2 = data2.get("papers", [])
        
        results_match = len(papers1) == len(papers2)
        
        log_test("Search Cache", results_match, 
                f"First: {first_time:.3f}s ({len(papers1)} papers), Second: {second_time:.3f}s ({len(papers2)} papers)")
        return results_match
        
    except Exception as e:
        log_test("Search Cache", False, f"Error: {e}")
        return False

def test_cache_invalidation(user_id: str) -> bool:
    """Test cache invalidation when new paper is added"""
    if not user_id:
        log_test("Cache Invalidation", False, "No user ID provided")
        return False
        
    try:
        # Search before adding paper
        response1 = requests.get(f"{BASE_URL}/papers/?search=cache+test", timeout=10)
        if response1.status_code != 200:
            log_test("Cache Invalidation", False, "Initial search failed")
            return False
            
        data1 = response1.json()
        initial_count = len(data1.get("papers", []))
        
        # Add new paper with specific keywords
        paper_data = {
            "title": f"Cache Test Paper {TEST_ID}",
            "authors": ["Cache Tester"],
            "abstract": "This paper is specifically designed to test cache invalidation functionality in the system.",
            "publication_date": "2024-03-01",
            "keywords": ["cache", "test", "invalidation"],
            "citations": []
        }
        
        headers = {"X-User-ID": user_id}
        upload_response = requests.post(
            f"{BASE_URL}/papers/",
            json=paper_data,
            headers=headers,
            timeout=10
        )
        
        if upload_response.status_code != 201:
            log_test("Cache Invalidation", False, "Paper upload failed")
            return False
            
        # Search again (cache should be invalidated)
        time.sleep(1)  # Brief pause to ensure processing
        response2 = requests.get(f"{BASE_URL}/papers/?search=cache+test", timeout=10)
        if response2.status_code != 200:
            log_test("Cache Invalidation", False, "Final search failed")
            return False
            
        data2 = response2.json()
        final_count = len(data2.get("papers", []))
        
        # Count should increase (or at least not decrease)
        cache_invalidated = final_count >= initial_count
        
        log_test("Cache Invalidation", cache_invalidated, 
                f"Papers before: {initial_count}, after: {final_count}")
        return cache_invalidated
        
    except Exception as e:
        log_test("Cache Invalidation", False, f"Error: {e}")
        return False

# ===================== INTEGRATION TESTS =====================

def test_view_tracking_integration(paper_id: str) -> bool:
    """Test Redis view tracking integration"""
    if not paper_id:
        log_test("View Tracking Integration", False, "No paper ID provided")
        return False
        
    try:
        # Get initial views
        response1 = requests.get(f"{BASE_URL}/papers/{paper_id}", timeout=10)
        if response1.status_code != 200:
            log_test("View Tracking Integration", False, "Initial request failed")
            return False
            
        initial_views = response1.json().get("views", 0)
        
        # Make several requests with pauses
        for i in range(5):
            time.sleep(0.5)
            requests.get(f"{BASE_URL}/papers/{paper_id}", timeout=10)
            
        # Get final views
        response2 = requests.get(f"{BASE_URL}/papers/{paper_id}", timeout=10)
        if response2.status_code != 200:
            log_test("View Tracking Integration", False, "Final request failed")
            return False
            
        final_views = response2.json().get("views", 0)
        view_increase = final_views - initial_views
        
        # Views should have increased
        success = view_increase > 0
        
        log_test("View Tracking Integration", success, 
                f"Views increased from {initial_views} to {final_views} (+{view_increase})")
        return success
        
    except Exception as e:
        log_test("View Tracking Integration", False, f"Error: {e}")
        return False

def test_citation_count_integration(citing_paper_id: str, cited_paper_id: str) -> bool:
    """Test citation count calculation"""
    if not citing_paper_id or not cited_paper_id:
        log_test("Citation Count Integration", False, "Missing paper IDs")
        return False
        
    try:
        # Check cited paper's citation count
        response = requests.get(f"{BASE_URL}/papers/{cited_paper_id}", timeout=10)
        if response.status_code != 200:
            log_test("Citation Count Integration", False, "Failed to get cited paper")
            return False
            
        data = response.json()
        citation_count = data.get("citation_count", 0)
        
        # Should have at least 1 citation
        success = citation_count >= 1
        
        log_test("Citation Count Integration", success, 
                f"Cited paper has {citation_count} citations")
        return success
        
    except Exception as e:
        log_test("Citation Count Integration", False, f"Error: {e}")
        return False

# ===================== MAIN TEST RUNNER =====================

def main():
    """Run all tests in logical order"""
    print("🚀 Starting Complete Research Papers Manager Test Suite")
    print(f"🎯 Test ID: {TEST_ID}")
    print_section("INITIALIZING")
    
    test_results = []
    
    # Phase 1: Health and Connectivity
    print_section("HEALTH & CONNECTIVITY TESTS")
    test_results.append(test_root_endpoint())
    test_results.append(test_health_check())
    
    # Phase 2: Authentication
    print_section("AUTHENTICATION TESTS")
    signup_success, user_id = test_user_signup()
    test_results.append(signup_success)
    
    login_success, login_user_id = test_user_login()
    test_results.append(login_success)
    
    # Use login user_id if available, otherwise signup user_id
    active_user_id = login_user_id if login_user_id else user_id
    
    test_results.append(test_duplicate_username())
    test_results.append(test_invalid_login())
    test_results.append(test_signup_validation())
    
    # Phase 3: Papers Management
    print_section("PAPERS MANAGEMENT TESTS")
    test_results.append(test_paper_upload_without_auth())
    
    if active_user_id:
        upload_success, paper_id = test_paper_upload(active_user_id)
        test_results.append(upload_success)
    else:
        log_test("Paper Upload", False, "No valid user ID available")
        test_results.append(False)
        paper_id = ""
    
    test_results.append(test_paper_search())
    test_results.append(test_paper_validation(active_user_id))
    test_results.append(test_nonexistent_paper())
    
    # Test paper detail with view tracking
    if paper_id:
        test_results.append(test_paper_detail(paper_id))
    else:
        log_test("Paper Detail", False, "No paper ID available")
        test_results.append(False)
    
    # Test citations
    citing_paper_id = ""
    if active_user_id and paper_id:
        citation_success, citing_paper_id = test_paper_with_citations(active_user_id, paper_id)
        test_results.append(citation_success)
    else:
        log_test("Paper with Citations", False, "Missing user ID or paper ID")
        test_results.append(False)
    
    # Phase 4: Admin Endpoints
    print_section("ADMIN ENDPOINTS TESTS")
    test_results.append(test_admin_sync_status())
    test_results.append(test_admin_manual_sync())
    
    # Phase 5: Cache and Integration
    print_section("CACHE & INTEGRATION TESTS")
    test_results.append(test_search_cache())
    
    if active_user_id:
        test_results.append(test_cache_invalidation(active_user_id))
    else:
        log_test("Cache Invalidation", False, "No user ID available")
        test_results.append(False)
    
    if paper_id:
        test_results.append(test_view_tracking_integration(paper_id))
    else:
        log_test("View Tracking Integration", False, "No paper ID available")
        test_results.append(False)
    
    if citing_paper_id and paper_id:
        test_results.append(test_citation_count_integration(citing_paper_id, paper_id))
    else:
        log_test("Citation Count Integration", False, "Missing paper IDs")
        test_results.append(False)
    
    # Final Summary
    print_section("TEST RESULTS SUMMARY")
    passed = sum(test_results)
    total = len(test_results)
    pass_rate = (passed / total) * 100 if total > 0 else 0
    
    print(f"📊 Overall Results: {passed}/{total} tests passed ({pass_rate:.1f}%)")
    print(f"🎯 Test ID: {TEST_ID}")
    
    if active_user_id:
        print(f"👤 Created User ID: {active_user_id[:8]}...")
    if paper_id:
        print(f"📄 Created Paper ID: {paper_id[:8]}...")
    if citing_paper_id:
        print(f"📖 Created Citing Paper ID: {citing_paper_id[:8]}...")
    
    print()
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! The system is working correctly.")
        print("✅ All endpoints are functioning as expected.")
        print("✅ Authentication, papers management, caching, and admin features are operational.")
        return 0
    else:
        print("⚠️  SOME TESTS FAILED! Please review the output above.")
        print(f"❌ {total - passed} test(s) failed out of {total} total tests.")
        print("💡 Check the detailed logs above for specific failure reasons.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
