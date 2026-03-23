"""Test suite for Mergington High School Activities API"""
import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_all_activities_returns_success(self, client, fresh_activities):
        """Test that all activities are returned successfully"""
        # Arrange
        expected_activities = fresh_activities
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
        assert response.json() == expected_activities
        assert len(response.json()) == 3
    
    def test_get_activities_includes_participant_count(self, client, fresh_activities):
        """Test that activity responses include participant information"""
        # Arrange
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        assert "Chess Club" in activities
        assert "participants" in activities["Chess Club"]
        assert len(activities["Chess Club"]["participants"]) == 2


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_student_succeeds(self, client, fresh_activities):
        """Test successfully signing up a new student for an activity"""
        # Arrange
        activity_name = "Gym Class"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity_name}"
        assert email in fresh_activities[activity_name]["participants"]
    
    def test_signup_duplicate_student_fails(self, client, fresh_activities):
        """Test that signing up an already-registered student returns error"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]
    
    def test_signup_nonexistent_activity_fails(self, client, fresh_activities):
        """Test that signing up for a non-existent activity returns error"""
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_updates_participant_list(self, client, fresh_activities):
        """Test that signup correctly updates the participant list"""
        # Arrange
        activity_name = "Gym Class"
        email = "student1@mergington.edu"
        initial_count = len(fresh_activities[activity_name]["participants"])
        
        # Act
        client.post(f"/activities/{activity_name}/signup", params={"email": email})
        updated_count = len(fresh_activities[activity_name]["participants"])
        
        # Assert
        assert updated_count == initial_count + 1
        assert email in fresh_activities[activity_name]["participants"]


class TestUnregister:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_existing_student_succeeds(self, client, fresh_activities):
        """Test successfully unregistering a student from an activity"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
        assert email not in fresh_activities[activity_name]["participants"]
    
    def test_unregister_nonexistent_student_fails(self, client, fresh_activities):
        """Test that unregistering a student not in the activity returns error"""
        # Arrange
        activity_name = "Gym Class"
        email = "notregistered@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]
    
    def test_unregister_nonexistent_activity_fails(self, client, fresh_activities):
        """Test that unregistering from a non-existent activity returns error"""
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_unregister_updates_participant_list(self, client, fresh_activities):
        """Test that unregister correctly updates the participant list"""
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        initial_count = len(fresh_activities[activity_name]["participants"])
        
        # Act
        client.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        updated_count = len(fresh_activities[activity_name]["participants"])
        
        # Assert
        assert updated_count == initial_count - 1
        assert email not in fresh_activities[activity_name]["participants"]


class TestRootRoute:
    """Tests for GET / endpoint"""
    
    def test_root_redirects_to_static(self, client):
        """Test that root path redirects to static HTML"""
        # Arrange
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
