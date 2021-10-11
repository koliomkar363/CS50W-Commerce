from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Categories(models.Model):
    category = models.CharField(max_length=64)

    def __str__(self):
        return f'{self.category}'


class Listing(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='listing_user'
    )
    title = models.CharField(max_length=64)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    img_url = models.URLField()
    category = models.ForeignKey(
        Categories,
        on_delete=models.CASCADE,
        related_name='listing_category'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} posted {self.title} at {self.created_at}"


class Watchlist(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="watchlist_user"
    )
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name="watchlist_listing"
    )


class Bid(models.Model):
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='bid_listing'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='highest_bidder'
    )
    bids = models.DecimalField(max_digits=8, decimal_places=2)
    winner = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} placed a bid of ${self.bids} on {self.listing}"


class Comment(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="user_comment"
    )
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name="listing_comment"
    )
    comment = models.TextField()

    def __str__(self):
        return f"{self.user} commented {self.comment} on {self.listing}"
