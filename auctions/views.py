from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required

from .models import User, Categories, Listing, Watchlist, Bid, Comment
from .forms import CreateListingForm, AddCommentForm


def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.filter(active=True)
    })


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


@login_required
def create(request):
    if request.method == "POST":
        # Populate the form
        form = CreateListingForm(request.POST)

        if form.is_valid():
            user = request.user
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            price = form.cleaned_data["bid"]

            # Check if an image url is provided
            if form.cleaned_data["image_url"]:
                img_url = form.cleaned_data["image_url"]
            else:
                img_url = "https://external-content.duckduckgo.com/iu/?u=http%3A%2F%2Ffremontgurdwara.org%2Fwp-content%2Fuploads%2F2020%2F06%2Fno-image-icon-2.png&f=1&nofb=1"

            category = Categories.objects.get(pk=request.POST["category"])

            # Insert the listing's data in the Listing Table
            Listing.objects.create(
                user=user,
                title=title,
                description=description,
                price=price,
                img_url=img_url,
                category=category
            )

        return redirect("index")

    return render(request, "auctions/create.html", {
        "form": CreateListingForm(),
        "categories": Categories.objects.all()
    })


@login_required
def listing(request, listing_id):
    user = request.user
    listing = Listing.objects.get(pk=listing_id)
    starting_price = listing.price
    status = ""
    count = Bid.objects.filter(listing=listing_id).count()

    if count > 0:
        latest = Bid.objects.filter(listing=listing_id).latest('bids')
        highest_bid = latest.bids
        text = f"{count} bid(s) so far."
    else:
        latest = ""
        highest_bid = 0
        text = "0 bid(s) so far."

    if request.method == "POST":
        placed_bid = float(request.POST["bid"])

        if placed_bid >= starting_price and placed_bid > highest_bid:
            Bid.objects.create(
                user=User.objects.get(id=user.id),
                listing=listing,
                bids=placed_bid
            )

            latest = Bid.objects.filter(listing=listing_id).latest('bids')
            count += 1
            text = f"{count} bid(s) so far."
            status = "success"
        else:
            status = "failed"

    watchlist = Watchlist.objects.filter(user=user, listing=listing_id)
    comments = Comment.objects.filter(listing=listing_id)

    return render(request, "auctions/listing.html", {
        "user": user,
        "listing": listing,
        "form": AddCommentForm(),
        "watchlist": watchlist,
        "comments": comments,
        "status": status,
        "latest": latest,
        "text": text
    })


@login_required
def my_listing(request):
    return render(request, "auctions/my_listing.html", {
        "listings": Listing.objects.filter(user=request.user.id)
    })


def categories(request):
    return render(request, "auctions/categories.html", {
        "categories": Categories.objects.all()
    })


def filter(request, category_id):
    category = Categories.objects.get(pk=category_id)
    listings = Listing.objects.filter(category=category_id, active=True)

    return render(request, "auctions/filter.html", {
        "category": category,
        "listings": listings
    })


@login_required
def watchlist(request):
    user = request.user
    watchlists = Watchlist.objects.filter(user=user.id)

    # Returns the User's Watchlist
    return render(request, "auctions/watchlist.html", {
        "watchlists": watchlists
    })


@login_required
def update(request, listing_id):
    user = request.user
    watchlist = Watchlist.objects.filter(user=user, listing=listing_id)

    # Remove listing from the Watchlist
    if watchlist:
        watchlist.delete()

    # Add listing to the Watchlist
    else:
        Watchlist.objects.create(
            user=User.objects.get(id=user.id),
            listing=Listing.objects.get(id=listing_id)
        )

    return redirect("listing", listing_id=listing_id)


@login_required
def comment(request, listing_id):
    user = request.user

    if request.method == "POST":
        # Populate the form
        form = AddCommentForm(request.POST)

        if form.is_valid():
            comment = form.cleaned_data["comment"]

            # Insert the comment in the Comments Table
            Comment.objects.create(
                user=User.objects.get(id=user.id),
                listing=Listing.objects.get(id=listing_id),
                comment=comment
            )

    return redirect("listing", listing_id=listing_id)


@login_required
def my_bids(request):
    user = request.user
    bids = Bid.objects.filter(user=user.id)

    # Returns User's bids
    return render(request, "auctions/my_bids.html", {
        "bids": bids
    })


@login_required
def close(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    count = Bid.objects.filter(listing=listing_id).count()

    if count > 0:
        bids = Bid.objects.filter(listing=listing_id).latest('bids')

        # Update winner = True for the highest bidder
        bids.winner = True
        bids.save(update_fields=['winner'])

    # To close listing, update the active field
    listing.active = False
    listing.save(update_fields=['active'])

    return redirect("listing", listing_id=listing_id)
