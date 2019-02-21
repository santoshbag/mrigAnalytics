# -*- coding: utf-8 -*-
"""
Created on Wed Jan 16 13:21:59 2019

@author: Santosh Bag
"""
import datetime

def dict_to_html(dic=None):
    if dic == None:
        return ""
#    table = "<table> <tr><td><b> Heads </b></td><td><b> Value </b></td> </tr> "
#    
#    for head in dic.keys():
#        table = table + "<tr><td>"
#        table = table + str(head)
#        table = table + "</td><td>"
#        table = table + str(dic[head])
#        table = table + "</td>"
#        table = table + "</tr>"
#    table = table + "</table>"

    keys = list(dic.keys())
    vals = [dic[key] for key in keys]
    
    table = list_to_html([keys,vals])
    return table

def list_to_html(arglist=None,size="normal"):
    if arglist == None:
        return ""

    header_html = "<th class=\"head-item mbr-fonts-style display-7\"  style=\"padding: 5px;\" bgcolor=\"#f9f295\"><font color=\"#0f7699\" size=\"1\" onclick=\"sortTable(%s)\">%s</th>"
    body_html = "<td class=\"body-item mbr-fonts-style display-7\" style=\"padding: 5px;\" nowrap=\"nowrap\"><font size=\"1\">%s</td>"

    if size == "small":
        header_html = "<th class=\"head-item mbr-fonts-style\" style=\"padding: 5px;\" bgcolor=\"#f9f295\"><font color=\"#0f7699\" size=\"1\"  onclick=\"sortTable(%s)\">%s</font></th>"
        body_html = "<td class=\"body-item mbr-fonts-style\" style=\"padding: 5px;\" nowrap=\"nowrap\"><font size=\"1\">%s</font></td>"
        

#    table = "<thead> <tr class=\"table-heads \">"
    table = "<tr class=\"table-heads \">"
    
    # Header
    i = 0
    for head in arglist[0]:
#        table = table + "<th class=\"head-item mbr-fonts-style display-7\">" + head + "</th>"
        if isinstance(head,float):
            table = table + header_html %(i,"{0:9.2f}".format(head))
        elif isinstance(head,datetime.date):
            table = table + header_html %(i,head.strftime('%d-%b-%Y'))
        else:
            table = table + header_html %(i,head)
        i = i + 1
        
    table = table + "</tr></thead><tbody>"
    
    for row in arglist[1:]:
        table = table + "<tr>"
        for cell in row:
            if isinstance(cell,float):
                table = table + body_html %("{0:9.2f}".format(cell))
            elif isinstance(cell,datetime.date):
                table = table + body_html %(cell.strftime('%d-%b-%Y'))
            else:
                table = table + body_html %(cell)

        table = table + "</tr>"
    table = table + "</tbody>"    
    return table