"""
Thai2Drive API Backend Tests
Tests all backend endpoints for the Norwegian driving theory quiz app
"""
import pytest
import requests
import os

# Use public URL for testing
BASE_URL = "https://norge-quiz-app.preview.emergentagent.com"
API_BASE = f"{BASE_URL}/api"

# Test device ID
TEST_DEVICE_ID = "test_device_thai2drive_123"

class TestDatabaseSeeding:
    """Test database seeding endpoint"""
    
    def test_seed_database(self):
        """POST /api/seed should seed 45 questions"""
        response = requests.post(f"{API_BASE}/seed")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "message" in data or "seeded" in data
        print(f"✓ Seed endpoint response: {data}")


class TestCategories:
    """Test categories endpoint"""
    
    def test_get_categories_returns_5_categories(self):
        """GET /api/categories should return 5 categories"""
        response = requests.get(f"{API_BASE}/categories")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        categories = response.json()
        assert isinstance(categories, list), "Categories should be a list"
        assert len(categories) == 5, f"Expected 5 categories, got {len(categories)}"
        
        # Verify category structure
        for cat in categories:
            assert "name" in cat, "Category should have 'name' field"
            assert "count" in cat, "Category should have 'count' field"
            assert isinstance(cat["count"], int), "Count should be an integer"
        
        category_names = [c["name"] for c in categories]
        expected_categories = ["Traffic Signs", "Road Rules", "Right of Way", "Speed Limits", "Safety"]
        assert set(category_names) == set(expected_categories), f"Expected categories {expected_categories}, got {category_names}"
        
        print(f"✓ Categories: {categories}")


class TestQuestions:
    """Test questions endpoints"""
    
    def test_get_random_questions_count_10(self):
        """GET /api/questions/random?count=10 should return 10 questions"""
        response = requests.get(f"{API_BASE}/questions/random?count=10")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        questions = response.json()
        assert isinstance(questions, list), "Questions should be a list"
        assert len(questions) == 10, f"Expected 10 questions, got {len(questions)}"
        
        # Verify question structure
        for q in questions:
            assert "id" in q, "Question should have 'id'"
            assert "question_text_no" in q, "Question should have Norwegian text"
            assert "question_text_th" in q, "Question should have Thai text"
            assert "question_text_en" in q, "Question should have English text"
            assert "correct_answer" in q, "Question should have correct_answer"
            assert "category" in q, "Question should have category"
            assert q["correct_answer"] in ["A", "B", "C", "D"], "Correct answer should be A, B, C, or D"
        
        print(f"✓ Retrieved {len(questions)} random questions")
    
    def test_get_random_questions_with_category(self):
        """GET /api/questions/random with category filter should work"""
        response = requests.get(f"{API_BASE}/questions/random?count=5&category=Safety")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        questions = response.json()
        assert isinstance(questions, list), "Questions should be a list"
        assert len(questions) <= 5, f"Expected max 5 questions, got {len(questions)}"
        
        # All questions should be from Safety category
        for q in questions:
            assert q["category"] == "Safety", f"Expected Safety category, got {q['category']}"
        
        print(f"✓ Retrieved {len(questions)} Safety questions")


