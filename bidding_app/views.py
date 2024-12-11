from django.shortcuts import render
from bidding_app.models import *
from django.contrib.auth.models import User

POINTS = 2000
MAXBID = 1000
MINBIDS = 8
# Create your views here.

def welcome(request):
    context = dict()
    the_user = request.user
    if the_user.username == 'hardeepjohar' or the_user.username == 'admin':
        context = dict()
        return render(request,"admin_page.html",context)
    else:
        context=dict()
        bidding_user = BiddingUser.objects.get(user=the_user)
        context['bidding_user'] = bidding_user

        return render(request,"user_welcome.html",context)


def create_user(roster_record):
    from django.contrib.auth.models import User

    roster_data = roster_record.split(',')
    if roster_data[0] == "Uni":
        return None
    username = roster_data[0]
    #Check if user already exists
    if User.objects.filter(username=username).exists():
        return None

    email = roster_data[5]
    fname=roster_data[2]
    lname=roster_data[4]
    N=8
    import random,string
    new_password = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(N))
    from django.contrib.auth.models import User
    new_user = User.objects.create_user(username,email,new_password)
    new_user.first_name=fname
    new_user.last_name=lname
    new_user.save()
    new_bidding_user = BiddingUser(user=new_user,password=new_password,email=email)
    new_bidding_user.save()
    return None

def admin_actions(request):
    the_user = request.user
    print(the_user.username)
    if not the_user.username == "hardeepjohar":
        context = dict()
        context["message"] = "Unauthorized action!"
        return render(request,"user_welcome.html",context)
    try:
        request.GET['projects']
        file = request.GET['fname']
        update_projects(file)
        return render(request,"admin_page.html")
    except:
        pass

    try:
        request.GET['users']
        file = request.GET['fname']
        create_all_users(file)
        return render(request, "admin_page.html")
    except:
        pass

    try:
        request.GET['write_users']
        all_users = BiddingUser.objects.all()
        file = request.GET['fname']
        with open('static/'+file,'w') as f:
            for u in all_users:
                f.write(u.user.username + ',' + u.password + ',' + u.email +'\n')
        return render(request, "admin_page.html")
    except:
        pass

    try:
        request.GET["write_bids"]
        all_bids = Bids.objects.all()
        file= request.GET['fname']
        with open('static/'+file,'w') as f:
            for b in all_bids:
                if b.bid_amt <=0:
                    continue
                f.write(b.bidding_user.user.username + ',' + b.project + ',' + str(b.bid_amt) + '\n')
        return render(request, "admin_page.html")
    except:
        pass
    return render(request,"admin_page.html")

def make_bids(request):
    #extend cols so that it is a tuple (project,bid_value)
    #use this value on the bid_page
    user=request.user
    b_user=BiddingUser.objects.get(user=user)
    c_bids = Bids.objects.filter(bidding_user=b_user)
    bids = dict()
    for bid in c_bids:
        bids[bid.project] = bid.bid_amt
    all_projects = Project.objects.all()
    project_list = list()
    total_bid = 0
    for p in all_projects:
        pid = p.project_id
        bid_amt = bids.get(pid,0)
        total_bid += bid_amt
        project_list.append((p,bid_amt))
    n = len(project_list)
    col_len = n//3+1
    cols = [list(),list(),list()]
    print(col_len,n)
    cols[0] = project_list[:col_len]
    cols[1] = project_list[col_len:2*col_len]
    cols[2] = project_list[2*col_len:]
    context=dict()
    context['c1'] = cols[0]
    context['c2'] = cols[1]
    context['c3'] = cols[2]
    context['points'] = POINTS - total_bid
    context['minbids'] = MINBIDS
    context['maxbid'] = MAXBID
    return render(request,"bid_page.html",context)

def do_alloc(request):
    import datetime
    now = datetime.datetime.now()
    logfile = "static/log"
    f = open(logfile,"a+")
    user=request.user
    b_user = BiddingUser.objects.get(user=user)
    #INSERT CHECK HERE TO CATCH NON-LOGGEDIN USERS
    projects = Project.objects.all()
    #Server side verification of bids
    all_bids = list()
    count = 0
    for p in projects:
        bid = request.GET[p.project_id]
        try:
            bid = int(bid)
        except:
            bid = 0
        if bid > MAXBID:
            f.write("VIOLATION: " + str(now) + " " + str(user) + " " + p.project_id + " " + str(bid) + " "  + "\n")
        if bid>0:
            all_bids+=(p.project_id,bid)
            count += 1
    if count < MINBIDS:
        f.write("VIOLATION: " + str(now) + " " + str(user) + " " + "COUNT" + " " + str(count) + "\n")
    output = "USER: " +  str(now) + " " + str(user)
    output += " " + str(all_bids) + "\n"
    f.write(output)

    f.close()
    for p in projects:
        bid = request.GET[p.project_id]
        try:
            bid=int(bid)
        except:
            bid=0
        #all_bids.append((p.project_id,bid))


        try:
            bid_obj = Bids.objects.get(bidding_user=b_user,project=p.project_id)
            bid_obj.bid_amt = bid
        except:
            if bid == 0:
                continue
            bid_obj = Bids(bidding_user=b_user,project=p.project_id,bid_amt=bid)

        bid_obj.save()


    return render(request,'user_welcome.html')

def see_bids(request):
    return render(request,"see_bids.html")

def create_all_users(file):
    roster_file = "static/" + file
    with open(roster_file,'r') as f:
        for line in f:
            create_user(line)

def update_projects(file):

    project_file = "static/" + file

    with open(project_file,'r') as f:
        for line in f:
            #project_data = line.strip().split('\t')
            project_data = line.strip()
            update_project(project_data)

def update_project(project_data):
    #pid = project_data[0]
    pid = project_data
    if pid == "PROJECT ID":
        return None
    print("writing ",pid)

    try:
        p_obj = Project.objects.get(project_id=pid)
        p_obj.project_description = "None"
        p_obj.project_objective = "None"
        p_obj.project_deliverables = "None"

        p_obj.project_skills = "None"
        p_obj.project_notes = "None"
        """
        p_obj.project_description = project_data[1]
        p_obj.project_objective = project_data[2]
        p_obj.project_deliverables = project_data[3]

        p_obj.project_skills = project_data[4]
        p_obj.project_notes = project_data[5]
        """
        p_obj.save()
    except:
        p_obj = Project.objects.create(project_id=pid)
        p_obj.project_description = "None"
        p_obj.project_objective = "None"
        p_obj.project_deliverables = "None"

        p_obj.project_skills = "None"
        p_obj.project_notes = "None"

        """
        p_obj.project_description = project_data[1]
        p_obj.project_objective = project_data[2]
        p_obj.project_deliverables = project_data[3]

        p_obj.project_skills = project_data[4]
        p_obj.project_notes = project_data[5]
        """
        print("Got to the point where a project is saved")
        p_obj.save()

def help(request):
    return render(request,"help.html")