from sys import exit
import time
try:
    import requests
except:
    print("Python Request module not available on this machine")
    print("Fatal Error: The program will now quit!")
    print("Run <pip install requests> to install this module ")
    exit()
import re
from platform import platform

psdemail=''
psdpass=''

branchfilter='' #branch that must be included in consolidated projects
#only single branch input supported
#leave empty to skip branch filtering

studentid=0

projectlist='2023-2024 / SEM-I' #project list for which data will be fetched. Entire history is sent by the server thus has to be filtered

searchword=[] #Domains identified by two letter wild card here inside the list. 
#El=Electronics 
#Co=Computer Science
#IT
#Fi=Finance and Management
#Ch=Chemical
#Me=Mechanical

stripendlimit=0 #Lower limit for stripend (First Degree)

scholarship=0 #Lower limit for Scholarship Amount

stripendlimitpg=0 #Lower limit for stripend (Higher Degree)

ignore_details=True #Ignores project briefing and provides a tabular output

searchword.append('-')

if (platform()[0:7]=="Windows"):
    import ctypes
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

class bcolors:
    HEADER = '\033[95m'
    OKGREEN = '\033[92m'
    OKBLUE = '\033[94m'
    OKPURPLE = '\033[95m'
    INFOYELLOW = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

if(ignore_details):
    fname="Station_list.html"
else:
    fname="Station_brief.html"

file_html = open(fname, "w")

if(ignore_details):
    file_html.write('''<!DOCTYPE html>
    <html style="background-color:#1e1e1e;">
    <style>
    table, th ,td{
        color: white;
        border:2px solid white;
    }
    </style>
    <head>
    <title>Station List</title>
    </head> 
    <body>''')
else:
    file_html.write('''<!DOCTYPE html>
    <html style="background-color:#131516;">
    <head>
    <title>Station List</title>
    </head> 
    <body>''')


def link(uri, label=None):
    if label is None: 
        label = uri
    parameters = ''

    escape_mask = '\033]8;{};{}\033\\{}\033]8;;\033\\'

    return escape_mask.format(parameters, uri, label)

def token_gen():
    curr_millis=int(time.time()*1000)
    epochTicks = 621355968000000000
    ticksPerMillisecond = 10000
    token= epochTicks + (curr_millis * ticksPerMillisecond)
    return int(token)


f=open('debug','w')

url='http://psd.bits-pilani.ac.in/Login.aspx'

resp_url=f'http://psd.bits-pilani.ac.in/Student/NEWStudentDashboard.aspx?StudentId={studentid}'

resp_url2='http://psd.bits-pilani.ac.in/Student/StudentStationPreference.aspx'

station_fetch='http://psd.bits-pilani.ac.in/Student/ViewActiveStationProblemBankData.aspx'

pb_details='http://psd.bits-pilani.ac.in/Student/StationproblemBankDetails.aspx'

ps=requests.Session()
resp_get=ps.get(url)
outhtml = resp_get.text.splitlines()
test=0
print(f"{bcolors.OKBLUE}>{bcolors.ENDC}Getting Validation token...")
formelement=[]
for line in outhtml:
    if (line.find('<form')>0):
        test=test+1
    if test>0:
        formelement.append(line)
    if (line.find('</form')>0):
        test=test-1

inputelement=[]
for line in formelement:
    if (line.find('VIEWSTATE')>0):
        inputelement.append(line)
    if (line.find('EVENTVALIDATION')>0):
        inputelement.append(line)
inval=[]
for i in range(len(inputelement)):
    inputelement[i]=inputelement[i].split(' ')
    for entry in inputelement[i]:
        if (len(entry)>5 and entry[0:5]=='value'):
            inputelement[i]=entry[7:-1]

payload = {
    '__EVENTTARGET':"",
    '__EVENTARGUMENT':"",
    '__VIEWSTATE':inputelement[0],
    '__VIEWSTATEGENERATOR':inputelement[1],
    '__EVENTVALIDATION':inputelement[2],
    'TxtEmail': psdemail,
    'txtPass': psdpass,
    'Button1':"Login",
    'txtEmailid':""
}

