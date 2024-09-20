from django.shortcuts import render,redirect,get_object_or_404
from .models import Category
from .forms import Categoryforms
from django.contrib import messages
from django.views.generic import ListView


def category_list(request):
    categories = Category.objects.all().order_by('id')
    return render(request, 'adminpart/category_list.html',{'categories':categories})

def create_category(request):
    if request.method == 'POST':
        form = Categoryforms(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Category added successfully.")
            return redirect ('category:category_list')
        else:
            messages.error(request, 'Retry. Please correct the errors.')
    else:
        form = Categoryforms()
    return render(request, 'adminpart/create_category.html',{'form':form})

def edit_category(request,category_id):
    category = get_object_or_404(Category,id =category_id)
    if request.method == 'POST':
        form = Categoryforms(request.POST,request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request,'Category updated successfully.')
            return redirect('category:category_list')
        else:
            messages.error(request, 'Retry. Please correct the errors.')
    else:
        form = Categoryforms(instance=category)
    return render (request,'adminpart/category_update.html',{'form':form})

def delete_category(request,category_id):
    if request.method == 'POST':
        category = get_object_or_404(Category,id =category_id)
        category.is_listed = not category.is_listed
        category.save()
        return redirect('category:category_list')

def toggle_category_listing(request,category_id):
    category = get_object_or_404(Category, id = category_id)
    category.is_listed = not category.is_listed
    category.save()
    return redirect('category:category_list')



#user side


class UserCategoryListView(ListView):
    model = Category
    template_name = 'userpart/user_panel/user_category_list.html'
    context_object_name = 'categories'
    paginate_by = 12  

    def get_queryset(self):
        return Category.objects.filter(is_listed=True).order_by('category_name')