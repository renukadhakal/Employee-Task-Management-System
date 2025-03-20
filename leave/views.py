from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from .models import LeaveRequest, LeaveType
from .forms import LeaveRequestForm
from notification.models import Notification
from account.models import User
from django.contrib import messages


@login_required(login_url="/login")
def leave_request_list(request):
    if request.user.role == User.Role_Type.MANAGER:
        leave_requests = LeaveRequest.objects.filter(
            user__report_to=request.user
        ).order_by("-applied_at")
    elif request.user.role == User.Role_Type.EMPLOYEE:
        leave_requests = LeaveRequest.objects.filter(user=request.user).order_by(
            "-applied_at"
        )
    elif request.user.role == User.Role_Type.ADMIN:
        leave_requests = LeaveRequest.objects.all().order_by("-applied_at")

    # print(leave_requests_with_types, 'leave requests with types')
    print(leave_requests, "leave requests")
    # print(leave_types_dict, 'leave types dict')
    # print(leave_types, 'leave types')
    return render(
        request,
        "leave/leave_request_list.html",
        {
            "leave_requests": leave_requests,
            "leave_types": LeaveType.objects.all(),
            "remaining_leave": LeaveRequest.remaining_leave(request.user),
        },
    )
    # leave_requests = LeaveRequest.objects.filter(user=request.user).order_by(
    #     "-applied_at"
    # )
    # # leave = Leave.objects.get(user=request.user)
    # # remaining_leave = leave.total
    # return render(
    #     request,
    #     "leave/leave_request_list.html",
    #     {"leave_requests": leave_requests, "remaining_leave": LeaveRequest.remaining_leave(request.user)},
    # )


@login_required(login_url="/login")
def leave_request_create(request):
    if request.method == "POST":
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave_request = form.save(commit=False)
            leave_request.user = request.user
            leave_request.applied_at = now()

            requested_days = (leave_request.end_at - leave_request.start_at).days + 1
            print(requested_days, "requested days")
            available_days = LeaveRequest.remaining_for_type(
                leave_request.leave_type, request.user
            )
            print(available_days, "available days")
            if requested_days > available_days:
                messages.error(
                    request,
                    f"You cannot request more leave days than available. You have {available_days} days available.",
                )
                return redirect("leave:leave_request_list")

            # leave = Leave.objects.get(user=request.user)

            # if requested_days > leave.total:
            #     messages.error(
            #         request, "You cannot request more leave days than available."
            #     )
            # else:
            leave_request.save()
            if request.user.report_to:
                Notification.objects.create(
                    title="Leave request",
                    message=f"{request.user.username} has requested {requested_days} days of leave.",
                    user=request.user.report_to,
                )

            messages.success(request, "Leave request submitted successfully.")
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

    if leave_request.status != LeaveRequest.Leave_Types.PENDING:
        messages.error(request, "This leave request has already been processed.")
        return redirect("leave:manager_leave_requests")

    requested_days = (leave_request.end_at - leave_request.start_at).days + 1

    leave = LeaveRequest.objects.get(user=leave_request.user)

    if requested_days > leave.total:
        messages.error(
            request, "Cannot approve leave request. Not enough leave balance."
        )
        return redirect("leave:manager_leave_requests")

    leave_request.status = LeaveRequest.Leave_Types.APPROVED
    leave_request.approved_by = request.user
    leave_request.save()

    leave.total -= requested_days
    leave.save()

    Notification.objects.create(
        title="Leave request",
        message="Your leave has been approved.",
        user=leave_request.user,
    )

    messages.success(request, "Leave request approved successfully.")
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
