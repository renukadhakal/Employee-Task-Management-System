from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from .models import LeaveRequest, Leave
from .forms import LeaveRequestForm
from notification.models import Notification
from account.models import User


@login_required(login_url="/login")
def leave_request_list(request):
    leave_requests = LeaveRequest.objects.filter(user=request.user).order_by(
        "-applied_at"
    )
    leave = Leave.objects.get(user=request.user)
    remaining_leave = leave.total
    return render(
        request,
        "leave/leave_request_list.html",
        {"leave_requests": leave_requests, "remaining_leave": remaining_leave},
    )


@login_required(login_url="/login")
def leave_request_create(request):
    if request.method == "POST":
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave_request = form.save(commit=False)
            leave_request.user = request.user
            leave_request.applied_at = now()
            leave_request.save()
            Notification.objects.create(
                title="Leave request",
                message=f"{request.user.username} has requested a leave.",
                user=request.user.report_to,
            )
            return redirect("leave:leave_request_list")

    else:
        form = LeaveRequestForm()
    return render(request, "leave/leave_request_form.html", {"form": form})


@login_required(login_url="/login")
def leave_request_delete(request, pk):
    leave_request = get_object_or_404(LeaveRequest, pk=pk, user=request.user)
    if request.method == "POST":
        leave_request.delete()
        return redirect("leave:leave_request_list")
    return render(
        request,
        "leave/leave_request_confirm_delete.html",
        {"leave_request": leave_request},
    )


@login_required
def leave_request_edit(request, pk):
    leave_request = get_object_or_404(LeaveRequest, pk=pk, user=request.user)

    if request.method == "POST":
        form = LeaveRequestForm(request.POST, instance=leave_request)
        if form.is_valid():
            form.save()
            return redirect("leave:leave_request_list")
    else:
        form = LeaveRequestForm(instance=leave_request)

    return render(
        request, "leave/leave_request_form.html", {"form": form, "edit_mode": True}
    )


@login_required
def manager_leave_requests(request):
    if request.user.role != User.Role_Type.MANAGER:
        return redirect("leave:leave_request_list")

    leave_requests = LeaveRequest.objects.filter(user__report_to=request.user).order_by(
        "status", "start_at"
    )

    return render(
        request, "leave/manager_leave_requests.html", {"leave_requests": leave_requests}
    )


@login_required
def approve_leave_request(request, pk):
    leave_request = get_object_or_404(LeaveRequest, pk=pk, user__report_to=request.user)

    leave_request.status = LeaveRequest.Leave_Types.APPROVED
    leave_request.approved_by = request.user
    leave_request.save()
    Notification.objects.create(
        title="Leave request",
        message="Your Leave have been approved",
        user=leave_request.user,
    )
    leave = Leave.objects.get(user=leave_request.user)
    leave.total = leave.total - 1
    leave.save()
    return redirect("leave:manager_leave_requests")


@login_required
def reject_leave_request(request, pk):
    leave_request = get_object_or_404(LeaveRequest, pk=pk, user__report_to=request.user)

    leave_request.status = LeaveRequest.Leave_Types.REJECTED
    leave_request.approved_by = request.user
    leave_request.save()

    Notification.objects.create(
        title="Leave request",
        message="Your Leave have been rejected",
        user=leave_request.user,
    )
    return redirect("leave:manager_leave_requests")