payload2 ={'CompanyId':"0"}

headers={
    'Host': 'psd.bits-pilani.ac.in',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Content-Type': 'application/json; charset=utf-8',
    'X-Requested-With': 'XMLHttpRequest',
    'Origin': 'http://psd.bits-pilani.ac.in',
    'Connection': 'keep-alive',
    'Referer': 'http://psd.bits-pilani.ac.in/Student/StudentStationPreference.aspx'
}
print(f"{bcolors.OKBLUE}>{bcolors.ENDC}Logging in...")
post_req=ps.post(url,data=payload)
outhtml=post_req.text.splitlines()

for line in outhtml:
    if (line.find('StudentId')>0):
        studentid=line.split(' ')

try:
    for entry in studentid:
        if (entry[-16:-7]=='StudentId'):
            studentid=entry[-6:-1]
    print(f"{bcolors.OKGREEN}SUCCESS{bcolors.ENDC}\n")
except:
    exit(f"{bcolors.FAIL}Check Email and Password{bcolors.ENDC}")

get_req=ps.get(resp_url)
print(f"{bcolors.OKBLUE}>{bcolors.ENDC}Getting Dashboard...")
get_req=ps.get(resp_url2)
print(f"{bcolors.OKBLUE}>{bcolors.ENDC}Getting Station List....")
post_req=ps.post(resp_url2+'/getinfoStation',headers=headers,json=payload2)

if(post_req.status_code==404):
    print(f"{bcolors.FAIL}ERROR access Station Preference list{bcolors.ENDC}")
    print(f"{bcolors.OKBLUE}>{bcolors.ENDC}Fallback to problem bank scraping....")
    print(f"{bcolors.OKBLUE}>{bcolors.ENDC}Getting Station List....")
    payload_bak={'batchid': "undefined",
                'token': str(token_gen())}

    headers.update({'Referer': station_fetch})
    post_req=ps.post(station_fetch+'/getPBdetail',headers=headers,json=payload_bak)

    jsonout=post_req.text[8:-4]
    jsonout=jsonout.split('},{')
    for i in range(len(jsonout)):
        jsonout[i]=re.sub('\\\\"','',jsonout[i])
        jsonout[i]=re.sub('\\\\\\\\u0026','&',jsonout[i])
        jsonout[i]=jsonout[i].split(',')
        temp=[]
        for subentry in jsonout[i]:
            temprep=subentry.split(':',1)
            if len(temprep)>1:
                temp.append(temprep[1].rstrip())
            else:
                temp[-1]=temp[-1]+','+subentry.rstrip()
        jsonout[i]=temp
    for i in range(len(jsonout)):
        temp=jsonout[i][0]
        jsonout[i][0]=jsonout[i][-2]
        jsonout[i][-2]=temp
        temp=jsonout[i][6]
        jsonout[i][6]=jsonout[i][-1]
        jsonout[i][-1]=temp
        temp=jsonout[i][2]
        jsonout[i][2]=jsonout[i][-6]+'-'+jsonout[i][-3]+', '+jsonout[i][-4]
        jsonout[i][-3]=temp
else:
    jsonout=post_req.text[8:-4]
    jsonout=jsonout.split('},{')
    for i in range(len(jsonout)):
        jsonout[i]=re.sub('\\\\"','',jsonout[i])
        jsonout[i]=re.sub('\\\\\\\\u0026','&',jsonout[i])
        jsonout[i]=jsonout[i].split(',')
        temp=[]
        for subentry in jsonout[i]:
            temprep=subentry.split(':',1)
            if len(temprep)>1:
                temp.append(temprep[1].rstrip())
            else:
                temp[-1]=temp[-1]+','+subentry.rstrip()
        jsonout[i]=temp

print(f"{bcolors.OKGREEN}RECIEVED{bcolors.ENDC}\n")

print(f"{bcolors.OKBLUE}>{bcolors.ENDC}Preference Filtering Started")
pop_arr=[]
for j in range(len(jsonout)):
    if(len(searchword)>1 and jsonout[j][2][0:2] not in searchword):
        pop_arr.append(j)

