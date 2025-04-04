from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from .models import FlowMonitor
from .forms import FlowMonitorBasicForm, FlowStepForm


@login_required
def flow_monitor_list(request):
    """View to list all flow monitors for the current user"""
    flow_monitors = FlowMonitor.objects.filter(owner=request.user).order_by('name')
    
    # Get basic status for each flow
    flow_data = []
    for flow in flow_monitors:
        last_check = flow.checks.order_by('-created_at').first()
        status = "Unknown"
        last_checked = None
        
        if last_check:
            status = "Successful" if last_check.is_successful else "Failed"
            last_checked = last_check.created_at
            
        flow_data.append({
            'id': flow.id,
            'name': flow.name,
            'status': status,
            'last_checked': last_checked,
            'starting_url': flow.starting_url,
            'step_count': flow.steps.count(),
        })
    
    return render(
        request,
        'flow_monitors/flow_monitor_list.html',
        {
            'flow_monitors': flow_data,
        }
    )

@login_required
def flow_monitor_create(request):
    """First step in creating a flow monitor - basic info"""
    if request.method == 'POST':
        form = FlowMonitorBasicForm(request.POST)
        if form.is_valid():
            flow = form.save(commit=False)
            flow.owner = request.user
            flow.save()
            
            # Store the new flow's ID in session for the next steps
            request.session['flow_creation_id'] = str(flow.id)
            
            messages.success(request, f'Flow "{flow.name}" created. Now add steps to your flow.')
            return redirect('flow_step_add')
    else:
        form = FlowMonitorBasicForm()
    
    return render(
        request,
        'flow_monitors/flow_monitor_form.html',
        {
            'form': form,
            'title': 'Create Flow Monitor',
            'step': 1,
            'total_steps': 2,  # Basic info + steps
        }
    )

@login_required
def flow_step_add(request):
    """Add steps to the flow monitor"""
    # Get the flow being created from session
    flow_id = request.session.get('flow_creation_id')
    if not flow_id:
        messages.error(request, 'Flow creation session expired. Please start again.')
        return redirect('flow_monitor_create')
    
    # Get the flow and verify ownership
    flow = get_object_or_404(FlowMonitor, pk=flow_id)
    if flow.owner != request.user:
        messages.error(request, "You don't have permission to edit this flow")
        return HttpResponseForbidden("You don't have permission to edit this flow")
    
    # Get the current steps and next step number
    current_steps = flow.steps.order_by('sequence')
    next_step_number = current_steps.count() + 1
    
    if request.method == 'POST':
        # Check if the user clicked "done"
        if 'done' in request.POST:
            # Clear the session variable
            if 'flow_creation_id' in request.session:
                del request.session['flow_creation_id']
                
            messages.success(request, f'Flow "{flow.name}" created successfully with {current_steps.count()} steps.')
            return redirect('flow_monitor_list')
        
        # Otherwise, process the new step
        form = FlowStepForm(request.POST, step_number=next_step_number)
        if form.is_valid():
            step = form.save(commit=False)
            step.flow = flow
            step.sequence = next_step_number
            step.save()
            
            messages.success(request, f'Step {next_step_number} added. Add another step or click Done.')
            return redirect('flow_step_add')
    else:
        # For GET requests, show a fresh form for the next step
        form = FlowStepForm(step_number=next_step_number)
        
        # Set initial action type based on step number
        if next_step_number == 1:
            # First step is usually to navigate to the starting URL
            form.initial['action_type'] = 'navigate'
            form.initial['url'] = flow.starting_url
            form.initial['description'] = f'Navigate to {flow.starting_url}'
    
    return render(
        request,
        'flow_monitors/flow_step_form.html',
        {
            'form': form,
            'flow': flow,
            'current_steps': current_steps,
            'next_step_number': next_step_number,
            'title': f'Add Steps to {flow.name}',
        }
    )

@login_required
def flow_monitor_detail(request, pk):
    """View to see details of a flow monitor and its checks"""
    # Get the flow and verify ownership
    flow = get_object_or_404(FlowMonitor, pk=pk)
    if flow.owner != request.user:
        messages.error(request, "You don't have permission to view this flow")
        return HttpResponseForbidden("You don't have permission to view this flow")
    
    # Get the steps
    steps = flow.steps.order_by('sequence')
    
    # Get recent checks
    checks = flow.checks.order_by('-created_at')[:10]
    
    # Calculate success rate
    total_checks = flow.checks.count()
    successful_checks = flow.checks.filter(is_successful=True).count()
    success_rate = (successful_checks / total_checks * 100) if total_checks > 0 else 0
    
    return render(
        request,
        'flow_monitors/flow_monitor_detail.html',
        {
            'flow': flow,
            'steps': steps,
            'checks': checks,
            'total_checks': total_checks,
            'success_rate': success_rate,
        }
    )

@login_required
def flow_monitor_check_now(request, pk):
    """Manually trigger a flow check"""
    # Get the flow and verify ownership
    flow = get_object_or_404(FlowMonitor, pk=pk)
    if flow.owner != request.user:
        messages.error(request, "You don't have permission to check this flow")
        return HttpResponseForbidden("You don't have permission to check this flow")
    
    try:
        # Schedule the flow check to run immediately
        from monitors.tasks import perform_flow_check
        import django_rq
        
        queue = django_rq.get_queue('high')
        job = queue.enqueue(perform_flow_check, str(flow.id))
        
        messages.info(request, f"Check initiated for {flow.name}. Results will be available shortly.")
    except Exception as e:
        messages.error(request, f"Error scheduling check: {str(e)}")
    
    return redirect('flow_monitor_detail', pk=flow.id)

@login_required
def flow_monitor_delete(request, pk):
    """Delete a flow monitor"""
    # Get the flow and verify ownership
    flow = get_object_or_404(FlowMonitor, pk=pk)
    if flow.owner != request.user:
        messages.error(request, "You don't have permission to delete this flow")
        return HttpResponseForbidden("You don't have permission to delete this flow")
    
    if request.method == 'POST':
        name = flow.name
        flow.delete()
        messages.success(request, f'Flow "{name}" deleted successfully')
        return redirect('flow_monitor_list')
    
    return render(
        request, 
        'flow_monitors/flow_monitor_confirm_delete.html', 
        {'flow': flow}
    )