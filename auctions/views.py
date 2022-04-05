from django.contrib.auth import authenticate, login, logout, get_user_model
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import *
from .forms import *
User=get_user_model()

def index(request):
    # Get all Auction Items
    auct_lists = AuctionListing.objects.filter(active=True)
    if auct_lists:
        return render(request, "auctions/index.html", {"auct_lists": auct_lists})

    return render(request, "auctions/index.html", {})


def login_view(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def closed(request):
    # Get closed Auction Items
    auct_lists = AuctionListing.objects.filter(active=False)
    if auct_lists:
        return render(request, "auctions/closed.html", {"auct_lists": auct_lists})

    return render(request, "auctions/closed.html", {})

def auct_list(request, auct_list_id):
    # OBJ
    auct_list = AuctionListing.objects.get(id=auct_list_id)
    comments = Comment.objects.filter(auct_list=auct_list)
    bids = Bid.objects.filter(auct_list=auct_list)
    
    # Auction Status
    author = auct_list.user.username
    status = {
        'winner_name': None,
        'auct_status': auct_list.active,
        'bids_count': bids.count()
    }
    # FORMS
    bid_form = CreateBid()
    comment_form = CreateComment()

    # Get current bid if exists
    if bids:
        bids_list = []
        for bid in bids:
            bids_list.append(bid.bid_price)
        current_bid = max(bids_list)
        current_bid_obj = Bid.objects.get(bid_price=current_bid)
    else:
        current_bid = auct_list.start_bid
        current_bid_obj = {"user": request.user.username, "bid_price": current_bid}



    #if user == author close auction, which makes the highest bidder winner and deactivate auction list
    if auct_list.active == False:
        bid = Bid.objects.get(auct_list=auct_list, bid_price=current_bid)
        if bid:
            name = bid.user.username
            status = {
                'winner_name': name,
                'auct_status': auct_list.active,
                'bids_count': bids.count(),
            }


    if request.method == "POST":
        comment_form = CreateComment(request.POST)

        #Create Comments
        if comment_form.is_valid():
            if request.user.is_authenticated:
                user = User.objects.get(username=request.user.username)
                Comment(user=user, auct_list=auct_list, comment=request.POST['comment']).save()

        # Create Watchlist and add User to it, or if it already exists only add the user to it
        if "watchlist" in request.POST:
            if request.user.is_authenticated:
                user = User.objects.get(username=request.user.username)
                if request.POST['watchlist'] == "1":
                    watchlist = Watchlist.objects.filter(auction=auct_list)
                    if not watchlist:
                        watchlist = Watchlist.objects.create(auction=auct_list)
                        watchlist.added.add(user)
                    if watchlist and not user.watchlist.filter(auction=auct_list).exists():
                        watchlist = Watchlist.objects.get(auction=auct_list)
                        watchlist.added.add(user)
                #  Remove User from watchlist if remove from watchlist 
                else:
                    if user.watchlist.filter(auction=auct_list).exists():
                        watchlist = Watchlist.objects.get(auction=auct_list)
                        watchlist.added.remove(user)

    #Check if the user is inside the watchlist, and display: add to watchlist or remove from watchlist
    if request.user.is_authenticated:
        user = User.objects.get(username=request.user.username)
        if user.watchlist.filter(auction=auct_list).exists():
            watchlist = Watchlist.objects.get(auction=auct_list)
            return render(request, "auctions/auct_list.html", {"auct_list": auct_list, "author": author, "current_bid_obj": current_bid_obj, "bid_form": CreateBid(), "comment_form": CreateComment(), "comments": comments, "status": status, "watchlist": watchlist})

    return render(request, "auctions/auct_list.html", {"auct_list": auct_list, "author": author, "current_bid_obj": current_bid_obj, "bid_form": CreateBid(), "comment_form": CreateComment(), "comments": comments, "status": status})


def bid(request, auct_list_id):
    if request.method == "POST":
        bid_form = CreateBid()
        if request.user.is_authenticated:
            # Change bid if corresponds to verification, or display an error if not
            user = User.objects.get(username=request.user.username)
            auct_list = AuctionListing.objects.get(id=auct_list_id)
            bid_value = float(request.POST['bid_value'])
            start_bid = auct_list.start_bid
            bids = Bid.objects.filter(auct_list=auct_list)
            bids_list = []
            if bids:
                for bid in bids:
                    bids_list.append(bid.bid_price)
                current_bid = max(bids_list)
            else:
                current_bid = start_bid
            if bid_value > start_bid and bid_value > current_bid:
                m = Bid(user=user, auct_list=auct_list, bid_price=bid_value)
                m.save()
            else:
                messages.error(request, 'Bid value must be greater than current bid.')

    return redirect('auct_list', auct_list_id=auct_list_id)


def finish(request, auct_list_id):
    # Finishes the Auction Item
    auct_list = AuctionListing.objects.get(id=auct_list_id)
    auct_list.active = False
    auct_list.save()
    return redirect('auct_list', auct_list_id=auct_list_id)

@login_required(login_url='login')
def create(request):
    # Create an Auction Item
    if request.method == "POST":
        user = User.objects.get(username=request.user.username)
        form = CreateListing(request.POST)
        if form.is_valid():
            title = request.POST['title']
            description = request.POST['description']
            start_bid = request.POST['start_bid']
            category = request.POST['category']
            image_url = request.POST['image_url']

            m = AuctionListing(title=title, description=description, start_bid=start_bid, category=category, image_url=image_url, user=user)
            m.save()
            return redirect('index')
    else:
        form = CreateListing()

    return render(request, "auctions/create.html", {"form": form})

def category(request):
    if request.method == "POST":
        if "category" in request.POST:
            category = request.POST['category']
            return redirect('category-result', category=category)
    return render(request, "auctions/category.html", {})

def categoryResult(request, category):
    # Get Auction Items filtered by category
    # If category == All returns all Auction Items
    if category == "All":
        auct_lists = AuctionListing.objects.all()
    else:
        auct_lists = AuctionListing.objects.filter(category=category)
    if auct_lists:
        return render(request, "auctions/category_result.html", {"auct_lists": auct_lists})
    return render(request, "auctions/category_result.html", {})

@login_required(login_url='login')
def watchlist(request):
    # Get Auction Items if user is in the Watchlist
    user = User.objects.get(username=request.user.username)
    watchlists = Watchlist.objects.filter(added=user)
    if watchlists:
        auct_lists = []
        for watchlist in watchlists:
            auct_lists.append(watchlist.auction)
        return render(request, "auctions/watchlist.html", {"auct_lists": auct_lists})

    return render(request, "auctions/watchlist.html", {})