pop_arr.reverse()
for entry in pop_arr:
    jsonout.pop(entry)
print(f"{bcolors.OKGREEN}Domain Filtered\n{bcolors.ENDC}")
for j in range(len(jsonout)):
    try:
        [Sdomain,StationName]=jsonout[j][2].split('-',1)
    except:
        [Sdomain,StationName]=['-',jsonout[j][2]]
    print(f'{bcolors.INFOYELLOW}>{bcolors.ENDC}{Sdomain.rstrip()}-{StationName}')

print(f"\n{bcolors.OKBLUE}>{bcolors.ENDC}Fetching Project list...\n")
headers.update({'Referer': station_fetch})
fetchlist=[]
k=0
for entry in jsonout:
    k=k+1
    print(f"\033[A{bcolors.OKBLUE}>{bcolors.ENDC}Fetching data {bcolors.OKBLUE}{round(k/len(jsonout)*100,2)}%{bcolors.ENDC} Done  ")
    payload3={
        'StationId':f'{entry[-2]}'
    }
    post_req=ps.post(station_fetch+'/getPBPOPUP',headers=headers,json=payload3)
    fetchlist.append(re.sub('\\\\"','',post_req.text[8:-4]))
    fetchlist[-1]=fetchlist[-1].split('},{')
    for i in range(len(fetchlist[-1])):
        fetchlist[-1][i]=fetchlist[-1][i].split(',')
        temp=[]
        for subentry in fetchlist[-1][i][2:]:
            temprep=subentry.split(':',1)
            if len(temprep)>1:
                temp.append(temprep[1].rstrip())
            else:
                temp[-1]=temp[-1]+','+subentry.rstrip()
        fetchlist[-1][i]=temp

print(f"{bcolors.OKGREEN}RECIEVED{bcolors.ENDC}\n")
print(f"{bcolors.OKBLUE}>{bcolors.ENDC}Filtering for incomplete data and Stripend Constraints")
print(f"{bcolors.FAIL}ALSO REMOVING PAST SEMESTER DATA{bcolors.ENDC}")
pop_arroext=[]
for i in range(len(fetchlist)):
    pop_arrint=[]
    for j in range(len(fetchlist[i])):
        fetchlist[i][j].append(j)
        valid=False
        if(len(branchfilter)>1):
            if(len(fetchlist[i][j])>1):
                count=len([*re.finditer('any',fetchlist[i][j][-5],re.IGNORECASE)])-len([*re.finditer('anya',fetchlist[i][j][-5],re.IGNORECASE)])-len([*re.finditer('anyb',fetchlist[i][j][-5],re.IGNORECASE)])-len([*re.finditer('anyc',fetchlist[i][j][-5],re.IGNORECASE)])
                if(re.search(branchfilter,fetchlist[i][j][-5],re.IGNORECASE)):
                    valid=True
                elif(count>0 or len(fetchlist[i][j][-5].strip())<2):
                    valid=True
                elif(re.search(f'any{branchfilter}',fetchlist[i][j][-5],re.IGNORECASE)):
                    valid=True
        else:
            valid=True
        if(len(fetchlist[i][j])<2 or int(fetchlist[i][j][-2])<stripendlimitpg or int(fetchlist[i][j][-3])<scholarship or int(fetchlist[i][j][-4])<stripendlimit or (fetchlist[i][j][1]!=projectlist and j) or not valid):
            if(len(fetchlist[i][j])<2):
                print(f"{bcolors.INFOYELLOW}>{bcolors.ENDC}No Fetch File? Check Debug Output")
                f.write(str(jsonout[i]))
                f.write('-------------')
                f.write(str(fetchlist[i]))
                f.write('\n')
            pop_arrint.append(j)
            try:
                print(f"{bcolors.INFOYELLOW}>{bcolors.ENDC}Project List {bcolors.OKBLUE}{fetchlist[i][j][1]}{bcolors.ENDC} removed-{jsonout[i][2]}")
            except:
                print(f"{bcolors.INFOYELLOW}>{bcolors.ENDC}Removed Broken list data")
    pop_arrint.reverse()
    for entry in pop_arrint:
        fetchlist[i].pop(entry)
    if(len(fetchlist[i])==0):
        pop_arroext.append(i)
        print(f"{bcolors.INFOYELLOW}>{bcolors.ENDC}Station removed-{bcolors.FAIL}{jsonout[i][2]}{bcolors.ENDC}")

