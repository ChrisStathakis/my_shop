from django.db import models


class TranscationsQueryset(models.QuerySet):

    def is_active(self):
        return self.filter(active=True)


class BillCategoryManager(models.Manager):

    def get_queryset(self):
        return TranscationsQueryset(self.model, using=self._db)


class PersonManager(models.Manager):

    def get_queryset(self):
        return TranscationsQueryset(self.model, using=self._db)


class ExpenseCategoryManager(models.Manager):

    def get_queryset(self):
        return TranscationsQueryset(self.model, using=self._db)


class OccupationManager(models.Manager):

    def get_queryset(self):
        return TranscationsQueryset(self.model, using=self._db)