class TestProgress:
    """Test user progress endpoints"""
    
    def test_get_progress_creates_new_if_not_exists(self):
        """GET /api/progress/{device_id} should create new progress if not exists"""
        response = requests.get(f"{API_BASE}/progress/{TEST_DEVICE_ID}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        progress = response.json()
        assert "device_id" in progress, "Progress should have device_id"
        assert progress["device_id"] == TEST_DEVICE_ID
        assert "total_questions_answered" in progress
        assert "correct_answers" in progress
        assert "questions_by_category" in progress
        
        print(f"✓ Progress retrieved: {progress}")
    
    def test_update_progress_correct_answer(self):
        """PUT /api/progress/{device_id}?answered_correct=true&category=Safety should update progress"""
        response = requests.put(
            f"{API_BASE}/progress/{TEST_DEVICE_ID}?answered_correct=true&category=Safety"
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "success" in data or "progress" in data
        
        # Verify progress was updated by fetching it again
        get_response = requests.get(f"{API_BASE}/progress/{TEST_DEVICE_ID}")
        assert get_response.status_code == 200
        
        updated_progress = get_response.json()
        assert updated_progress["total_questions_answered"] > 0, "Total questions should be incremented"
        assert updated_progress["correct_answers"] > 0, "Correct answers should be incremented"
        assert "Safety" in updated_progress["questions_by_category"], "Safety category should exist"
        
        print(f"✓ Progress updated: {updated_progress}")
    
    def test_update_progress_incorrect_answer(self):
        """PUT /api/progress/{device_id}?answered_correct=false&category=Road Rules should update progress"""
        # Get current progress
        before_response = requests.get(f"{API_BASE}/progress/{TEST_DEVICE_ID}")
        before_progress = before_response.json()
        before_total = before_progress["total_questions_answered"]
        before_correct = before_progress["correct_answers"]
        
        # Update with incorrect answer
        response = requests.put(
            f"{API_BASE}/progress/{TEST_DEVICE_ID}?answered_correct=false&category=Road%20Rules"
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Verify progress
        after_response = requests.get(f"{API_BASE}/progress/{TEST_DEVICE_ID}")
        after_progress = after_response.json()
        
        assert after_progress["total_questions_answered"] == before_total + 1, "Total should increment"
        assert after_progress["correct_answers"] == before_correct, "Correct count should not change"
        
        print(f"✓ Progress updated with incorrect answer")


class TestBookmarks:
    """Test bookmarks endpoints"""
    
    def test_create_bookmark(self):
        """POST /api/bookmarks should create a bookmark"""
        # First get a question ID
        questions_response = requests.get(f"{API_BASE}/questions/random?count=1")
        questions = questions_response.json()
        question_id = questions[0]["id"]
        
        # Create bookmark
        response = requests.post(
            f"{API_BASE}/bookmarks",
            json={"device_id": TEST_DEVICE_ID, "question_id": question_id}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        bookmark = response.json()
        assert "id" in bookmark, "Bookmark should have id"
        assert bookmark["device_id"] == TEST_DEVICE_ID
        assert bookmark["question_id"] == question_id
        
        print(f"✓ Bookmark created: {bookmark}")
    
    def test_get_bookmarks(self):
        """GET /api/bookmarks/{device_id} should return bookmarks"""
        response = requests.get(f"{API_BASE}/bookmarks/{TEST_DEVICE_ID}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        bookmarks = response.json()
        assert isinstance(bookmarks, list), "Bookmarks should be a list"
        assert len(bookmarks) > 0, "Should have at least one bookmark from previous test"
        
        print(f"✓ Retrieved {len(bookmarks)} bookmarks")
    
    def test_get_bookmarked_questions(self):
        """GET /api/bookmarked-questions/{device_id} should return full question objects"""
        response = requests.get(f"{API_BASE}/bookmarked-questions/{TEST_DEVICE_ID}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        questions = response.json()
        assert isinstance(questions, list), "Bookmarked questions should be a list"
        
        # Verify question structure
        for q in questions:
            assert "id" in q
            assert "question_text_no" in q
            assert "correct_answer" in q
        
        print(f"✓ Retrieved {len(questions)} bookmarked questions")


class TestQuizAttempts:
    """Test quiz attempts endpoints"""
    
    def test_save_quiz_attempt(self):
        """POST /api/quiz-attempts should save a quiz attempt"""
        attempt_data = {
            "device_id": TEST_DEVICE_ID,
            "mode": "practice",
            "category": "Safety",
            "total_questions": 10,
            "correct_answers": 7,
            "score_percentage": 70.0,
            "passed": None,
            "questions_answered": [
                {"question_id": "q1", "selected_answer": "A", "correct": True},
                {"question_id": "q2", "selected_answer": "B", "correct": False}
            ],
            "started_at": "2026-01-01T10:00:00Z"
        }
        
        response = requests.post(
            f"{API_BASE}/quiz-attempts",
            json=attempt_data
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        attempt = response.json()
        assert "id" in attempt, "Attempt should have id"
        assert attempt["device_id"] == TEST_DEVICE_ID
        assert attempt["mode"] == "practice"
        assert attempt["score_percentage"] == 70.0
        
        print(f"✓ Quiz attempt saved: {attempt['id']}")
    
    def test_get_quiz_attempts(self):
        """GET /api/quiz-attempts/{device_id} should return quiz attempts"""
        response = requests.get(f"{API_BASE}/quiz-attempts/{TEST_DEVICE_ID}?limit=20")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        attempts = response.json()
        assert isinstance(attempts, list), "Attempts should be a list"
        assert len(attempts) > 0, "Should have at least one attempt from previous test"
        
        # Verify attempt structure
        for attempt in attempts:
            assert "id" in attempt
            assert "mode" in attempt
            assert "score_percentage" in attempt
            assert "completed_at" in attempt
        
        print(f"✓ Retrieved {len(attempts)} quiz attempts")


class TestExamMode:
    """Test exam mode specific requirements"""
    
    def test_exam_mode_45_questions(self):
        """Exam mode should return 45 questions"""
        response = requests.get(f"{API_BASE}/questions/random?count=45")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        questions = response.json()
        assert len(questions) == 45, f"Expected 45 questions for exam mode, got {len(questions)}"
        
        print(f"✓ Exam mode: Retrieved {len(questions)} questions")
    
    def test_exam_attempt_with_pass_status(self):
        """Exam attempt should include pass/fail status"""
        attempt_data = {
            "device_id": TEST_DEVICE_ID,
            "mode": "exam",
            "total_questions": 45,
            "correct_answers": 40,
            "score_percentage": 88.89,
            "passed": True,  # 88.89% > 85% threshold
            "questions_answered": [],
            "started_at": "2026-01-01T11:00:00Z"
        }
        
        response = requests.post(
            f"{API_BASE}/quiz-attempts",
            json=attempt_data
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        attempt = response.json()
        assert attempt["passed"] == True, "Exam with 88.89% should be marked as passed"
        
        print(f"✓ Exam attempt saved with pass status: {attempt['passed']}")