pop_arroext.reverse()
for entry in pop_arroext:
    fetchlist.pop(entry)
    jsonout.pop(entry)
print(f"{bcolors.OKGREEN}DONE{bcolors.ENDC}\n")
print(f"{bcolors.OKBLUE}>{bcolors.ENDC}Starting sort by Stripend")
fetchswitch=[]

for i in range(len(fetchlist)):
    fetchswitch.append(int(fetchlist[i][0][-4]))

indices = sorted(
    range(len(fetchswitch)),
    key=lambda index: fetchswitch[index], reverse=True)

fetchlist = [fetchlist[index] for index in indices]

jsonout = [jsonout[index] for index in indices]
print(f"{bcolors.OKGREEN}DONE{bcolors.ENDC}\n")

print(f"{bcolors.OKBLUE}>{bcolors.ENDC}Generating Project Sublist URLS")
for i in range(len(jsonout)):
    try:
        [Sdomain,StationName]=jsonout[i][2].split('-',1)
    except:
        [Sdomain,StationName]=['-',jsonout[i][2]]
    for j in range(len(fetchlist[i])):
        urlmask=f'http://psd.bits-pilani.ac.in/Student/StationproblemBankDetails.aspx?CompanyId={jsonout[i][-1]}&StationId={jsonout[i][-2]}&BatchIdFor={fetchlist[i][j][2]}&PSTypeFor={fetchlist[i][j][3]}'
        fetchlist[i][j].append(urlmask)

payload4={"batchid": "undefined"}

if(ignore_details):
    file_html.write('''<table>
    <tr>
    <th>Station</th>
    <th>Domain</th>
    <th>Latest Problem Bank</th>
    <th>Last updated on</th>
    <th>Eligibility</th>
    <th>Total Req. Interns</th>
    <th>Stripend</th>
    <th>Link</th>
    </tr>''')
