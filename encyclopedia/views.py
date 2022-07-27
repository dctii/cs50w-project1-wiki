from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django import forms

# Import functions from encyclopedia/util.py
from .util import *

# Import Markdown converter from markdown2 package
from markdown2 import Markdown
# Import "choice" which randomly selects an element from a populated sequence
from secrets import choice

# Form for creating new encyclopedia entries and editing pre-existing entries
class EntryForm(forms.Form):
    # Division for the entry's title.
    title = forms.CharField(
        # The label is a header title for the textarea box
        label="Entry Title", 
        # The widget is for HTML inputs and can take in GET/POST data. With "Textarea", a text input box is taken in by the title.
        widget=forms.Textarea(attrs={
                # These are HTML attributes that help define the appearance of the input, including bootstrap, in-line CSS, and definition of rows which helps determine the height of the input box.
                'class': 'form-control col-md-6 col-lg-6',
                'style' : 'margin-bottom: 10px', 
                'rows': 1}))
    # Division for the entry's title.
    content = forms.CharField(
        label="Content", 
        widget=forms.Textarea(attrs={
                'class' : 'form-control col-md-6 col-lg-6', 
                'rows' : 12}))
    # Hidden division that tells "views.py/def entry_handler" to be in editing mode or not.
    edit = forms.BooleanField(
        # The "views.py/def edit" function will switch the "initial" from False to "True", and this changed condition of the form help "entry_handler" ignore checking for a pre-existing title like new entry creation does.
        initial=False, 
        # Whether in edit is set to True or False can be flipped by the user clicking a checkbox that appears with the form. This control is hidden from the user with HiddenInput() and the control is done via a url path after clickking the "Edit" button on the entry.html page and "views.py/def edit"
        widget=forms.HiddenInput(),
        # This condition is a default so that editing mode doesn't interfere with new page entries.
        required=False)

# Returns every listed entry in encyclopedia's /entries library on the home page.
def index(request):
    # Renders the target file destination, here index.html
    return render(request, "encyclopedia/index.html", {
        # A context variable where "entries" is the name used in Django HTML and list_entries() is the data that the name maps on to
        "entries": list_entries()
    })

# Renders an entry page with content in Markdown language
def entry(request, title):
    # Condition where an existing entry page, *.md, is retrieved from /entries
    if get_entry(title) is not None:
        return render(request, "encyclopedia/entry.html", {
            # The data that "entry" maps onto converts a specific entry's data in Markdown language into HTML
            "content":Markdown().convert(get_entry(title)),
            # Data for the entry's title
            "EntryTitle":title
        })
    else:
        return render(request, "encyclopedia/no_entry_here.html",{
            "EntryTitle":title
        })

# Handles creation of new entries and editing pre-existing entries
def entry_handler(request):
    # If the user is requesting the page, but not submitting data, then render the default Create New Entry page with a blank EntryForm.
    if request.method == "GET":
        return render(request, "encyclopedia/new_entry.html",{
            "form":EntryForm(),
            # Context variable used to tells Django HTML if the page exists is False
            "exists": False
        })
    # If the user submits information, e.g., creating new or editing entries, then do this.
    elif request.method == "POST":
        # Variable for the EntryForm from .forms
        form = EntryForm(request.POST)
        # Checks whether the data in EntryForm is valid or not
        if form.is_valid():
            # Cleaning of the data required for consistent output
            # Pulls information from the title division of EntryForm
            title = form.cleaned_data["title"]
            # Pulls information from the content division of EntryForm
            content = form.cleaned_data["content"]
            # If the entry is new and the title doesn't exist or if it is in editing mode, then it will allow saving the information the user has input or edited in EntryForm
            if(get_entry(title) is None or form.cleaned_data["edit"] is True):
                # Function from utils.py to save ent
                save_entry(title, content)
                return HttpResponseRedirect(reverse("entry", kwargs={'title': title}))
            # If the entry already exists, then it renders a page with Django HTML conditions that the page exists is true.
            else:
                return render(request, "encyclopedia/new_entry.html",{
                    "form":form,
                    # Context variable used to tell Django HTML if the page exists is True
                    "exists":True,
                    "EntryTitle":title
                })
        # If the form to be posted is not valid, then return to the Create New Entry page with an empty form.
        else:
            return render(request, "encyclopedia/new_entry.html",{
                "form":form,
                "exists":False
            })
    

# Used to edit information using "def entry_handler".
    # Passes the title to retrieve pre-existing entry information.
def edit(request, title):
    # If there is a pre-existing entry that matches the title, do this.
    if get_entry(title) is not None:
        form = EntryForm()
        # Call on the title of a pre-existing entry's EntryForm
        form.fields["title"].initial = title
        # Set an attribute making the title readonly so the title cannot be modified.
        form.fields["title"].widget.attrs['readonly'] = True
        # Call on the content from an entry using the get_entry function in utils.py, finding it by "title"
        form.fields["content"].initial = get_entry(title)
        # Switch the boolean value of "edit" to True from its default "False" so edited content can be saved.
        form.fields["edit"].initial = True
        return render(request, "encyclopedia/edit.html",{
            "form": form,
            "edit": form.fields["edit"].initial,
            # The title of a pre-existing entry is given to call on pre-existing content to that can be edited.
            "EntryTitle": form.fields["title"].initial
        })
    # If an entry can't be retrieved with get_entry, do this
    else:
        # Return a page that tells the user there is no entry with the title path for wiki/<title>/edit they've tried
        return render(request, "encyclopedia/no_entry_here.html", {
            "EntryTitle":title
        })

# Jumps to a random page
def random(RandomEntry):
    # Takes in an argument which randomly selects, with secret.choices, from "def list_entries" from utils.py
    RandomEntry = choice(list_entries())
    # Returns a redirect to the "entry" path from urls.py, passing RandomEntry, which is read by the variable it is mapped to, 'title'.
    return HttpResponseRedirect(reverse("entry", kwargs={'title':RandomEntry}
        ))

# A function to query entries, jumping to entries that are exact matches and producing a list of queries that the input for any entry's substrings.
def search(request):
    # The output of the text input of the user is put out in the URL bar as "/search?q=(input)"
    input = request.GET.get('q', '')
    # If the user does not input anything and executes a query, it returns a response telling the user they have no input for their query.
    if input is '':
        return render(request, "encyclopedia/empty_search.html")
    # If the user does input something, then do this.
    else:
        # If the user's string input can retrieve an entry, then return the page with the title exactly matching the input.
        if(get_entry(input) is not None):
            return HttpResponseRedirect(reverse("entry", kwargs={'title':input }
            ))
        # If the input is not an exact match to an entry title, then do this: return a list with any titles that have matching substrings.
        else:
            # Create a Python list to collect substring finds
            SubstringResults = []
            # Comb through all entry titles in the /entries folder
            for entry in list_entries():
                # Regardless of case, if the user string input matches any substrings of an entry title, then add the entry title to the Python list SubstringResults[]
                if input.upper() in entry.upper():
                    SubstringResults.append(entry)
            # If there are no matching substrings, then there will be 0 items in SubstringResults[], and a page is returned that states there are no matching queries given the user's input.
            if len(SubstringResults) == 0:
                return render(request, "encyclopedia/no_search_results.html")
            # Return the results with matching substrings as a list on search.html
            return render(request, "encyclopedia/search.html", {
                "SubstringResults":SubstringResults,
                "input":input
            })