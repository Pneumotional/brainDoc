from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Document
from .forms import DocumentForm, RegisterForm



@login_required
def upload_document(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.user = request.user
            document.save()
            messages.success(request, 'Document uploaded successfully.')
            return redirect('dashboard')
    else:
        form = DocumentForm()
    return render(request, 'upload.html', {'form': form})

@login_required
def delete_document(request, pk):
    document = get_object_or_404(Document, pk=pk, user=request.user)
    document.file.delete()
    document.delete()
    messages.success(request, 'Document deleted successfully.')
    return redirect('dashboard')