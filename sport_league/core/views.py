# Django Imports


from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.urls import reverse
from django.views import View
from django.views.decorators.csrf import csrf_exempt

# App Imports
from utils.csv_utils import process_csv_file
from core.handlers import GamesHandler
from core.forms import CustomUserCreationForm, EventOperation

# 3rd Party Imports
from http import HTTPStatus
from json import loads



@csrf_exempt
def handler(request, *args, **kwargs):
    if request.method == "POST":
        request_body = loads(request.body)
        request_body = EventOperation(request_body)
        if request_body.is_valid():
            data = request_body.cleaned_data
            operation = data.get('operation', None)
            method_handler = getattr(GamesHandler, operation, None)
            if not method_handler:
                return JsonResponse(
                    data={"operation": [f"{operation} operation is not supported!"]},
                    status=HTTPStatus.UNPROCESSABLE_ENTITY,
                )
            return method_handler(request)
        else:
            return JsonResponse(
                data=request_body.errors,
                status=HTTPStatus.UNPROCESSABLE_ENTITY,
            )


def upload_csv(request):
    if request.method == 'POST':
        csv_file = request.FILES.get('csv_file', None)
        error = {"error": "No file provided."}
        success = "CSV file uploaded successfully."
        # Check if file is provided
        if not csv_file:
            return render(request, 'core/upload_csv.html', context=error)

        # Check if file is CSV
        if not csv_file.name.endswith('.csv'):
            error = {"error": "File is not a CSV file."}
            return render(request, 'core/upload_csv.html', context=error)
        try:
            process_csv_file(csv_file)
            return redirect(reverse('core:home') + f"?success={success}")
        except Exception as e:
            error = {"error": f'Error processing CSV file: {e}'}
            return render(request, 'core/upload_csv.html', context=error)
    return render(request, 'core/upload_csv.html')


class HomeView(View):

    def get(self, request, *args, **kwargs):
        success = request.GET.get('success')
        if success:
            return render(request, 'core/main.html', {'success': success})
        return render(request, "core/main.html")
