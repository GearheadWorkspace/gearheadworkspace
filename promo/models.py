from django.db import models


class Subscriber(models.Model):
	email = models.CharField(max_length=200, primary_key=True)