print(f"{bcolors.OKBLUE}>{bcolors.ENDC}Fetching Project Sublists and Generating Output HTML")
print(f"\n{bcolors.OKGREEN}Recommended Projects{bcolors.ENDC}")
for i in range(len(jsonout)):
    try:
        [Sdomain,StationName]=jsonout[i][2].split('-',1)
    except:
        [Sdomain,StationName]=['-',jsonout[j][2]]
    print(f'\n{bcolors.INFOYELLOW}Station{bcolors.ENDC}-{StationName}[{Sdomain.rstrip()}]')
    if(not ignore_details):
        file_html.write(f'''<div><h1 style="color:#e8e6e3;"><span style="color: fuchsia">{StationName}</span>[{Sdomain.rstrip()}]</h1>
        <ul>''')
    else:
        file_html.write(f'''<tr>
        <td><span style="color:#ff72ff;">{StationName}</span></td><td>{Sdomain.rstrip()}</td>''')
    for j in range(len(fetchlist[i])):
        uri=fetchlist[i][j][-1]
        headers.update({'Referer': uri})
        post_req=ps.get(uri)
        print("Loading Project Sub-list...")
        post_req=ps.post(pb_details+'/ViewPB',headers=headers,json=payload4)
        pbout=post_req.text[8:-3]
        pbout=pbout.split('},{')
        for k in range(len(pbout)):
            pbout[k]=re.sub('\\\\"','',pbout[k])
            pbout[k]=re.sub('\\\\\\\\u0026','&',pbout[k])
            pbout[k]=pbout[k].split(',')
            temp=[]
            for subentry in pbout[k]:
                temprep=subentry.split(':',1)
                if len(temprep)>1:
                    temp.append(temprep[1].rstrip())
                else:
                    temp[-1]=temp[-1]+','+subentry.rstrip()
            pbout[k]=temp
        outstring=''
        htmlstring=''
        totalinterns=0
        last_updated=''
        for k in range(len(pbout)):
            valid=False
            totalinterns=totalinterns+int(pbout[k][1])
            last_updated=pbout[k][-4]
            if(len(branchfilter)>1 and len(pbout[k][-3].strip())>1):
                count=len([*re.finditer('any',pbout[k][-3],re.IGNORECASE)])-len([*re.finditer('anya',pbout[k][-3],re.IGNORECASE)])-len([*re.finditer('anyb',pbout[k][-3],re.IGNORECASE)])-len([*re.finditer('anyc',pbout[k][-3],re.IGNORECASE)])
                if(re.search(branchfilter,pbout[k][-3],re.IGNORECASE)):
                    valid=True
                elif(count>0):
                    valid=True
                elif(re.search(f'any{branchfilter}',pbout[k][-3],re.IGNORECASE)):
                    valid=True
            else:
                valid=True
            if(valid and not ignore_details):
                htmlstring=htmlstring+f'<li>{k+1}. <span style="color: #337dff">ProjectBrief-</span> {pbout[k][4]}<br> <span style="color: #72ff72">Eligibility-</span>{pbout[k][-3]}<br> <span style="color: #ff1a1a">Req. Interns-</span>{pbout[k][1]}<br><a href={uri} target="_blank" style="color:orange;">View Details</a><br><br></li>'
                outstring=outstring+f'\t{k+1}. {bcolors.OKBLUE}ProjectBrief-{bcolors.ENDC} {pbout[k][4]}\n\t {bcolors.OKGREEN}Eligibility-{bcolors.ENDC}{pbout[k][-3]}\n\t {bcolors.FAIL}Req. Interns-{bcolors.ENDC}{pbout[k][1]}\n'
        outstring=f'\033[AProject List-{bcolors.INFOYELLOW}{fetchlist[i][j][1]}{bcolors.ENDC} | {bcolors.OKBLUE}Stirpend(FD)-{bcolors.ENDC}{fetchlist[i][j][-5]} | {bcolors.OKBLUE}Stirpend(HD)-{bcolors.ENDC}{fetchlist[i][j][-3]} | {bcolors.OKBLUE}Scholarship-{bcolors.ENDC}{fetchlist[i][j][-4]} | {bcolors.INFOYELLOW}Eligibility-{bcolors.ENDC}{fetchlist[i][j][-6]} | {bcolors.FAIL}Total Interns-{bcolors.ENDC}{totalinterns}\n'+outstring
        htmlstring=f'Project List-<span style="color: #d76363">{fetchlist[i][j][1]}</span> | <span style="color: #337dff">Stirpend(FD)-</span>{fetchlist[i][j][-5]} | <span style="color: #337dff">Stirpend(HD)-</span>{fetchlist[i][j][-3]} | <span style="color: #337dff">Scholarship-</span>{fetchlist[i][j][-4]}<br>'+htmlstring+'<br>'
        print(link(uri,outstring))
        if(not ignore_details):
            file_html.write(f'''<h2 style="color:#e8e6e3;">{htmlstring}</h2></ul>''')
            file_html.write('''</div>''')
        else:
            if(fetchlist[i][j][1]!=projectlist):
                set_color='red'
            else:
                set_color='blue'
            file_html.write(f'''<td><span style="color: {set_color}">{fetchlist[i][j][1]}</span></td>
            <td>{last_updated}</td>
            <td>{fetchlist[i][j][-6]}</td>
            <td><span style="color: lime">{totalinterns}</span></td>
            <td><span style="color: #337dff">{fetchlist[i][j][-5]}</span></td>
            <td><a href={uri} target="_blank" style="color:orange;">View Details</a></td>
            </tr>''')
if(ignore_details):
    file_html.write('''</table>''')
file_html.write('''</body>
</html>''')
file_html.close()
f.close()
print("Program executed Successfuly")

