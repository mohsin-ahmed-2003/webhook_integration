from django.db import models
from django.utils import timezone 
 
class GitHubEvent(models.Model): 
    event_type = models.CharField(max_length=50) # e.g., 'push', 'pull_request' 
    action = models.CharField(max_length=100, null=True, blank=True) # e.g., 'pushed', 'opened', 'closed', 'merged' 
    repo_name = models.CharField(max_length=255, null=True, blank=True) 
    actor = models.CharField(max_length=255, null=True, blank=True) 
    timestamp = models.DateTimeField(null=True, blank=True) 
    received_at = models.DateTimeField(default=timezone.now) # When we received it 
 
    # Specific fields for Push events 
    commit_id = models.CharField(max_length=40, null=True, blank=True) 
    # SHA of the commit 
    branch_name = models.CharField(max_length=255, null=True, blank=True) 
 
    # Specific fields for Pull Request events 
    pull_request_number = models.IntegerField(null=True, blank=True) 
    pull_request_title = models.TextField(null=True, blank=True) 
    base_branch = models.CharField(max_length=255, null=True, blank=True) 
    head_branch = models.CharField(max_length=255, null=True, blank=True) 
    review_state = models.CharField(max_length=50, null=True, blank=True) # For PR reviews 
 
    # Store the full JSON payload 
    payload = models.JSONField() 
 
    class Meta: 
        # Define a MongoDB collection name if you don't want the default 
        db_table = 'github_events_collection' 
        ordering = ['-timestamp'] # Order by latest events 
 
    def __str__(self): 
        return f"{self.event_type} by {self.actor} at {self.timestamp}"
    
    def get_display_text(self): 
        # This method will format the display text for the UI 
        if self.event_type == 'push': 
            return f"Push to {self.branch_name} in {self.repo_name} by {self.actor} (Commit: {self.commit_id[:7]})" 
        elif self.event_type == 'pull_request': 
            if self.action == 'opened': 
                return f"PR #{self.pull_request_number} opened: '{self.pull_request_title}' from {self.head_branch} to {self.base_branch} in {self.repo_name} by {self.actor}" 
            elif self.action == 'closed': 
                return f"PR #{self.pull_request_number} closed: '{self.pull_request_title}' in {self.repo_name} by {self.actor}" 
            elif self.action == 'merged': 
                return f"PR #{self.pull_request_number} merged: '{self.pull_request_title}' from {self.head_branch} to {self.base_branch} in {self.repo_name} by {self.actor}" 
        elif self.event_type == 'pull_request_review': 
            return f"PR Review ({self.review_state}) for PR #{self.pull_request_number} in {self.repo_name} by {self.actor}" 
        return f"Unhandled event: {self.event_type} action {self.action} in {self.repo_name}" 