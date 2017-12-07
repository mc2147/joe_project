from __future__ import unicode_literals
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

def Display(request):
    context = {}
    Display_String = ""
    context["Display"] = []
    context["Five_Day_Log"] = []
    # Daily Log
    r = open("Daily_Logs.txt", "r")
    l = r.readlines()
    for line in l:
        context["Display"].append(line)
    # Five-Day Log
    x = open("5_Day_Log.txt", "r")
    z = x.readlines()
    for line in z:
        context["Five_Day_Log"].append(line)
    # return HttpResponse("Test")
    return render(request, "Display.html", context)