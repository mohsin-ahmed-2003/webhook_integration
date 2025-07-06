import json 
from django.http import JsonResponse 
from django.views.decorators.csrf import csrf_exempt 
from django.views.decorators.http import require_POST 
from .models import GitHubEvent
from django.utils import timezone
from django.shortcuts import render 
from .models import GitHubEvent 
from django.core.paginator import Paginator

@csrf_exempt # CSRF exemption is crucial for webhooks 
@require_POST # Only accept POST requests 
def github_webhook_receiver(request): 
    # Verify GitHub Signature (Recommended for production) 
    # See: https://docs.github.com/en/developers/webhooks-and-events/webhooks/securing-your-webhooks 
 
    if request.headers.get('X-GitHub-Event'): 
        event_type = request.headers.get('X-GitHub-Event') 
        payload = json.loads(request.body.decode('utf-8')) 
 
        # Extract relevant data based on event type 
        # This is a simplified example; you'll need to parse the payload 
        # more thoroughly for different event types. 
 
        event_data = { 
            'event_type': event_type, 
            'received_at': timezone.now(), 
            'payload': payload, # Store the full payload for flexibility 
        }
    
     # For Push events 
        if event_type == 'push': 
            # Example: Extracting commit and branch info 
            commit_id = payload.get('after') 
            repo_name = payload['repository']['full_name'] 
            branch_ref = payload['ref'] # e.g., "refs/heads/main" 
            branch_name = branch_ref.split('/')[-1] 
            actor = payload['pusher']['name'] 
            timestamp = payload['head_commit']['timestamp'] if payload.get('head_commit') else None 
            event_data.update({ 
            'action': 'pushed', 
            'repo_name': repo_name, 
            'branch_name': branch_name, 
            'actor': actor, 
            'timestamp': timestamp, 
            'commit_id': commit_id, 
        })
            
        elif event_type == 'pull_request': 
            action = payload.get('action') # 'opened', 'closed', 'reopened', 'assigned', etc. 
            if action in ['opened', 'closed', 'reopened', 'merged']: # Focus on relevant actions 
                repo_name = payload['repository']['full_name'] 
                pr_number = payload['number'] 
                pr_title = payload['pull_request']['title'] 
                actor = payload['sender']['login'] 
                base_branch = payload['pull_request']['base']['ref'] 
                head_branch = payload['pull_request']['head']['ref'] 
                timestamp = payload['pull_request']['updated_at'] if action != 'closed' else payload['pull_request']['closed_at'] 
                event_data.update({ 
                    'action': action, 
                    'repo_name': repo_name, 
                    'actor': actor, 
                    'timestamp': timestamp, 
                    'pull_request_number': pr_number, 
                    'pull_request_title': pr_title, 
                    'base_branch': base_branch, 
                    'head_branch': head_branch, 
                }) 
        elif event_type == 'pull_request_review': 
            action = payload.get('action') # 'submitted', 'dismissed', 'edited' 
            if action == 'submitted': 
                repo_name = payload['repository']['full_name']
                pr_number = payload['pull_request']['number'] 
                actor = payload['sender']['login'] 
                timestamp = payload['review']['submitted_at'] 
                state = payload['review']['state'] # 'approved', 'changes_requested', 'commented' 
                event_data.update({ 
                    'action': 'PR_review_submitted', 
                    'repo_name': repo_name, 
                    'actor': actor, 
                    'timestamp': timestamp, 
                    'pull_request_number': pr_number, 
                    'review_state': state, 
                }) 

        # For Merge events (handled by pull_request closed/merged action) 
 
        try: 
            GitHubEvent.objects.create(**event_data) 
            return JsonResponse({'status': 'success', 'message': 'Event processed'}) 
        except Exception as e: 
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500) 
    return JsonResponse({'status': 'error', 'message': 'Invalid GitHub event'}, status=400) 

def event_list(request): 
    # Retrieve the latest 15 events, or whatever number is required 
    # The image mentions "keep polling from MongoDB every 15 seconds" 
    # This implies a frontend polling mechanism or websockets for real-time updates. 
    # For simplicity, we'll just fetch the latest for the initial load. 
    latest_events = GitHubEvent.objects.order_by('-timestamp')[:15] 
 
    # For pagination if you have many events 
    paginator = Paginator(latest_events, 10) # Show 10 events per page 
    page_number = request.GET.get('page') 
    page_obj = paginator.get_page(page_number) 
 
    context = { 
        'page_obj': page_obj, 
    } 
    return render(request, 'github_events/index.html', context) 