from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class AuctionListing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField()
    start_bid = models.DecimalField(max_digits=5, decimal_places=2)
    category = models.CharField(max_length=64, null=True, blank=True)
    image_url = models.ImageField(upload_to='', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="auction")
    active = models.BooleanField(default="True")

    def __str__(self):
        return f"{self.id}: Created by {self.title}"

class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bid")
    auct_list = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)
    bid_price = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.id}: {self.user} - {self.auct_list}: {self.bid_price}"

class Watchlist(models.Model):
    added = models.ManyToManyField(User, related_name="watchlist")
    auction = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="watchlist")

    def __str__(self):
        return f"{self.id}: {self.auction.title}"


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comment")
    auct_list = models.ForeignKey(AuctionListing, on_delete=models.CASCADE)
    comment = models.TextField()

    def __str__(self):
        return f"{self.id}: {self.user} - {self.comment}"
