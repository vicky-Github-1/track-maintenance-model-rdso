from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .models import PredictionResult
from .forms import CustomRegisterForm
from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import CustomUser 

import os
import pickle
from django.conf import settings
from .models import Task

#pridicton histry
from django.db.models import Count
from datetime import datetime, timedelta
from .forms import TaskForm
# Load model
model_path = os.path.join(settings.BASE_DIR, 'ml_model', 'final_model.pkl')
with open(model_path, 'rb') as f:
    model = pickle.load(f)

def predict_view(request):
    form = TaskForm()
    if not request.user.is_authenticated:
        return redirect('login')

    risk_percent = None
    f1 = f2 = f3 = f4 = f5= None  

    if request.method == "POST":
        try:
            f1 = float(request.POST.get("Speed"))
            f2 = float(request.POST.get("Vibration"))
            f3 = float(request.POST.get("Temperature"))
            f4 = float(request.POST.get("Axle_Load"))
            f5 = str(request.POST.get("Track_Id"))

            input_data = [[f1, f2, f3, f4]]
            proba = model.predict_proba(input_data)[0][1]
            risk_percent = round(proba * 100, 2)

            PredictionResult.objects.create(
            user=request.user,
            track_id=f5,
            speed=f1,
            vibration=f2,
            temperature=f3,
            axle_load=f4,
            prediction_percent=risk_percent
        )
        except Exception as e:
            risk_percent = f"Error: {e}"
    
    
    engineers = User.objects.filter(is_staff=False, is_deleted=False)  
    return render(request, 'predict.html', {
        'form': form,
        "prediction": risk_percent,
        "Speed": f1,
        "Vibration": f2,
        "Temperature": f3,
        "Axle_Load": f4,
        "Track_Id":f5,
        "engineers": engineers,
    })


def home_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'home.html', {
        'username': request.user.username
    })

from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomRegisterForm

def register_view(request):
    if request.method == 'POST':
        form = CustomRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # delay saving to update `is_staff`
            role = form.cleaned_data.get('role')
            user.zone = form.cleaned_data.get('zone')
            user.city = form.cleaned_data.get('city')

            if role == 'admin':
                user.is_staff = True  # ✅ typically, admin = is_staff
            elif role == 'engineer':
                user.is_staff = False

            user.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomRegisterForm()

    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')




def logout_view(request):
    logout(request)
    return redirect('login')


def alert_engineer(request):
    if request.method == "POST":
        engineer_id = request.POST.get("engineer_id")
        try:
            engineer = User.objects.get(id=engineer_id)
            send_mail(
                subject="🚨 High Maintenance Risk Alert",
                message="A track is at high maintenance risk. Please take action.",
                from_email="shubhamgupta23844@gmail.com",
                recipient_list=[engineer.email],
                fail_silently=False,
            )
            messages.success(request, f"Alert sent to {engineer.username} ({engineer.email})")
        except:
            messages.error(request, "Engineer not found.")

    return redirect("predict")

#pridiction history
def dashboard_view(request):
    # views.py (in dashboard_view)
    predictions = PredictionResult.objects.filter(user=request.user).order_by('-created_at')

    # predictions = PredictionResult.objects.all().order_by('-created_at')

    # Pie chart data (Maintenance Required vs Not Required)
    required = predictions.filter(prediction_percent__gte=75).count()
    not_required = predictions.filter(prediction_percent__lt=75).count()

    # Bar chart data (Predictions over past 7 days)
    today = datetime.today()
    labels = []
    counts = []

    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        count = predictions.filter(created_at__date=day.date()).count()
        labels.append(day.strftime('%b %d'))  # e.g., Jun 24
        counts.append(count)

    return render(request, 'dashboard.html', {
        'predictions': predictions,
        'required': required,
        'not_required': not_required,
        'labels': labels,
        'counts': counts,
    })


    #admin permission

def is_admin(User):
    return User.is_authenticated and User.role == 'admin'

@login_required
@user_passes_test(is_admin)
def user_list(request):
    users = CustomUser.objects.filter(is_deleted=False).exclude(pk=request.user.pk)
    create_form = CustomRegisterForm()
    return render(request, 'user_management/user_list.html', {
        'users': users,
        'create_form': create_form
    })


