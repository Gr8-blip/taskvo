# from django import forms
# from .models import Task

# class TaskForm(forms.ModelForm):
#     class Meta:
#         model = Task
#         fields = ['title', 'description', 'category', 'due_date']
        
        
#         widgets = {
#             'title': forms.TextInput(attrs={"placeholder": "Task Title (e.g., Finish Project Report)", "class": "w-full p-3 rounded-lg bg-gray-900 text-gray-100 border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500 text-lg placeholder-gray-400"}),
#             'description': forms.Textarea(attrs={"placeholder": "Description (Optional): Add more details here...", "class": "w-full p-3 rounded-lg bg-gray-900 text-gray-100 border border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500 text-base placeholder-gray-400 resize-y min-h-[60px]"}),
#             'category': forms.Select()
#         }