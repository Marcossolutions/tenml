from django.shortcuts import render,redirect,get_object_or_404
from .models import Category
from .forms import Categoryforms
from django.contrib import messages
from django.views.generic import ListView
from django.core.paginator import Paginator


def category_list(request):
    categories = Category.objects.all().order_by('id')
    per_page = 10
    paginator = Paginator(categories,per_page)
    page_number = request.GET.get('page',1)
    page_obj = paginator.get_page(page_number)
    return render(request, 'adminpart/category_list.html',{'page_obj':page_obj})

def create_category(request):
    if request.method == 'POST':
        form = Categoryforms(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Category added successfully.")
            return redirect ('category:category_list')
        else:
            for field in form:
                for error in field.errors:
                    messages.error(request,error)
            # messages.error(request, 'Retry. Please correct the errors in the forms.')
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
            for field in form:
                for error in field.errors:
                    messages.error(request,error)
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