@login_required
@user_passes_test(is_admin)
def create_user(request):
    if request.method == 'POST':
        form = CustomRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.entry_by = request.user
            user.zone = form.cleaned_data.get('zone')
            user.city = form.cleaned_data.get('city')
            # ✅ Mark admin as staff
            if user.role == 'admin':
                user.is_staff = True
            else:
                user.is_staff = False  # optional for clarity

            user.save()
            return redirect('user_list')
        else:
            print("Create Form Errors:", form.errors)

    return redirect('user_list')


from .forms import UserEditForm

@login_required
@user_passes_test(is_admin)
def edit_user(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)

    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save(commit=False)

            # ✅ Use cleaned_data to get updated role
            role = form.cleaned_data.get('role')
            if role == 'admin':
                user.is_staff = True
            else:
                user.is_staff = False

            # ✅ Update password if provided
            password1 = form.cleaned_data.get('password1')
            if password1:
                user.set_password(password1)

            user.modified_by = request.user
            user.save()
            return redirect('user_list')

        else:
            print("Form errors:", form.errors)

    return redirect('user_list')


@login_required
@user_passes_test(is_admin)
def delete_user(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)
    user.is_deleted = True
    user.delete_by = request.user
    user.save()
    return redirect('user_list')

    #admin assign task to enginner
@login_required
@user_passes_test(is_admin)
def assign_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.assigned_by = request.user
            task.save()
            messages.success(request, "✅ Task assigned successfully!")
            return redirect('predict') 
    else:
        form = TaskForm()

    return render(request, 'predict.html', {'form': form})

@login_required
def engineer_tasks(request):
    tasks = Task.objects.filter(assigned_to=request.user)
    
    return render(request, 'engineer_tasks.html', {'tasks': tasks})

#uplaod csv

import pandas as pd
from django.http import HttpResponse
from io import StringIO

import os
import pandas as pd
import pickle
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse

import os
import pandas as pd
import pickle
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse



def upload_and_predict(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']

        if not csv_file.name.endswith('.csv'):
            return HttpResponse("Invalid file format. Please upload a CSV file.")

        try:
            # Read CSV
            df_original = pd.read_csv(csv_file)

            # Locate 'track_id' regardless of case
            track_id_col = next((col for col in df_original.columns if col.lower() == 'track_id'), None)
            if not track_id_col:
                return HttpResponse("Error: 'track_id' column not found in uploaded file.")

            # Rename it to 'Track_ID' (capitalized)
            df_original.rename(columns={track_id_col: 'Track_ID'}, inplace=True)

            # Prepare model input (drop Track_ID)
            df_model_input = df_original.drop(columns=['Track_ID'])

            # Load ML model
            model_path = os.path.join(settings.BASE_DIR, 'ml_model', 'final_model.pkl')
            with open(model_path, 'rb') as f:
                model = pickle.load(f)

            # Predict probabilities
            probas = model.predict_proba(df_model_input)[:, 1]
            predictions = [f"{round(p * 100, 2)}%" for p in probas]

            # Append to DataFrame
            df_original['Prediction'] = predictions

            # Save to database (batch insert)
            batch_results = []
            for i, row in df_original.iterrows():
                try:
                    speed = row['Speed'] if pd.notnull(row['Speed']) else 0.0
                    vibration = row['Vibration'] if pd.notnull(row            ['Vibration']) else 0.0
                    temperature = row['Temperature'] if pd.notnull(row            ['Temperature']) else 0.0
                    axle_load = row['Axle_Load'] if pd.notnull(row            ['Axle_Load']) else 0.0
            
                    batch_results.append(PredictionResult(
                        user=request.user,
                        track_id=row['Track_ID'],
                        speed=speed,
                        vibration=vibration,
                        temperature=temperature,
                        axle_load=axle_load,
                        prediction_percent=float(row['Prediction'].replace('%', ''))
                    ))
                except Exception as e:
                    print(f"Row {i} skipped due to error: {e}")


            if batch_results:
                PredictionResult.objects.bulk_create(batch_results)

            # Render as HTML table
            html_table = df_original.to_html(classes='table table-bordered text-start', index=False, table_id="predictionTable")
            return render(request, 'upload_csv/upload.html', {'table': html_table})

        except Exception as e:
            return HttpResponse(f"Error: {str(e)}")

    return render(request, 'upload_csv/upload.html')

@login_required
def clear_user_predictions(request):
    PredictionResult.objects.filter(user=request.user).delete()
    messages.success(request, "Your prediction results have been cleared.")
    return redirect('dashboard')  # 🔁 Replace with your actual dashboard view name
